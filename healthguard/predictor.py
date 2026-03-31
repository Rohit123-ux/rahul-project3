"""
HealthGuard — predictor.py
Loads all 3 models and runs predictions from unified input
"""
import numpy as np
import pickle
import os

# ── LOAD ALL MODELS ON STARTUP ────────────────────
def load_models():
    models = {}
    base = os.path.join(os.path.dirname(__file__), 'models')

    # FIX: Wrapped in try/except — gives a clear error message if any .pkl is missing
    # instead of a raw FileNotFoundError with no context.
    try:
        models['heart_model']    = pickle.load(open(f'{base}/heart_model.pkl',    'rb'))
        models['heart_scaler']   = pickle.load(open(f'{base}/heart_scaler.pkl',   'rb'))
        models['heart_features'] = pickle.load(open(f'{base}/heart_features.pkl', 'rb'))

        models['diabetes_model']    = pickle.load(open(f'{base}/diabetes_model.pkl',    'rb'))
        models['diabetes_scaler']   = pickle.load(open(f'{base}/diabetes_scaler.pkl',   'rb'))
        models['diabetes_features'] = pickle.load(open(f'{base}/diabetes_features.pkl', 'rb'))

        models['kidney_model']    = pickle.load(open(f'{base}/kidney_model.pkl',    'rb'))
        models['kidney_scaler']   = pickle.load(open(f'{base}/kidney_scaler.pkl',   'rb'))
        models['kidney_imputer']  = pickle.load(open(f'{base}/kidney_imputer.pkl',  'rb'))
        models['kidney_features'] = pickle.load(open(f'{base}/kidney_features.pkl', 'rb'))
    except FileNotFoundError as e:
        missing = str(e)
        raise RuntimeError(
            f"\n[HealthGuard] Model file not found: {missing}\n"
            "Make sure all .pkl files are placed inside the 'models/' folder.\n"
            "Required: heart_model.pkl, heart_scaler.pkl, heart_features.pkl,\n"
            "          diabetes_model.pkl, diabetes_scaler.pkl, diabetes_features.pkl,\n"
            "          kidney_model.pkl, kidney_scaler.pkl, kidney_imputer.pkl, kidney_features.pkl"
        ) from e
    except Exception as e:
        raise RuntimeError(f"[HealthGuard] Failed to load ML models: {e}") from e

    return models

MODELS = load_models()

# ── RISK LEVEL ────────────────────────────────────
def risk_level(pct):
    if pct < 30:  return "Low Risk"
    if pct < 60:  return "Moderate Risk"
    return              "High Risk"

def advice(disease, pct):
    if disease == 'heart':
        if pct < 30: return "Your cardiovascular indicators look healthy. Maintain regular exercise and a balanced diet."
        if pct < 60: return "Moderate cardiovascular risk detected. Monitor blood pressure and cholesterol regularly. Consult a doctor."
        return "High cardiovascular risk detected. Consult a cardiologist immediately and avoid strenuous activity."
    if disease == 'diabetes':
        if pct < 30: return "Blood sugar indicators appear normal. Maintain a low-sugar diet and stay physically active."
        if pct < 60: return "Pre-diabetic indicators present. Reduce sugar intake and get an HbA1c test done soon."
        return "High diabetes risk detected. Consult an endocrinologist and monitor fasting blood glucose daily."
    if disease == 'kidney':
        if pct < 30: return "Kidney function indicators are within normal range. Stay well-hydrated every day."
        if pct < 60: return "Mild kidney stress markers present. Reduce sodium intake and check creatinine levels."
        return "Significant kidney disease risk detected. Consult a nephrologist and get a GFR test urgently."

