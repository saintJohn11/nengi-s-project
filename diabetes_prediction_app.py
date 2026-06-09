import streamlit as st
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Diabetes Risk Assessment System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CREATE HOSPITAL BACKGROUND IMAGE =====================
@st.cache_resource
def create_hospital_background():
    """Create a professional hospital-themed background image"""
    # Create a light blue-gray background
    img = Image.new('RGB', (1920, 1080), color='#f0f4f8')
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Add medical-themed pattern
    # Subtle diagonal lines
    for i in range(0, 1920, 80):
        draw.line([(i, 0), (i+500, 1080)], fill=(200, 220, 240, 30), width=2)
    
    # Add medical crosses pattern (subtle)
    for y in range(0, 1080, 200):
        for x in range(0, 1920, 300):
            # Draw subtle plus signs
            draw.line([(x, y-20), (x, y+20)], fill=(0, 102, 204, 15), width=3)
            draw.line([(x-20, y), (x+20, y)], fill=(0, 102, 204, 15), width=3)
    
    # Add gradient-like effect with circles
    for i in range(5):
        x = i * 400
        y = 1080 + i * 100
        draw.ellipse([x-100, y-100, x+100, y+100], fill=(173, 216, 230, 10))
    
    # Save to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return img_base64

# Get background image
bg_image = create_hospital_background()

