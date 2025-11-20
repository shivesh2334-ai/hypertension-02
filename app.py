aimport streamlit as st
import pandas as pd
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Hypertension Management System",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .risk-low {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .risk-moderate {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .risk-high {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    .info-box {
        background-color: #e7f3ff;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'patient_data' not in st.session_state:
    st.session_state.patient_data = {}

# Sidebar navigation
st.sidebar.title("🏥 Navigation")
page = st.sidebar.radio(
    "Select Section",
    ["Home", "Patient Assessment", "Treatment Options", "Diet Advice", "Exercise Plan", "Reports"]
)

# Helper Functions
def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)

def classify_bp(systolic, diastolic):
    """Classify blood pressure"""
    if systolic < 120 and diastolic < 80:
        return "Normal", "low"
    elif systolic < 130 and diastolic < 80:
        return "Elevated", "moderate"
    elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
        return "Stage 1 Hypertension", "moderate"
    elif systolic >= 140 or diastolic >= 90:
        return "Stage 2 Hypertension", "high"
    elif systolic >= 180 or diastolic >= 120:
        return "Hypertensive Crisis - EMERGENCY", "high"
    return "Unknown", "moderate"

def calculate_risk_score(data):
    """Calculate cardiovascular risk score"""
    score = 0
    
    # Age factor
    if data.get('age', 0) > 65:
        score += 3
    elif data.get('age', 0) > 55:
        score += 2
    elif data.get('age', 0) > 45:
        score += 1
    
    # BMI factor
    bmi = data.get('bmi', 0)
    if bmi >= 30:
        score += 2
    elif bmi >= 25:
        score += 1
    
    # Comorbidities
    if data.get('diabetes'):
        score += 3
    if data.get('cad'):
        score += 3
    if data.get('ckd'):
        score += 2
    if data.get('smoking'):
        score += 2
    
    # BP classification
    bp_class, _ = classify_bp(data.get('systolic', 120), data.get('diastolic', 80))
    if "Crisis" in bp_class:
        score += 5
    elif "Stage 2" in bp_class:
        score += 3
    elif "Stage 1" in bp_class:
        score += 2
    
    return score

def get_risk_category(score):
    """Determine risk category based on score"""
    if score <= 3:
        return "Low Risk", "low"
    elif score <= 7:
        return "Moderate Risk", "moderate"
    elif score <= 12:
        return "High Risk", "high"
    else:
        return "Very High Risk", "high"

