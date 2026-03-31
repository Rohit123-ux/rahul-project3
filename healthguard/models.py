"""
HealthGuard DB — models.py
Database table definitions:
  - User       (patients and doctors)
  - Prediction (every health check result)
  - Alert      (high risk notifications)
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ── USER TABLE ────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password      = db.Column(db.String(200), nullable=False)   # bcrypt hashed
    role          = db.Column(db.String(10), default='patient') # 'patient' or 'doctor'
    age           = db.Column(db.Integer, nullable=True)
    sex           = db.Column(db.String(10), nullable=True)     # 'Male' or 'Female'
    mobile        = db.Column(db.String(15), nullable=True)
    blood_group   = db.Column(db.String(5), nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    predictions   = db.relationship('Prediction', backref='patient', lazy=True)
    alerts        = db.relationship('Alert', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'


# ── PREDICTION TABLE ──────────────────────────────
class Prediction(db.Model):
    __tablename__ = 'predictions'

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # ── Input values ──
    age             = db.Column(db.Float)
    sex             = db.Column(db.Float)
    cp              = db.Column(db.Float)
    trestbps        = db.Column(db.Float)
    chol            = db.Column(db.Float)
    fasting_sugar   = db.Column(db.Float)
    glucose         = db.Column(db.Float)
    thalach         = db.Column(db.Float)
    exang           = db.Column(db.Float)
    oldpeak         = db.Column(db.Float)
    bmi             = db.Column(db.Float)
    pregnancies     = db.Column(db.Float)
    insulin         = db.Column(db.Float)
    hemo            = db.Column(db.Float)
    sc              = db.Column(db.Float)

    # ── Prediction results ──
    heart_risk      = db.Column(db.Float)   # percentage 0-100
    diabetes_risk   = db.Column(db.Float)
    kidney_risk     = db.Column(db.Float)
    overall_score   = db.Column(db.Integer) # score out of 100

    heart_level     = db.Column(db.String(20))  # Low/Moderate/High Risk
    diabetes_level  = db.Column(db.String(20))
    kidney_level    = db.Column(db.String(20))
    overall_status  = db.Column(db.String(30))  # Good Health / Needs Attention / Seek Medical Care

    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Prediction user={self.user_id} heart={self.heart_risk}% date={self.created_at}>'


# ── ALERT TABLE ───────────────────────────────────
class Alert(db.Model):
    __tablename__ = 'alerts'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    disease     = db.Column(db.String(20))   # 'heart' / 'diabetes' / 'kidney'
    old_risk    = db.Column(db.Float)
    new_risk    = db.Column(db.Float)
    message     = db.Column(db.String(200))
    is_read     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Alert {self.disease} {self.old_risk}%→{self.new_risk}%>'
