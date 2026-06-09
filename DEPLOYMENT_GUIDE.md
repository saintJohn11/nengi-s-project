# 🏥 Hospital Deployment Configuration Guide

## Quick Setup for Hospital IT Teams

### Environment Variables
Create a `.env` file in your deployment directory:

```env
# Streamlit Configuration
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_MAXUPLOADSIZE=1024
STREAMLIT_CLIENT_SHOWSTARTMESSAGE=false
STREAMLIT_LOGGER_LEVEL=info

# Hospital Specific
HOSPITAL_NAME="Your Hospital Name"
HOSPITAL_DEPARTMENT="Endocrinology"
APP_VERSION="1.0"
ENVIRONMENT="production"

# Security
ENABLE_XSRF_PROTECTION=true
SECURE_HEADERS=true
```

---

## Security Configuration Template

### Step 1: HTTPS with Self-Signed Certificate (Hospital Internal)
```bash
# Generate certificate (valid for 365 days)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Common Name: diabetes-assessment.hospital.local
# Organization: Your Hospital Name
```

### Step 2: Nginx Reverse Proxy with Authentication
Create `/etc/nginx/sites-available/diabetes-app`:

```nginx
upstream streamlit {
    server 127.0.0.1:8501;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=diabetes_limit:10m rate=10r/s;

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    
    server_name diabetes-assessment.hospital.local;
    
    # SSL Certificates
    ssl_certificate /etc/ssl/certs/hospital.crt;
    ssl_certificate_key /etc/ssl/private/hospital.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    
    # Basic Authentication (Active Directory recommended instead)
    auth_basic "Hospital Access Required";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    # Rate Limiting
    limit_req zone=diabetes_limit burst=20 nodelay;
    
    # Logging
    access_log /var/log/nginx/diabetes_access.log combined;
    error_log /var/log/nginx/diabetes_error.log;
    
    # Proxy Configuration
    location / {
        proxy_pass http://streamlit;
        
        # Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Original-URL $scheme://$http_host$request_uri;
        
        # Timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name diabetes-assessment.hospital.local;
    return 301 https://$server_name$request_uri;
}
```

### Step 3: Create Basic Auth File
```bash
# Install htpasswd utility
sudo apt-get install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd doctor1
sudo htpasswd /etc/nginx/.htpasswd doctor2
sudo htpasswd /etc/nginx/.htpasswd nurse1

# Set permissions
sudo chmod 640 /etc/nginx/.htpasswd
```

### Step 4: Enable Nginx Configuration
```bash
sudo ln -s /etc/nginx/sites-available/diabetes-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Advanced: Active Directory Integration

For hospital networks using Active Directory:

### Install Nginx Auth Module
```bash
sudo apt-get install libnginx-mod-http-auth-pam

# Create PAM service config (/etc/pam.d/nginx-diabetes):
auth    required    pam_unix.so shadow nodelay
account required    pam_unix.so
```

### Update Nginx config to use AD:
```nginx
location / {
    auth_pam "Hospital Active Directory";
    auth_pam_service_name "nginx-diabetes";
    
    # Rest of proxy config...
}
```

---

## Systemd Service Management

### Service File: `/etc/systemd/system/diabetes-assessment.service`
```ini
[Unit]
Description=Hospital Diabetes Risk Assessment System
Documentation=man:streamlit(1)
After=network.target
Requires=network-online.target

[Service]
Type=simple
User=streamlit
Group=streamlit
WorkingDirectory=/opt/diabetes-assessment

# Environment
EnvironmentFile=/opt/diabetes-assessment/.env
Environment="PATH=/opt/diabetes-assessment/venv/bin:/usr/local/bin:/usr/bin"

# Startup
ExecStart=/opt/diabetes-assessment/venv/bin/streamlit run diabetes_prediction_app.py \
    --logger.level=info \
    --server.port=8501 \
    --server.headless=true \
    --client.showErrorDetails=false

# Restart policy
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=diabetes-app

# Security
PrivateTmp=yes
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/diabetes-assessment/logs

# Resource Limits
LimitNOFILE=65535
LimitNPROC=4096

# Timeouts
TimeoutStartSec=30
TimeoutStopSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable diabetes-assessment.service
sudo systemctl start diabetes-assessment.service

# Check status
sudo systemctl status diabetes-assessment.service