# HOME PAGE
if page == "Home":
    st.markdown('<h1 class="main-header">🩺 Hypertension Management System</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📋 **Comprehensive Assessment**\n\nComplete patient evaluation with risk stratification")
    
    with col2:
        st.success("💊 **Treatment Planning**\n\nEvidence-based medication and management strategies")
    
    with col3:
        st.warning("🥗 **Lifestyle Management**\n\nPersonalized diet and exercise recommendations")
    
    st.markdown("---")
    
    st.markdown("### 📊 About This System")
    st.write("""
    This comprehensive hypertension management system helps healthcare providers:
    
    - **Assess** patients using standardized protocols
    - **Identify** modifiable and non-modifiable risk factors
    - **Screen** for secondary hypertension
    - **Plan** appropriate treatment strategies
    - **Provide** personalized lifestyle recommendations
    - **Monitor** patient progress over time
    
    Navigate using the sidebar to begin patient assessment.
    """)
    
    st.markdown("---")
    st.info("⚠️ **Emergency Protocol**: Any patient with BP ≥180/120 mmHg with symptoms requires immediate emergency referral")

# PATIENT ASSESSMENT PAGE
elif page == "Patient Assessment":
    st.markdown('<h1 class="main-header">📋 Patient Assessment</h1>', unsafe_allow_html=True)
    
    tabs = st.tabs(["Demographics & Vitals", "Medical History", "Risk Factors", "Secondary HTN Screening", "Assessment Summary"])
    
    # Tab 1: Demographics & Vitals
    with tabs[0]:
        st.markdown('<div class="section-header">Patient Demographics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Name", key="patient_name")
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=45, key="age")
            sex = st.selectbox("Sex", ["Male", "Female"], key="sex")
        
        with col2:
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.1, key="weight")
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=170.0, step=0.1, key="height")
            waist = st.number_input("Waist Circumference (cm)", min_value=50.0, max_value=200.0, value=85.0, step=0.1, key="waist")
        
        # Calculate BMI
        bmi = calculate_bmi(weight, height)
        st.metric("Calculated BMI", f"{bmi} kg/m²")
        
        if bmi < 18.5:
            st.info("Underweight")
        elif 18.5 <= bmi < 25:
            st.success("Normal weight")
        elif 25 <= bmi < 30:
            st.warning("Overweight")
        else:
            st.error("Obese")
        
        st.markdown('<div class="section-header">Vital Signs</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            systolic = st.number_input("Systolic BP (mmHg)", min_value=70, max_value=250, value=130, key="systolic")
        
        with col2:
            diastolic = st.number_input("Diastolic BP (mmHg)", min_value=40, max_value=150, value=85, key="diastolic")
        
        with col3:
            hr = st.number_input("Heart Rate (bpm)", min_value=40, max_value=200, value=75, key="hr")
        
        # BP Classification
        bp_class, bp_risk = classify_bp(systolic, diastolic)
        
        if bp_risk == "low":
            st.success(f"**Blood Pressure Classification:** {bp_class}")
        elif bp_risk == "moderate":
            st.warning(f"**Blood Pressure Classification:** {bp_class}")
        else:
            st.error(f"**Blood Pressure Classification:** {bp_class}")
        
        if systolic >= 180 or diastolic >= 120:
            st.error("⚠️ **EMERGENCY**: Patient requires immediate emergency referral!")
        
        duration_htn = st.number_input("Duration of Hypertension (years)", min_value=0, max_value=50, value=0, key="duration_htn")
    
    # Tab 2: Medical History
    with tabs[1]:
        st.markdown('<div class="section-header">History of Present Illness</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**When was Elevated BP First Detected?**")
            bp_first_detected = st.selectbox(
                "Time frame",
                ["Current visit", "Within last 6 months", "6-12 months ago", 
                 "1-2 years ago", "2-5 years ago", ">5 years ago"],
                key="bp_first_detected"
            )
            
            st.markdown("**Previous Treatment History**")
            previous_treatment = st.multiselect(
                "Select all that apply",
                ["Never treated", "Diet/lifestyle only", "Previous medication (stopped)",
                 "Currently on medication", "Non-compliant with medication"],
                key="previous_treatment"
            )
            
            if "Currently on medication" in previous_treatment:
                current_meds = st.text_area("List current medications and doses", key="current_meds")
        
        with col2:
            st.markdown("**Average BP Readings**")
            home_monitoring = st.checkbox("Home BP monitoring", key="home_monitoring")
            if home_monitoring:
                home_bp_sys = st.number_input("Average home systolic", min_value=80, max_value=200, value=130, key="home_bp_sys")
                home_bp_dia = st.number_input("Average home diastolic", min_value=50, max_value=130, value=85, key="home_bp_dia")
            
            st.markdown("**Target Organ Damage Symptoms**")
            target_organ_symptoms = st.multiselect(
                "Check if present",
                ["None", "Chest pain/angina", "Shortness of breath", "Palpitations",
                 "Headaches", "Vision changes", "Dizziness", "Nosebleeds",
                 "Fatigue", "Confusion", "Blood in urine"],
                key="target_organ_symptoms"
            )
        
        st.markdown("---")
        st.markdown('<div class="section-header">Physical Examination Findings</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**General**")
            general_appearance = st.text_area("General appearance", placeholder="Well-appearing, no acute distress", key="general_appearance", height=80)
            
            st.markdown("**HEENT**")
            fundoscopic = st.selectbox("Fundoscopic exam", ["Normal", "AV nicking", "Hemorrhages", "Papilledema", "Not done"], key="fundoscopic")
            thyroid = st.selectbox("Thyroid", ["Normal", "Enlarged", "Nodules"], key="thyroid_exam")
        
        with col2:
            st.markdown("**Cardiovascular**")
            heart_sounds = st.multiselect(
                "Heart sounds",
                ["Regular rhythm", "S4 gallop", "S3 gallop", "Murmur", "Normal S1/S2"],
                default=["Regular rhythm", "Normal S1/S2"],
                key="heart_sounds"
            )
            
            peripheral_pulses = st.selectbox("Peripheral pulses", ["Normal", "Diminished", "Absent", "Asymmetric"], key="peripheral_pulses")
            carotid_bruit = st.checkbox("Carotid bruit", key="carotid_bruit")
            abdominal_bruit = st.checkbox("Abdominal bruit", key="abdominal_bruit_exam")
        
        with col3:
            st.markdown("**Extremities**")
            edema = st.selectbox("Edema", ["None", "Trace", "1+", "2+", "3+", "4+"], key="edema")
            
            st.markdown("**Neurological**")
            neuro_exam = st.multiselect(
                "Findings",
                ["Grossly intact", "Focal deficits", "Sensory changes", "Motor weakness"],
                default=["Grossly intact"],
                key="neuro_exam"
            )
        
        st.markdown("---")
        st.markdown('<div class="section-header">Comorbidities & Target Organ Damage</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Major Risk Factors**")
            diabetes = st.checkbox("Diabetes Mellitus", key="diabetes")
            if diabetes:
                diabetes_duration = st.number_input("Duration (years)", min_value=0, max_value=60, value=5, key="diabetes_duration")
                hba1c = st.number_input("HbA1c (%)", min_value=4.0, max_value=15.0, value=6.5, step=0.1, key="hba1c")
            
            dyslipidemia = st.checkbox("Dyslipidemia", key="dyslipidemia")
            if dyslipidemia:
                total_chol = st.number_input("Total Cholesterol (mg/dL)", min_value=100, max_value=500, value=200, key="total_chol")
                ldl = st.number_input("LDL (mg/dL)", min_value=50, max_value=300, value=130, key="ldl")
                hdl = st.number_input("HDL (mg/dL)", min_value=20, max_value=100, value=45, key="hdl")
                triglycerides = st.number_input("Triglycerides (mg/dL)", min_value=50, max_value=1000, value=150, key="triglycerides")
            
            microalbuminuria = st.checkbox("Microalbuminuria/Proteinuria", key="microalbuminuria")
            if microalbuminuria:
                protein_amount = st.number_input("24hr urine protein (mg)", min_value=0, max_value=5000, value=300, key="protein_amount")
            
            gfr_reduced = st.checkbox("GFR <60 mL/min", key="gfr_reduced")
            if gfr_reduced:
                gfr_value = st.number_input("eGFR (mL/min/1.73m²)", min_value=5, max_value=59, value=45, key="gfr_value")
        
        with col2:
            st.markdown("**Target Organ Damage/Clinical Cardiovascular Disease**")
            
            lvh = st.checkbox("Left Ventricular Hypertrophy (LVH)", key="lvh")
            if lvh:
                lvh_type = st.multiselect("Detected by", ["ECG", "Echocardiography", "Both"], key="lvh_type")
            
            cad = st.checkbox("Coronary Artery Disease", key="cad")
            if cad:
                cad_details = st.multiselect(
                    "Specify",
                    ["Previous MI", "Angina pectoris", "CABG", "PCI/Stent", "Stable angina"],
                    key="cad_details"
                )
            
            heart_failure = st.checkbox("Heart Failure", key="heart_failure")
            if heart_failure:
                hf_type = st.selectbox("Type", ["HFrEF (systolic)", "HFpEF (diastolic)", "Both"], key="hf_type")
                nyha_class = st.selectbox("NYHA Class", ["I", "II", "III", "IV"], key="nyha_class")
            
            cva = st.checkbox("Stroke/TIA", key="cva")
            if cva:
                stroke_type = st.selectbox("Type", ["Ischemic stroke", "TIA", "Hemorrhagic stroke"], key="stroke_type")
                stroke_date = st.date_input("Date of event", key="stroke_date")
            
            ckd = st.checkbox("Chronic Kidney Disease", key="ckd")
            if ckd:
                ckd_stage = st.selectbox("CKD Stage", ["Stage 1", "Stage 2", "Stage 3a", "Stage 3b", "Stage 4", "Stage 5"], key="ckd_stage")
                creatinine = st.number_input("Serum Creatinine (mg/dL)", min_value=0.5, max_value=15.0, value=1.2, step=0.1, key="creatinine")
            
            pad = st.checkbox("Peripheral Arterial Disease", key="pad")
            retinopathy = st.checkbox("Hypertensive Retinopathy", key="retinopathy")
            if retinopathy:
                retinopathy_grade = st.selectbox("Grade", ["Grade 1", "Grade 2", "Grade 3", "Grade 4"], key="retinopathy_grade")
        
        st.markdown("---")
        st.markdown('<div class="section-header">Family History</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fh_htn = st.checkbox("Hypertension", key="fh_htn")
            if fh_htn:
                fh_htn_relation = st.text_input("Relation(s)", placeholder="e.g., Mother, Father", key="fh_htn_relation")
            
            fh_premature_cad = st.checkbox("Premature CAD (Men <55, Women <65)", key="fh_premature_cad")
            if fh_premature_cad:
                fh_cad_details = st.text_input("Details", placeholder="Age and relation", key="fh_cad_details")
        
        with col2:
            fh_stroke = st.checkbox("Stroke/CVA", key="fh_stroke")
            if fh_stroke:
                fh_stroke_relation = st.text_input("Relation(s)", placeholder="e.g., Grandmother", key="fh_stroke_relation")
            
            fh_kidney = st.checkbox("Kidney Disease", key="fh_kidney")
            fh_diabetes = st.checkbox("Diabetes Mellitus", key="fh_diabetes")
            fh_sudden_death = st.checkbox("Sudden Cardiac Death", key="fh_sudden_death")
    
    # Tab 3: Risk Factors
    with tabs[2]:
        st.markdown('<div class="section-header">Modifiable Risk Factors</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            smoking = st.checkbox("Current Smoker", key="smoking")
            if smoking:
                cigs_per_day = st.number_input("Cigarettes per day", min_value=1, max_value=100, value=10, key="cigs_per_day")
                smoking_years = st.number_input("Years of smoking", min_value=1, max_value=60, value=10, key="smoking_years")
            
            alcohol = st.checkbox("Alcohol Consumption", key="alcohol")
            if alcohol:
                drinks_per_week = st.number_input("Drinks per week", min_value=1, max_value=50, value=5, key="drinks_per_week")
            
            physical_inactivity = st.checkbox("Physical Inactivity (<150 min/week)", key="physical_inactivity")
            high_salt = st.checkbox("High Salt Intake", key="high_salt")
        
        with col2:
            poor_diet = st.checkbox("Poor Diet Quality", key="poor_diet")
            stress = st.checkbox("Chronic Stress", key="stress")
            sleep_deprivation = st.checkbox("Sleep Deprivation (<6 hrs/night)", key="sleep_deprivation")
            sleep_apnea_symptoms = st.checkbox("Sleep Apnea Symptoms", key="sleep_apnea_symptoms")
    
    # Tab 4: Secondary HTN Screening
    with tabs[3]:
        st.markdown('<div class="section-header">Laboratory Evaluation</div>', unsafe_allow_html=True)
        
        st.info("**Routine Tests Recommended for All Patients**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Basic Labs**")
            urinalysis_done = st.checkbox("Urinalysis", key="urinalysis_done")
            if urinalysis_done:
                protein = st.selectbox("Protein", ["Negative", "Trace", "1+", "2+", "3+", "4+"], key="urine_protein")
                blood = st.selectbox("Blood", ["Negative", "Trace", "1+", "2+", "3+"], key="urine_blood")
                glucose_urine = st.selectbox("Glucose", ["Negative", "Trace", "1+", "2+"], key="urine_glucose")
            
            bmp_done = st.checkbox("Basic Metabolic Panel", key="bmp_done")
            if bmp_done:
                sodium = st.number_input("Sodium (mEq/L)", min_value=120, max_value=160, value=140, key="sodium")
                potassium = st.number_input("Potassium (mEq/L)", min_value=2.5, max_value=7.0, value=4.0, step=0.1, key="potassium")
                creatinine_lab = st.number_input("Creatinine (mg/dL)", min_value=0.3, max_value=15.0, value=1.0, step=0.1, key="creatinine_lab")
                egfr = st.number_input("eGFR (mL/min/1.73m²)", min_value=5, max_value=150, value=90, key="egfr")
        
        with col2:
            st.markdown("**Lipid Panel**")
            lipids_done = st.checkbox("Fasting Lipid Profile", key="lipids_done")
            if lipids_done:
                total_chol_lab = st.number_input("Total Cholesterol (mg/dL)", min_value=100, max_value=500, value=200, key="total_chol_lab")
                ldl_lab = st.number_input("LDL (mg/dL)", min_value=30, max_value=300, value=130, key="ldl_lab")
                hdl_lab = st.number_input("HDL (mg/dL)", min_value=20, max_value=100, value=50, key="hdl_lab")
                tg_lab = st.number_input("Triglycerides (mg/dL)", min_value=30, max_value=1000, value=150, key="tg_lab")
            
            st.markdown("**Glucose**")
            fasting_glucose = st.number_input("Fasting Glucose (mg/dL)")            