# Custom CSS for medical-professional styling with background
st.markdown(f"""
<style>
    * {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/png;base64,{bg_image}");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    [data-testid="stSidebar"] {{
        background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }}
    
    .main {{
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }}
    
    .metric-card {{
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid #0066cc;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.5);
    }}
    
    .warning-box {{
        background: rgba(255, 243, 205, 0.95);
        border-left: 5px solid #ff9800;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    
    .risk-high {{
        background: rgba(255, 235, 238, 0.98);
        border-left: 5px solid #d32f2f;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(211, 47, 47, 0.15);
    }}
    
    .risk-moderate {{
        background: rgba(255, 243, 224, 0.98);
        border-left: 5px solid #f57c00;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(245, 124, 0, 0.15);
    }}
    
    .risk-low {{
        background: rgba(232, 245, 233, 0.98);
        border-left: 5px solid #388e3c;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(56, 142, 60, 0.15);
    }}
    
    .header-title {{
        color: #0a1f3d;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 10px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }}
    
    .section-header {{
        color: #0066cc;
        font-size: 20px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 15px;
        border-bottom: 3px solid #0066cc;
        padding-bottom: 12px;
        background: linear-gradient(90deg, rgba(0,102,204,0.05), transparent);
        padding-left: 12px;
        border-radius: 5px;
    }}
    
    .model-card {{
        background: white;
        border: 2px solid #0066cc;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    
    .model-card:hover {{
        box-shadow: 0 6px 16px rgba(0,102,204,0.2);
        border-color: #0052a3;
        background: #f0f6ff;
    }}
    
    .input-label {{
        font-weight: 600;
        color: #0a1f3d;
        margin-bottom: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# ===================== LOAD MODELS =====================
@st.cache_resource
def load_models():
    """Load pre-trained models"""
    try:
        with open('trained_models/random_forest_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        with open('trained_models/xgboost_model.pkl', 'rb') as f:
            xgb_model = pickle.load(f)
        with open('trained_models/logistic_regression_model.pkl', 'rb') as f:
            lr_model = pickle.load(f)
        with open('trained_models/robust_scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        return rf_model, xgb_model, lr_model, scaler
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None, None, None

# ===================== HELPER FUNCTIONS =====================
def interpret_risk(probability):
    """Interpret diabetes risk level"""
    if probability < 0.3:
        return "LOW", "🟢"
    elif probability < 0.7:
        return "MODERATE", "🟡"
    else:
        return "HIGH", "🔴"

def get_risk_recommendations(probability, age, glucose, bmi):
    """Provide medical recommendations based on risk factors"""
    recommendations = []
    
    if probability > 0.7:
        recommendations.append("• Immediate medical consultation recommended")
        recommendations.append("• Consider HbA1c and glucose tolerance testing")
    elif probability > 0.3:
        recommendations.append("• Schedule follow-up glucose testing in 3-6 months")
        recommendations.append("• Monitor lifestyle factors and diet")
    else:
        recommendations.append("• Continue regular health check-ups")
        recommendations.append("• Maintain healthy lifestyle and diet")
    
    if glucose > 126:
        recommendations.append("• Fasting glucose level is elevated - medical evaluation needed")
    elif glucose > 100:
        recommendations.append("• Fasting glucose is borderline - monitor closely")
    
    if bmi > 30:
        recommendations.append("• BMI indicates obesity - consider weight management program")
    elif bmi > 25:
        recommendations.append("• BMI is overweight range - lifestyle modifications recommended")
    
    if age > 60:
        recommendations.append("• Increased age is a risk factor - regular screening important")
    
    return recommendations

def format_patient_summary(patient_data):
    """Create a summary table for patient data"""
    summary_df = pd.DataFrame({
        'Parameter': list(patient_data.keys()),
        'Value': list(patient_data.values())
    })
    return summary_df

# ===================== MAIN APP =====================
# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown('<div class="header-title">🏥 Diabetes Risk Assessment System</div>', unsafe_allow_html=True)
    st.markdown("*Clinical Decision Support Tool for Healthcare Professionals*")
with col2:
    st.metric("System Status", "✓ Online", delta="Ready")

st.divider()

# Load models
rf_model, xgb_model, lr_model, scaler = load_models()

if rf_model is None:
    st.error("⚠️ Unable to load models. Please check the trained_models directory.")
    st.stop()

# ===================== SIDEBAR - MODEL & SETTINGS =====================
with st.sidebar:
    st.markdown("### ⚙️ System Settings")
    
    st.markdown("#### 📊 Select Prediction Models")
    st.markdown("*Choose one or more models for prediction*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_rf = st.checkbox("🌲 Random Forest", value=True, help="Ensemble method - High accuracy")
    
    with col2:
        use_xgb = st.checkbox("⚡ XGBoost", value=True, help="Gradient boosting - Very fast")
    
    with col3:
        use_lr = st.checkbox("📈 Logistic Regression", value=True, help="Linear model - Interpretable")
    
    # Ensure at least one model is selected
    if not (use_rf or use_xgb or use_lr):
        st.warning("⚠️ Please select at least one model!")
        use_rf = True
    
    selected_models = []
    if use_rf:
        selected_models.append("Random Forest")
    if use_xgb:
        selected_models.append("XGBoost")
    if use_lr:
        selected_models.append("Logistic Regression")
    
    st.divider()
    st.markdown("### 📋 Model Details")
    
    if use_rf:
        with st.expander("🌲 Random Forest"):
            st.markdown("""
            - **Type**: Ensemble (voting)
            - **Strength**: High accuracy, handles non-linear patterns
            - **Use**: Primary diagnosis recommendation
            - **Speed**: ~50ms per prediction
            """)
    
    if use_xgb:
        with st.expander("⚡ XGBoost"):
            st.markdown("""
            - **Type**: Gradient boosting
            - **Strength**: Fast, excellent for complex patterns
            - **Use**: Validation & cross-check
            - **Speed**: ~20ms per prediction
            """)
    
    if use_lr:
        with st.expander("📈 Logistic Regression"):
            st.markdown("""
            - **Type**: Linear classifier
            - **Strength**: Interpretable, stable baseline
            - **Use**: Comparison & baseline
            - **Speed**: ~5ms per prediction
            """)
    
    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Disclaimer**: This tool is for clinical decision support only. 
    Always validate results with proper medical diagnosis.
    """)
    
    st.markdown("---")
    st.markdown("**Hospital Diabetes Assessment System v1.0**")
    st.markdown("*For Healthcare Professionals Only*")