# View logs
sudo journalctl -u diabetes-assessment.service -f
```

---

## Database Integration (Optional)

For hospitals wanting to track assessments (with proper consent):

### SQLite Example (Built-in, No Setup Required)
```python
# Add to app for optional logging (disabled by default)
import sqlite3
from datetime import datetime

def log_assessment(patient_id, age, glucose, risk_level, probability):
    """Log assessment to local database (requires user consent)"""
    conn = sqlite3.connect('assessments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS assessments
                 (id INTEGER PRIMARY KEY, patient_id TEXT, age INT, 
                  glucose INT, risk_level TEXT, probability REAL, 
                  timestamp TEXT)''')
    c.execute('INSERT INTO assessments VALUES (?, ?, ?, ?, ?, ?, ?)',
              (None, patient_id, age, glucose, risk_level, probability, 
               datetime.now().isoformat()))
    conn.commit()
    conn.close()
```

### PostgreSQL Integration (For Large Hospitals)
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Connection example
import psycopg2

conn = psycopg2.connect(
    host="db.hospital.local",
    database="diabetes_assessments",
    user="app_user",
    password="secure_password"
)
```

---

## Monitoring & Logging

### Setup Log Rotation
Create `/etc/logrotate.d/diabetes-app`:
```
/var/log/diabetes-assessment/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 streamlit streamlit
    sharedscripts
    postrotate
        systemctl reload diabetes-assessment > /dev/null 2>&1 || true
    endscript
}
```

### Monitor Application Health
```bash
# Create health check script
cat > /opt/diabetes-assessment/health_check.sh << 'EOF'
#!/bin/bash
curl -s https://diabetes-assessment.hospital.local/health || \
    systemctl restart diabetes-assessment
EOF

chmod +x /opt/diabetes-assessment/health_check.sh

# Add to crontab (check every 5 minutes)
*/5 * * * * /opt/diabetes-assessment/health_check.sh
```

---

## Backup & Disaster Recovery

### Backup Models (Critical!)
```bash
# Create daily backups
0 2 * * * tar -czf /backup/diabetes-models-$(date +\%Y\%m\%d).tar.gz \
    /opt/diabetes-assessment/trained_models/

# Keep 30 days of backups
find /backup -name "diabetes-models-*.tar.gz" -mtime +30 -delete
```

### Restore from Backup
```bash
cd /opt/diabetes-assessment
tar -xzf /backup/diabetes-models-20260609.tar.gz
systemctl restart diabetes-assessment
```

---

## Performance Tuning

### For High-Volume Hospitals
```bash
# Increase system limits
echo "streamlit soft nofile 65535" >> /etc/security/limits.conf
echo "streamlit hard nofile 65535" >> /etc/security/limits.conf

# Optimize Nginx for streaming
cat >> /etc/nginx/nginx.conf << 'EOF'
http {
    # Increase buffer sizes
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json;
}
EOF
```

### Streamlit Performance Settings
```toml
# ~/.streamlit/config.toml
[client]
maxMessageSize = 200

[logger]
level = "warning"

[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = true

[browser]
serverAddress = "diabetes-assessment.hospital.local"
```

---

## HIPAA Compliance Checklist

- [ ] HTTPS/TLS enabled (encryption in transit)
- [ ] Access authentication (AD/SSO)
- [ ] Audit logging enabled
- [ ] Regular backups configured
- [ ] No patient data stored in app
- [ ] Secure deletion of logs (30 days)
- [ ] Staff training completed
- [ ] Legal review conducted
- [ ] Business Associate Agreement (BAA) signed
- [ ] Security Officer approved

---

## IT Admin Quick Commands

```bash
# Check app status
systemctl status diabetes-assessment

# View recent logs
journalctl -u diabetes-assessment -n 50

# Restart application
systemctl restart diabetes-assessment

# Test Nginx configuration
nginx -t

# Monitor system resources
htop -p $(pgrep -f streamlit)

# Verify HTTPS certificate
openssl x509 -in /etc/ssl/certs/hospital.crt -text -noout
```

---

## Support Contact Information

For technical issues, contact your hospital's:
- **Systems Administrator**: Infrastructure support
- **Security Officer**: Compliance and authentication
- **Clinical Informatics**: Integration with EHR

---

**Version**: 1.0  
**Last Updated**: June 2026  
**Maintenance**: Hospital IT Department
