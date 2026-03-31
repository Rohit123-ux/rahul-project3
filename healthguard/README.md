# 🛡️ HealthGuard — Multi Disease Risk Assessment System
### B.Tech Final Year Project | Dept. of CSE | Govt. College of Engineering, Odisha

---

## 📦 Project Structure
```
healthguard_db/
├── data/                    ← 3 real datasets
├── models/                  ← 3 trained ML models (.pkl files)
├── templates/               ← All HTML pages
│   ├── base.html            ← Base layout (navbar, styles)
│   ├── index.html           ← Landing page
│   ├── login.html           ← Login page
│   ├── register.html        ← Patient registration
│   ├── patient_dashboard.html ← Patient dashboard
│   ├── predict.html         ← Health check form
│   ├── result.html          ← Prediction results
│   ├── history.html         ← All past predictions
│   ├── doctor_dashboard.html ← Doctor overview
│   └── view_patient.html    ← Individual patient view
├── config.py                ← MySQL configuration
├── models.py                ← Database table definitions
├── predictor.py             ← ML prediction logic
├── report.py                ← PDF report generation
├── app.py                   ← Flask routes and logic
└── requirements.txt         ← All dependencies
```

---

## 🚀 Setup Instructions

### Step 1 — Install MySQL
- Download MySQL from: https://dev.mysql.com/downloads/installer/
- Install with default settings
- Remember your root password

### Step 2 — Create Database
Open MySQL Command Line or phpMyAdmin and run:
```sql
CREATE DATABASE healthguard;
```

### Step 3 — Update Config
Open `config.py` and set your MySQL password:
```python
MYSQL_PASSWORD = 'your_mysql_password_here'
```

### Step 4 — Install Python Libraries
```bash
pip install -r requirements.txt
```

### Step 5 — Run the App
```bash
python app.py
```

### Step 6 — Open Browser
```
http://localhost:5000
```

---

## 👤 Default Accounts

| Role   | Email                      | Password   |
|--------|----------------------------|------------|
| Doctor | doctor@healthguard.com     | doctor123  |

Register as a Patient from the home page.

---

## 🌟 Features

### Patient Features
- Register and login securely
- Fill one form → get 3 disease predictions
- View risk trend charts over time
- Download PDF health report
- See alerts when risk increases

### Doctor Features
- View all registered patients
- Filter by risk level (High / Moderate / Low)
- Search patient by name
- View individual patient history
- Download any patient PDF report

---

## 📊 Model Accuracy
| Disease       | Test Accuracy |
|---------------|---------------|
| Heart Disease | 88.33%        |
| Diabetes      | 74.03%        |
| Kidney Disease| 100.00%       |

---

## 🔧 Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Backend**: Python Flask
- **Database**: MySQL + Flask-SQLAlchemy
- **Auth**: Flask-Login + Flask-Bcrypt
- **ML**: scikit-learn (Voting Ensemble)
- **PDF**: ReportLab

---

*HealthGuard — B.Tech Final Year Project 2024–25*
