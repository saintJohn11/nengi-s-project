# 🏥 Diabetes Risk Assessment System

**Clinical Decision Support Tool for Healthcare Professionals**

A professional-grade Streamlit application designed specifically for hospitals and healthcare facilities to assess diabetes risk in patients using machine learning models.

---

## 🎯 Features

### Core Functionality
- **Multi-Model Predictions**: Compare predictions from 3 different ML models:
  - Random Forest (high accuracy, robust)
  - XGBoost (fast, excellent pattern recognition)
  - Logistic Regression (interpretable baseline)
  
- **Comprehensive Patient Input**: 
  - Age, Pregnancies, Glucose levels
  - Blood Pressure, Skin Thickness, Insulin
  - BMI, Diabetes Pedigree Function
  
- **Risk Assessment with Clinical Interpretation**:
  - Clear risk level classification (LOW/MODERATE/HIGH)
  - Probability percentages
  - Color-coded visual indicators
  
- **Intelligent Recommendations**:
  - Automated clinical recommendations based on risk factors
  - Specific guidance for glucose, BMI, and age indicators
  - Medical action items for doctors

- **Professional Report Generation**:
  - Downloadable assessment reports (TXT format)
  - Complete patient data summary
  - Timestamp and model information
  - Clinical disclaimers

---

## 📋 Patient Data Parameters

| Parameter | Unit | Range | Description |
|-----------|------|-------|-------------|
| **Age** | Years | 1-120 | Patient age |
| **Pregnancies** | Count | 0-20 | Number of pregnancies (females) |
| **Glucose** | mg/dL | 0-400 | Fasting blood glucose level |
| **Blood Pressure** | mmHg | 0-250 | Diastolic blood pressure |
| **Skin Thickness** | mm | 0-100 | Triceps skin fold thickness |
| **Insulin** | µU/mL | 0-900 | 2-hour serum insulin |
| **BMI** | kg/m² | 10-60 | Body Mass Index |
| **Diabetes Pedigree** | Score | 0-2.5 | Family history factor |

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Prepare Model Files
Ensure the trained models are in a `trained_models` directory:
```
trained_models/
├── random_forest_model.pkl
├── xgboost_model.pkl
├── logistic_regression_model.pkl
└── robust_scaler.pkl
```

### Step 3: Run the Application
```bash
streamlit run diabetes_prediction_app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📦 Deployment Options

### Option 1: Streamlit Cloud (Recommended for Teams)
**Best for**: Healthcare team with cloud access

1. Push code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New app" → Select repository
4. Set main file path: `diabetes_prediction_app.py`
5. Deploy!

**Advantages**:
- Secure HTTPS connection (hospital requirement)
- User authentication support
- Easy team sharing
- No server management

---

### Option 2: Render (Easy Alternative)
**Best for**: Small hospital networks

1. Create account at [render.com](https://render.com)
2. Connect GitHub repository
3. Create new "Web Service"
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run diabetes_prediction_app.py --server.port=10000`
6. Set `STREAMLIT_SERVER_HEADLESS=true` in environment

---

### Option 3: Docker (Enterprise Deployment)
**Best for**: Large hospital systems with IT infrastructure

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY trained_models/ ./trained_models/
COPY diabetes_prediction_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "diabetes_prediction_app.py", "--server.port=8501"]
```

Build and run:
```bash
docker build -t diabetes-assessment:v1 .
docker run -p 8501:8501 diabetes-assessment:v1
```

---

### Option 4: Self-Hosted (On-Premises)
**Best for**: Hospital servers with strict data privacy requirements

1. **Linux Server Setup**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install python3-pip python3-venv
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install & Configure**:
   ```bash
   pip install -r requirements.txt
   
   # Create Streamlit config
   mkdir ~/.streamlit
   cat > ~/.streamlit/config.toml << EOF
   [server]
   port = 8501
   headless = true
   
   [logger]
   level = "info"
   EOF
   ```

3. **Setup Systemd Service** (`/etc/systemd/system/diabetes-app.service`):
   ```ini
   [Unit]
   Description=Diabetes Assessment Application
   After=network.target
   
   [Service]
   Type=simple
   User=streamlit
   WorkingDirectory=/opt/diabetes-app
   ExecStart=/opt/diabetes-app/venv/bin/streamlit run diabetes_prediction_app.py
   Restart=always
   RestartSec=10
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start Service**:
   ```bash
   sudo systemctl enable diabetes-app
   sudo systemctl start diabetes-app
   ```

---

## 🔒 Security & Compliance

### Data Privacy
- ✅ **No data storage**: Predictions are calculated in real-time, not stored
- ✅ **HIPAA-ready**: Deploy on secure hospital networks
- ✅ **On-premises option**: Keep data within hospital infrastructure
- ✅ **Audit logs**: Can be added for compliance tracking