# ── UNIFIED PREDICT ───────────────────────────────
def predict_all(data):
    """
    data: dict with keys from unified form
    Returns: dict with heart, diabetes, kidney predictions
    """
    results = {}

    # ── HEART ──────────────────────────────────────
    # features: age,sex,cp,trestbps,chol,fbs,restecg,thalach,exang,oldpeak,slope,ca,thal
    # fbs = 1 if fasting blood sugar > 120
    # exang = exercise induced angina (0/1)
    # oldpeak, slope, ca, thal — use defaults if not provided
    fbs   = 1 if float(data.get('fasting_sugar', 100)) > 120 else 0
    exang = int(data.get('exang', 0))
    heart_input = np.array([[
        float(data['age']),
        float(data['sex']),
        float(data['cp']),
        float(data['trestbps']),
        float(data['chol']),
        fbs,
        float(data.get('restecg', 0)),
        float(data['thalach']),
        exang,
        float(data.get('oldpeak', 1.0)),
        float(data.get('slope', 1)),
        float(data.get('ca', 0)),
        float(data.get('thal', 2)),
    ]])
    heart_scaled = MODELS['heart_scaler'].transform(heart_input)
    heart_proba  = MODELS['heart_model'].predict_proba(heart_scaled)[0]
    heart_pct    = round(heart_proba[1] * 100, 1)
    results['heart'] = {
        'probability': heart_pct,
        'risk_level':  risk_level(heart_pct),
        'advice':      advice('heart', heart_pct),
        'prediction':  int(heart_pct >= 50),
    }

    # ── DIABETES ───────────────────────────────────
    # features: Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age
    diab_input = np.array([[
        float(data.get('pregnancies', 0)),
        float(data['glucose']),
        float(data['trestbps']),          # reuse blood pressure
        float(data.get('skin_thickness', 29)),
        float(data.get('insulin', 125)),
        float(data['bmi']),
        float(data.get('dpf', 0.47)),
        float(data['age']),
    ]])
    diab_scaled = MODELS['diabetes_scaler'].transform(diab_input)
    diab_proba  = MODELS['diabetes_model'].predict_proba(diab_scaled)[0]
    diab_pct    = round(diab_proba[1] * 100, 1)
    results['diabetes'] = {
        'probability': diab_pct,
        'risk_level':  risk_level(diab_pct),
        'advice':      advice('diabetes', diab_pct),
        'prediction':  int(diab_pct >= 50),
    }

    # ── KIDNEY ─────────────────────────────────────
    # features: age,bp,sg,al,su,rbc,pc,pcc,ba,bgr,bu,sc,sod,pot,hemo,pcv,wc,rc,htn,dm,cad,appet,pe,ane
    kidney_input = np.array([[
        float(data['age']),
        float(data['trestbps']),           # bp
        float(data.get('sg',   1.020)),    # specific gravity
        float(data.get('al',   0)),        # albumin
        float(data.get('su',   0)),        # sugar in urine
        float(data.get('rbc',  0)),        # rbc (0=normal)
        float(data.get('pc',   0)),        # pus cell (0=normal)
        float(data.get('pcc',  0)),        # pus cell clumps
        float(data.get('ba',   0)),        # bacteria
        float(data['glucose']),            # bgr = blood glucose random
        float(data.get('bu',   40)),       # blood urea
        float(data['sc']),                 # serum creatinine
        float(data.get('sod',  135)),      # sodium
        float(data.get('pot',  4.5)),      # potassium
        float(data['hemo']),               # hemoglobin
        float(data.get('pcv',  44)),       # packed cell volume
        float(data.get('wc',   8000)),     # white blood cell count
        float(data.get('rc',   5.2)),      # red blood cell count
        float(data.get('htn',  0)),        # hypertension
        float(data.get('dm',   0)),        # diabetes mellitus
        float(data.get('cad',  0)),        # coronary artery disease
        float(data.get('appet',0)),        # appetite (0=good)
        float(data.get('pe',   0)),        # pedal edema
        float(data.get('ane',  0)),        # anemia
    ]])
    kidney_imp    = MODELS['kidney_imputer'].transform(kidney_input)
    kidney_scaled = MODELS['kidney_scaler'].transform(kidney_imp)
    kidney_proba  = MODELS['kidney_model'].predict_proba(kidney_scaled)[0]
    kidney_pct    = round(kidney_proba[1] * 100, 1)
    results['kidney'] = {
        'probability': kidney_pct,
        'risk_level':  risk_level(kidney_pct),
        'advice':      advice('kidney', kidney_pct),
        'prediction':  int(kidney_pct >= 50),
    }

    # ── OVERALL HEALTH SCORE ───────────────────────
    avg_risk  = (heart_pct + diab_pct + kidney_pct) / 3
    score     = round(100 - avg_risk)
    score     = max(0, min(100, score))

    if score >= 75:   status = "Good Health";       sub = "Keep up your healthy lifestyle"
    elif score >= 50: status = "Needs Attention";   sub = "Consult a doctor for a checkup"
    else:             status = "Seek Medical Care"; sub = "Multiple risk factors detected"

    results['overall'] = {
        'score':  score,
        'status': status,
        'sub':    sub,
    }

    return results