# ===================== MAIN CONTENT =====================
# Patient Information Section
st.markdown('<div class="section-header">📝 Patient Information</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    age = st.number_input(
        "Age (years)",
        min_value=1,
        max_value=120,
        value=45,
        step=1,
        help="Patient age in years"
    )

with col2:
    pregnancy = st.number_input(
        "Pregnancies",
        min_value=0,
        max_value=20,
        value=0,
        step=1,
        help="For female patients"
    )

with col3:
    glucose = st.number_input(
        "Glucose (mg/dL)",
        min_value=0,
        max_value=400,
        value=120,
        step=1,
        help="Fasting blood glucose level"
    )

with col4:
    blood_pressure = st.number_input(
        "Blood Pressure (mmHg)",
        min_value=0,
        max_value=250,
        value=70,
        step=1,
        help="Diastolic blood pressure"
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    skin_thickness = st.number_input(
        "Skin Thickness (mm)",
        min_value=0,
        max_value=100,
        value=20,
        step=1,
        help="Triceps skin fold thickness"
    )

with col2:
    insulin = st.number_input(
        "Insulin (µU/mL)",
        min_value=0,
        max_value=900,
        value=80,
        step=1,
        help="2-hour serum insulin"
    )

with col3:
    bmi = st.number_input(
        "BMI (kg/m²)",
        min_value=10.0,
        max_value=60.0,
        value=25.0,
        step=0.1,
        help="Body Mass Index"
    )

with col4:
    diabetes_pedigree = st.number_input(
        "Diabetes Pedigree Function",
        min_value=0.0,
        max_value=2.5,
        value=0.5,
        step=0.01,
        help="Family history of diabetes"
    )

# ===================== PREDICTION SECTION =====================
st.markdown('<div class="section-header">🔍 Risk Assessment & Analysis</div>', unsafe_allow_html=True)

if st.button("🔬 Analyze Diabetes Risk Using Selected Models", key="predict_btn", use_container_width=True):
    if not selected_models:
        st.error("Please select at least one model from the sidebar!")
    else:
        # Prepare input data
        input_data = np.array([[
            pregnancy,
            glucose,
            blood_pressure,
            skin_thickness,
            insulin,
            bmi,
            diabetes_pedigree,
            age
        ]])
        
        # Scale the input
        input_scaled = scaler.transform(input_data)
        
        # Get predictions from all selected models
        predictions = {}
        probabilities = {}
        
        if "Random Forest" in selected_models:
            predictions['Random Forest'] = rf_model.predict(input_scaled)[0]
            probabilities['Random Forest'] = rf_model.predict_proba(input_scaled)[0][1]
        
        if "XGBoost" in selected_models:
            predictions['XGBoost'] = xgb_model.predict(input_scaled)[0]
            probabilities['XGBoost'] = xgb_model.predict_proba(input_scaled)[0][1]
        
        if "Logistic Regression" in selected_models:
            predictions['Logistic Regression'] = lr_model.predict(input_scaled)[0]
            probabilities['Logistic Regression'] = lr_model.predict_proba(input_scaled)[0][1]
        
        # Calculate ensemble probability (average of selected models)
        ensemble_prob = np.mean(list(probabilities.values()))
        risk_level, risk_emoji = interpret_risk(ensemble_prob)
        
        # Display main prediction result
        st.markdown('<div class="section-header">📊 Primary Risk Assessment (Ensemble)</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            if risk_level == "HIGH":
                st.markdown(f'<div class="risk-high"><h3>{risk_emoji} HIGH RISK</h3><p style="font-size: 32px; font-weight: bold; margin: 15px 0;">{ensemble_prob*100:.1f}%</p><p>Average diabetes prediction probability</p></div>', unsafe_allow_html=True)
            elif risk_level == "MODERATE":
                st.markdown(f'<div class="risk-moderate"><h3>{risk_emoji} MODERATE RISK</h3><p style="font-size: 32px; font-weight: bold; margin: 15px 0;">{ensemble_prob*100:.1f}%</p><p>Average diabetes prediction probability</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="risk-low"><h3>{risk_emoji} LOW RISK</h3><p style="font-size: 32px; font-weight: bold; margin: 15px 0;">{ensemble_prob*100:.1f}%</p><p>Average diabetes prediction probability</p></div>', unsafe_allow_html=True)
        
        with col2:
            st.metric("Models Used", len(selected_models))
            st.metric("Ensemble Result", "✓ Yes")
        
        with col3:
            st.metric("Assessment Date", datetime.now().strftime("%Y-%m-%d"))
            st.metric("Assessment Time", datetime.now().strftime("%H:%M:%S"))
        
        st.divider()
        
        # Individual Model Results
        if len(selected_models) > 1:
            st.markdown('<div class="section-header">📈 Individual Model Predictions</div>', unsafe_allow_html=True)
            
            # Create columns for each selected model
            model_cols = st.columns(len(selected_models))
            
            for idx, (model_name, col) in enumerate(zip(selected_models, model_cols)):
                with col:
                    prob = probabilities[model_name]
                    risk = interpret_risk(prob)[0]
                    emoji = interpret_risk(prob)[1]
                    
                    st.metric(
                        f"{emoji} {model_name}",
                        f"{prob*100:.1f}%",
                        delta=risk
                    )
        
        st.divider()
        
        # Risk Factors Summary
        st.markdown('<div class="section-header">⚠️ Patient Risk Factors Summary</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if glucose > 126:
                glucose_status = "🔴 Abnormal"
            elif glucose > 100:
                glucose_status = "🟡 Borderline"
            else:
                glucose_status = "🟢 Normal"
            st.metric("Glucose Level", f"{glucose} mg/dL", glucose_status)
        
        with col2:
            if bmi > 30:
                bmi_status = "🔴 Obese"
            elif bmi > 25:
                bmi_status = "🟡 Overweight"
            else:
                bmi_status = "🟢 Normal"
            st.metric("BMI Status", f"{bmi:.1f} kg/m²", bmi_status)
        
        with col3:
            if age > 60:
                age_status = "🔴 High Risk Age"
            elif age > 45:
                age_status = "🟡 Moderate Age"
            else:
                age_status = "🟢 Lower Age"
            st.metric("Age Group", f"{age} years", age_status)
        
        st.divider()
        
        # Clinical Recommendations
        st.markdown('<div class="section-header">💊 Clinical Recommendations</div>', unsafe_allow_html=True)
        recommendations = get_risk_recommendations(ensemble_prob, age, glucose, bmi)
        
        rec_col1, rec_col2 = st.columns([1, 3])
        
        with rec_col1:
            st.markdown("**Suggested Actions:**")
        
        with rec_col2:
            for rec in recommendations:
                st.markdown(f"• {rec}")
        
        st.divider()
        
        # Patient Data Summary
        st.markdown('<div class="section-header">📋 Patient Data Summary</div>', unsafe_allow_html=True)
        
        patient_data = {
            'Parameter': ['Age', 'Pregnancies', 'Glucose', 'Blood Pressure', 'Skin Thickness', 'Insulin', 'BMI', 'Diabetes Pedigree'],
            'Value': [f"{age} years", pregnancy, f"{glucose} mg/dL", f"{blood_pressure} mmHg", f"{skin_thickness} mm", f"{insulin} µU/mL", f"{bmi:.1f} kg/m²", f"{diabetes_pedigree:.3f}"],
            'Status': [age_status if 'age_status' in locals() else '✓', '✓', glucose_status if 'glucose_status' in locals() else '✓', '✓', '✓', '✓', bmi_status if 'bmi_status' in locals() else '✓', '✓']
        }
        
        summary_df = pd.DataFrame(patient_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Export option
        st.markdown('<div class="section-header">📥 Export & Report</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate comprehensive report
            models_used = ", ".join(selected_models)
            
            report_text = f"""
╔═══════════════════════════════════════════════════════════════╗
║         DIABETES RISK ASSESSMENT REPORT                       ║
╚═══════════════════════════════════════════════════════════════╝

📅 ASSESSMENT METADATA
{'─'*63}
Assessment Date:        {datetime.now().strftime('%Y-%m-%d')}
Assessment Time:        {datetime.now().strftime('%H:%M:%S')}
Models Used:            {models_used}
Number of Models:       {len(selected_models)}

👤 PATIENT INFORMATION
{'─'*63}
Age:                    {age} years
Pregnancies:            {pregnancy}
Glucose Level:          {glucose} mg/dL
Blood Pressure:         {blood_pressure} mmHg
Skin Thickness:         {skin_thickness} mm
Insulin Level:          {insulin} µU/mL
BMI:                    {bmi:.1f} kg/m²
Diabetes Pedigree:      {diabetes_pedigree:.3f}

⚠️ RISK ASSESSMENT RESULTS
{'─'*63}
Ensemble Risk Level:    {risk_level} {risk_emoji}
Ensemble Probability:   {ensemble_prob*100:.1f}%

INDIVIDUAL MODEL RESULTS:
"""
            
            for model_name, prob in probabilities.items():
                risk = interpret_risk(prob)[0]
                emoji = interpret_risk(prob)[1]
                report_text += f"\n{model_name:25} {prob*100:6.1f}%  ({risk})"
            
            report_text += f"""

📊 RISK FACTOR ANALYSIS
{'─'*63}
Glucose Status:         {glucose_status if 'glucose_status' in locals() else 'Normal'}
BMI Status:             {bmi_status if 'bmi_status' in locals() else 'Normal'}
Age Group:              {age_status if 'age_status' in locals() else 'Normal'}

💊 CLINICAL RECOMMENDATIONS
{'─'*63}
{chr(10).join(recommendations)}

⚕️ IMPORTANT DISCLAIMER
{'─'*63}
This assessment is for clinical decision support purposes only.

• NOT a replacement for professional medical diagnosis
• Always consult with qualified physicians
• Results must be validated with proper medical examination
• Consider additional testing (HbA1c, glucose tolerance test)
• Use as one tool among comprehensive clinical assessment

Hospital: [INSERT HOSPITAL NAME]
Department: Endocrinology / General Practice
Reviewed By: [INSERT DOCTOR NAME & SIGNATURE]

System: Hospital Diabetes Risk Assessment v1.0
{'═'*63}
"""
            
            st.download_button(
                label="📄 Download Comprehensive Report (TXT)",
                data=report_text,
                file_name=f"diabetes_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            # CSV export for records
            export_df = pd.DataFrame({
                'Assessment Date': [datetime.now().strftime('%Y-%m-%d')],
                'Assessment Time': [datetime.now().strftime('%H:%M:%S')],
                'Age': [age],
                'Glucose': [glucose],
                'BMI': [bmi],
                'Ensemble Risk': [f"{ensemble_prob*100:.1f}%"],
                'Risk Level': [risk_level],
                'Models Used': [models_used],
            })
            
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Assessment Data (CSV)",
                data=csv_data,
                file_name=f"diabetes_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

else:
    st.info("👆 Click 'Analyze Diabetes Risk Using Selected Models' button to assess the patient's diabetes risk based on the provided parameters.")

# Footer
st.divider()
st.markdown("""
---
<div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
    <p><strong>Diabetes Risk Assessment System v1.0</strong></p>
    <p>Clinical Decision Support Tool | For Healthcare Professionals Only</p>
    <p>⚕️ Always consult with qualified medical professionals for diagnosis and treatment</p>
</div>
""", unsafe_allow_html=True)