### Recommended Security Measures
1. **Enable HTTPS**: Use reverse proxy (Nginx/Apache)
2. **Authentication**: Implement hospital SSO/Active Directory
3. **Access Control**: Restrict to authorized personnel only
4. **Encryption**: Use TLS/SSL for data in transit
5. **Regular Updates**: Keep dependencies current

### Example Nginx Reverse Proxy:
```nginx
server {
    listen 443 ssl http2;
    server_name diabetes-assessment.hospital.local;
    
    ssl_certificate /etc/ssl/certs/hospital.crt;
    ssl_certificate_key /etc/ssl/private/hospital.key;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 💡 How to Use (For Doctors)

### Step-by-Step Workflow:

1. **Enter Patient Data**
   - Fill in all patient parameters from medical records
   - Use valid ranges (system validates input)
   
2. **Select Prediction Model**
   - Sidebar offers 3 models
   - Recommended: Random Forest for best accuracy
   
3. **Click "Analyze Diabetes Risk"**
   - System processes data through selected model
   - Comparison view shows all 3 models
   
4. **Review Results**
   - Large color-coded risk indicator (🟢🟡🔴)
   - Probability percentage
   - Risk factors summary
   
5. **Read Clinical Recommendations**
   - Automated suggestions based on results
   - Factor-specific guidance (glucose, BMI, age)
   
6. **Download Report**
   - Generate printable/shareable assessment report
   - Include in patient medical record

---

## 🎨 UI/UX Design Elements

### Medical-Professional Aesthetic
- **Clean, minimal interface** - reduces cognitive load
- **Color-coded risk indicators** - instant visual understanding
- **Large, readable typography** - easy for clinical environment
- **Organized sections** - logical workflow for doctors
- **Professional styling** - suitable for hospital displays

### Visual Hierarchy
- Patient input → Risk assessment → Recommendations → Report
- Clear section breaks and visual guides
- Consistent spacing and alignment

---

## ⚠️ Clinical Disclaimer

```
This tool is a CLINICAL DECISION SUPPORT SYSTEM for healthcare 
professionals ONLY. It should not be used for:

- Standalone diagnosis (always consult qualified doctors)
- Treatment decisions without professional judgment
- Patient self-assessment or public use
- Medical decisions in critical situations

Always validate all results with:
- Proper medical examination
- Certified diabetes screening tests
- Consultation with endocrinologists or physicians
```

---

## 📊 Model Performance Reference

The models were trained on clinical diabetes data with the following characteristics:

| Model | Training Approach | Strengths | Use Case |
|-------|-------------------|-----------|----------|
| **Random Forest** | Ensemble voting | High accuracy, handles non-linearity | Primary diagnosis |
| **XGBoost** | Gradient boosting | Fast inference, excellent patterns | Secondary validation |
| **Logistic Regression** | Linear classification | Interpretable, baseline comparison | Quick assessment |

---

## 🔄 Model Scaling

The RobustScaler is applied to all inputs for consistent model performance:
- Handles outliers well
- Scales features to similar ranges
- Improves model robustness
- Already integrated in the app

---

## 📱 Browser Compatibility

- ✅ Chrome/Chromium (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers (responsive design)

---

## 🛠️ Troubleshooting

### Models not loading?
```python
# Check if models directory exists and is readable
import os
print(os.path.exists('trained_models/'))
print(os.listdir('trained_models/'))
```

### Port already in use?
```bash
# Use different port
streamlit run diabetes_prediction_app.py --server.port=9000
```

### Performance issues?
- Models are cached using `@st.cache_resource`
- First load may be slower, subsequent loads are instant
- All predictions are < 100ms per patient

---

## 📈 Future Enhancements

Potential features for future versions:
- [ ] Patient history tracking (with consent)
- [ ] Batch processing for multiple patients
- [ ] Integration with hospital EHR systems
- [ ] Custom model training with hospital data
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Mobile app version
- [ ] Real-time risk monitoring

---

## 📞 Support & Maintenance

### For Technical Issues:
1. Check error messages in console
2. Verify all dependencies installed: `pip list`
3. Ensure models are in correct directory
4. Clear Streamlit cache: `streamlit cache clear`

### For Model Updates:
1. Retrain models with new data
2. Save with same filenames (pkl format)
3. Replace in `trained_models/` directory
4. Restart application

---

## 📄 License & Attribution

This diabetes prediction system is designed for clinical use.
- Models: Trained on validated clinical datasets
- Data: No real patient data stored or transmitted
- Compliance: Designed for HIPAA and hospital standards

---

## 👨‍⚕️ Developed For Healthcare Professionals

This tool is specifically engineered for:
- Endocrinologists
- General Practitioners
- Nurses
- Clinic staff
- Hospital administrators

**Version**: 1.0  
**Last Updated**: June 2026  
**Status**: Production Ready ✓

---

Made with ❤️ for better healthcare outcomes
