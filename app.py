import streamlit as st
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
        st.markdown('<div class="section-header">Comorbidities</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            diabetes = st.checkbox("Diabetes Mellitus", key="diabetes")
            if diabetes:
                hba1c = st.number_input("HbA1c (%)", min_value=4.0, max_value=15.0, value=6.5, step=0.1, key="hba1c")
            
            cad = st.checkbox("Coronary Artery Disease", key="cad")
            cva = st.checkbox("Cerebrovascular Accident (Stroke)", key="cva")
            ckd = st.checkbox("Chronic Kidney Disease", key="ckd")
            if ckd:
                ckd_stage = st.selectbox("CKD Stage", ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5"], key="ckd_stage")
        
        with col2:
            dyslipidemia = st.checkbox("Dyslipidemia", key="dyslipidemia")
            if dyslipidemia:
                total_chol = st.number_input("Total Cholesterol (mg/dL)", min_value=100, max_value=500, value=200, key="total_chol")
                ldl = st.number_input("LDL (mg/dL)", min_value=50, max_value=300, value=130, key="ldl")
                hdl = st.number_input("HDL (mg/dL)", min_value=20, max_value=100, value=45, key="hdl")
            
            thyroid = st.checkbox("Thyroid Disorder", key="thyroid")
            if thyroid:
                thyroid_type = st.selectbox("Type", ["Hypothyroidism", "Hyperthyroidism"], key="thyroid_type")
            
            lvh = st.checkbox("Left Ventricular Hypertrophy", key="lvh")
        
        st.markdown('<div class="section-header">Family History</div>', unsafe_allow_html=True)
        
        fh_htn = st.checkbox("Family History of Hypertension", key="fh_htn")
        fh_cad = st.checkbox("Family History of CAD", key="fh_cad")
        fh_stroke = st.checkbox("Family History of Stroke", key="fh_stroke")
        fh_kidney = st.checkbox("Family History of Kidney Disease", key="fh_kidney")
    
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
        st.markdown('<div class="section-header">Clinical Features Suggesting Secondary Hypertension</div>', unsafe_allow_html=True)
        
        resistant_htn = st.checkbox("Resistant Hypertension (uncontrolled on ≥3 drugs)", key="resistant_htn")
        acute_rise = st.checkbox("Acute Rise in Blood Pressure", key="acute_rise")
        malignant_htn = st.checkbox("Malignant/Accelerated Hypertension", key="malignant_htn")
        early_onset = st.checkbox("Onset before age 30 without risk factors", key="early_onset")
        onset_before_puberty = st.checkbox("Onset before puberty", key="onset_before_puberty")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Renal/Renovascular Clues**")
            abdominal_bruit = st.checkbox("Abdominal Bruit", key="abdominal_bruit")
            asymmetric_kidneys = st.checkbox("Asymmetric Kidney Sizes", key="asymmetric_kidneys")
            elevated_creatinine = st.checkbox("Elevated Creatinine", key="elevated_creatinine")
            abnormal_urinalysis = st.checkbox("Abnormal Urinalysis", key="abnormal_urinalysis")
        
        with col2:
            st.markdown("**Endocrine Clues**")
            hypokalemia = st.checkbox("Hypokalemia (suggests primary aldosteronism)", key="hypokalemia")
            cushings_features = st.checkbox("Cushing's Features", key="cushings_features")
            pheo_triad = st.checkbox("Pheochromocytoma Triad (headache, palpitations, sweating)", key="pheo_triad")
        
        st.markdown("---")
        st.markdown("**Medications That May Cause Hypertension**")
        
        medications = st.multiselect(
            "Select current medications",
            ["Oral Contraceptives", "NSAIDs", "Corticosteroids", "Decongestants", 
             "Anti-cancer Drugs", "Immunosuppressants", "Herbal Supplements"],
            key="medications"
        )
    
    # Tab 5: Assessment Summary
    with tabs[4]:
        st.markdown('<div class="section-header">Assessment Summary</div>', unsafe_allow_html=True)
        
        # Save all data to session state
        if st.button("Generate Assessment Summary", type="primary"):
            st.session_state.patient_data = {
                'patient_name': patient_name,
                'age': age,
                'sex': sex,
                'weight': weight,
                'height': height,
                'waist': waist,
                'bmi': bmi,
                'systolic': systolic,
                'diastolic': diastolic,
                'hr': hr,
                'duration_htn': duration_htn,
                'diabetes': diabetes,
                'cad': cad,
                'cva': cva,
                'ckd': ckd,
                'smoking': smoking,
                'physical_inactivity': physical_inactivity,
                'assessment_date': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            
            # Calculate risk score
            risk_score = calculate_risk_score(st.session_state.patient_data)
            risk_category, risk_level = get_risk_category(risk_score)
            
            st.session_state.patient_data['risk_score'] = risk_score
            st.session_state.patient_data['risk_category'] = risk_category
            
            st.success("✅ Assessment completed successfully!")
        
        if st.session_state.patient_data:
            data = st.session_state.patient_data
            
            st.markdown("### Patient Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Name", data.get('patient_name', 'N/A'))
                st.metric("Age", f"{data.get('age', 'N/A')} years")
            
            with col2:
                st.metric("BMI", f"{data.get('bmi', 'N/A')} kg/m²")
                st.metric("Blood Pressure", f"{data.get('systolic', 'N/A')}/{data.get('diastolic', 'N/A')} mmHg")
            
            with col3:
                bp_class, _ = classify_bp(data.get('systolic', 120), data.get('diastolic', 80))
                st.metric("BP Classification", bp_class)
            
            st.markdown("---")
            
            # Risk Assessment
            risk_score = data.get('risk_score', 0)
            risk_category, risk_level = get_risk_category(risk_score)
            
            if risk_level == "low":
                st.markdown(f'<div class="risk-low"><h3>Risk Category: {risk_category}</h3><p>Risk Score: {risk_score}/20+</p></div>', unsafe_allow_html=True)
            elif risk_level == "moderate":
                st.markdown(f'<div class="risk-moderate"><h3>Risk Category: {risk_category}</h3><p>Risk Score: {risk_score}/20+</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="risk-high"><h3>Risk Category: {risk_category}</h3><p>Risk Score: {risk_score}/20+</p></div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Recommendations
            st.markdown("### Immediate Actions Required")
            
            actions = []
            
            if data.get('systolic', 0) >= 180 or data.get('diastolic', 0) >= 120:
                actions.append("🚨 **EMERGENCY REFERRAL** - Hypertensive crisis")
            
            if risk_category in ["High Risk", "Very High Risk"]:
                actions.append("💊 Start or intensify antihypertensive therapy")
            
            if data.get('bmi', 0) >= 25:
                actions.append("🏃 Weight reduction program")
            
            if data.get('smoking'):
                actions.append("🚭 Smoking cessation counseling")
            
            if data.get('diabetes'):
                actions.append("🩸 Optimize diabetes management")
            
            actions.append("📋 Order basic investigations (CBC, LFT, KFT, Lipid Profile, HbA1c, TSH, ECG, Echo)")
            
            if resistant_htn or early_onset or malignant_htn:
                actions.append("🔬 Screen for secondary hypertension")
            
            for action in actions:
                st.write(action)

# TREATMENT OPTIONS PAGE
elif page == "Treatment Options":
    st.markdown('<h1 class="main-header">💊 Treatment Options</h1>', unsafe_allow_html=True)
    
    if not st.session_state.patient_data:
        st.warning("⚠️ Please complete Patient Assessment first")
    else:
        data = st.session_state.patient_data
        
        tabs = st.tabs(["Medication Selection", "Treatment Goals", "Monitoring Plan"])
        
        with tabs[0]:
            st.markdown('<div class="section-header">Antihypertensive Medication Selection</div>', unsafe_allow_html=True)
            
            st.info("""
            **First-Line Agents for Hypertension:**
            - ACE Inhibitors (ACEi)
            - Angiotensin Receptor Blockers (ARB)
            - Calcium Channel Blockers (CCB)
            - Thiazide/Thiazide-like Diuretics
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Risk Category", risk_category)
                st.metric("Risk Score", f"{risk_score}/20+")
            
            with col2:
                if risk_level == "low":
                    st.success("Low cardiovascular risk")
                elif risk_level == "moderate":
                    st.warning("Moderate cardiovascular risk")
                else:
                    st.error("High cardiovascular risk")
            
            st.markdown("---")
            
            st.markdown("### Comorbidities")
            
            comorbidities = []
            if data.get('diabetes'):
                comorbidities.append("✓ Diabetes Mellitus")
            if data.get('cad'):
                comorbidities.append("✓ Coronary Artery Disease")
            if data.get('cva'):
                comorbidities.append("✓ Cerebrovascular Accident")
            if data.get('ckd'):
                comorbidities.append("✓ Chronic Kidney Disease")
            
            if comorbidities:
                for condition in comorbidities:
                    st.write(condition)
            else:
                st.write("No significant comorbidities reported")
            
            st.markdown("---")
            
            st.markdown("### Risk Factors")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Modifiable Risk Factors:**")
                modifiable = []
                if data.get('smoking'):
                    modifiable.append("• Smoking")
                if data.get('physical_inactivity'):
                    modifiable.append("• Physical inactivity")
                if data.get('bmi', 0) >= 25:
                    modifiable.append(f"• Overweight/Obesity (BMI: {data.get('bmi')})")
                
                if modifiable:
                    for factor in modifiable:
                        st.write(factor)
                else:
                    st.write("None identified")
            
            with col2:
                st.markdown("**Non-Modifiable Risk Factors:**")
                non_modifiable = []
                if data.get('age', 0) >= 55:
                    non_modifiable.append(f"• Age ({data.get('age')} years)")
                if data.get('sex') == "Male":
                    non_modifiable.append("• Male sex")
                
                if non_modifiable:
                    for factor in non_modifiable:
                        st.write(factor)
                else:
                    st.write("None identified")
        
        with tabs[1]:
            st.markdown('<div class="section-header">Detailed Risk Assessment</div>', unsafe_allow_html=True)
            
            risk_score = data.get('risk_score', 0)
            
            st.markdown("### Risk Score Breakdown")
            
            score_components = []
            
            # Age component
            age = data.get('age', 0)
            if age > 65:
                score_components.append(("Age >65 years", 3))
            elif age > 55:
                score_components.append(("Age >55 years", 2))
            elif age > 45:
                score_components.append(("Age >45 years", 1))
            
            # BMI component
            bmi = data.get('bmi', 0)
            if bmi >= 30:
                score_components.append(("Obesity (BMI ≥30)", 2))
            elif bmi >= 25:
                score_components.append(("Overweight (BMI ≥25)", 1))
            
            # Comorbidities
            if data.get('diabetes'):
                score_components.append(("Diabetes Mellitus", 3))
            if data.get('cad'):
                score_components.append(("Coronary Artery Disease", 3))
            if data.get('ckd'):
                score_components.append(("Chronic Kidney Disease", 2))
            if data.get('smoking'):
                score_components.append(("Current Smoking", 2))
            
            # BP component
            bp_class, _ = classify_bp(data.get('systolic', 120), data.get('diastolic', 80))
            if "Crisis" in bp_class:
                score_components.append(("Hypertensive Crisis", 5))
            elif "Stage 2" in bp_class:
                score_components.append(("Stage 2 Hypertension", 3))
            elif "Stage 1" in bp_class:
                score_components.append(("Stage 1 Hypertension", 2))
            
            # Display components
            if score_components:
                risk_df = pd.DataFrame(score_components, columns=['Risk Factor', 'Points'])
                st.dataframe(risk_df, use_container_width=True)
                st.write(f"**Total Risk Score:** {risk_score}")
            
            st.markdown("---")
            
            st.markdown("### Risk Category Interpretation")
            
            risk_category, risk_level = get_risk_category(risk_score)
            
            if risk_level == "low":
                st.markdown('<div class="risk-low">', unsafe_allow_html=True)
                st.markdown("#### Low Risk")
                st.write("""
                - 10-year cardiovascular risk: <10%
                - Continue healthy lifestyle
                - Monitor BP regularly
                - Annual health check-ups
                - Focus on prevention
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            elif risk_level == "moderate":
                st.markdown('<div class="risk-moderate">', unsafe_allow_html=True)
                st.markdown("#### Moderate Risk")
                st.write("""
                - 10-year cardiovascular risk: 10-20%
                - Lifestyle modifications essential
                - May need medication
                - Follow-up every 3-6 months
                - Address modifiable risk factors
                """)
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.markdown('<div class="risk-high">', unsafe_allow_html=True)
                st.markdown("#### High/Very High Risk")
                st.write("""
                - 10-year cardiovascular risk: >20%
                - Medication usually required
                - Intensive lifestyle modifications
                - Close monitoring (monthly initially)
                - May need specialist referral
                - Aggressive treatment targets
                """)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tabs[2]:
            st.markdown('<div class="section-header">Comprehensive Treatment Plan</div>', unsafe_allow_html=True)
            
            st.markdown("### Blood Pressure Management")
            
            systolic = data.get('systolic', 130)
            diastolic = data.get('diastolic', 85)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current BP:**")
                st.metric("Reading", f"{systolic}/{diastolic} mmHg")
            
            with col2:
                st.write("**Target BP:**")
                if data.get('diabetes') or data.get('ckd'):
                    st.metric("Goal", "<130/80 mmHg")
                elif data.get('age', 0) >= 65:
                    st.metric("Goal", "<140/90 mmHg")
                else:
                    st.metric("Goal", "<130/80 mmHg")
            
            st.markdown("---")
            
            st.markdown("### Treatment Recommendations")
            
            st.markdown("#### 1. Pharmacological Treatment")
            
            if systolic >= 140 or diastolic >= 90:
                st.warning("**Medication recommended** - Stage 2 Hypertension")
                st.write("Consider starting with:")
                if data.get('diabetes') or data.get('ckd'):
                    st.write("- ACE Inhibitor or ARB (first choice for renal protection)")
                    st.write("- May add CCB or thiazide diuretic")
                else:
                    st.write("- Any first-line agent (ACEi, ARB, CCB, or thiazide)")
                    st.write("- Consider dual therapy if BP ≥160/100")
            elif systolic >= 130 or diastolic >= 80:
                st.info("**Lifestyle modifications first, consider medication if:**")
                st.write("- High cardiovascular risk")
                st.write("- Target organ damage present")
                st.write("- BP not controlled after 3-6 months of lifestyle changes")
            else:
                st.success("**Lifestyle modifications sufficient at this time**")
            
            st.markdown("---")
            
            st.markdown("#### 2. Lifestyle Modifications")
            
            lifestyle_mods = [
                ("Weight Loss", "Target BMI <25 kg/m²" if data.get('bmi', 0) >= 25 else "Maintain healthy weight", "5-20 mmHg per 10kg loss"),
                ("DASH Diet", "Rich in fruits, vegetables, low-fat dairy", "8-14 mmHg reduction"),
                ("Sodium Reduction", "Limit to <2g/day (ideally <1.5g)", "2-8 mmHg reduction"),
                ("Physical Activity", "150 min/week moderate exercise", "5-8 mmHg reduction"),
                ("Alcohol Moderation", "≤2 drinks/day (men), ≤1 drink/day (women)", "2-4 mmHg reduction"),
                ("Smoking Cessation", "Complete cessation", "Reduces CV risk"),
            ]
            
            lifestyle_df = pd.DataFrame(lifestyle_mods, columns=['Intervention', 'Target', 'BP Reduction'])
            st.dataframe(lifestyle_df, use_container_width=True)
            
            st.markdown("---")
            
            st.markdown("#### 3. Monitoring and Follow-up")
            
            risk_category = data.get('risk_category', 'Moderate Risk')
            
            if "High" in risk_category or "Very High" in risk_category:
                st.write("**High-Risk Follow-up Schedule:**")
                st.write("- Week 2: BP check, medication tolerance")
                st.write("- Week 4: BP check, basic labs (BMP)")
                st.write("- Month 2: BP check, assess response")
                st.write("- Month 3: Comprehensive review")
                st.write("- Ongoing: Every 1-2 months until target achieved")
            else:
                st.write("**Standard Follow-up Schedule:**")
                st.write("- Month 1: BP check, initial labs")
                st.write("- Month 3: Comprehensive review")
                st.write("- Ongoing: Every 3-6 months once stable")
            
            st.markdown("---")
            
            st.markdown("#### 4. Investigations Required")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Baseline Tests:**")
                tests = [
                    "✓ Complete Blood Count (CBC)",
                    "✓ Basic Metabolic Panel (BMP)",
                    "✓ Lipid Profile with Lp(a)",
                    "✓ HbA1c",
                    "✓ Thyroid Function Tests (TSH)",
                    "✓ Urinalysis",
                    "✓ ECG",
                    "✓ Echocardiogram"
                ]
                for test in tests:
                    st.write(test)
            
            with col2:
                st.write("**Additional Tests (if indicated):**")
                additional = [
                    "□ Renal ultrasound with Doppler",
                    "□ 24-hour urine collection",
                    "□ Plasma renin activity",
                    "□ Aldosterone level",
                    "□ Sleep study",
                    "□ Plasma metanephrine",
                    "□ 24-hour urinary cortisol"
                ]
                for test in additional:
                    st.write(test)
            
            st.markdown("---")
            
            st.markdown("#### 5. Patient Education Topics")
            
            education = [
                "Understanding hypertension and its risks",
                "Proper home BP monitoring technique",
                "Medication adherence and timing",
                "Recognizing warning signs and when to seek help",
                "DASH diet principles and meal planning",
                "Safe exercise guidelines",
                "Stress management techniques",
                "Importance of lifestyle modifications"
            ]
            
            for topic in education:
                st.write(f"• {topic}")
        
        with tabs[3]:
            st.markdown('<div class="section-header">Export Options</div>', unsafe_allow_html=True)
            
            st.write("Generate and download comprehensive patient reports:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
                    st.info("PDF generation feature - would generate comprehensive report")
                
                if st.button("📊 Export to Excel", use_container_width=True):
                    st.info("Excel export feature - would export all data tables")
            
            with col2:
                if st.button("📧 Email Report", use_container_width=True):
                    st.info("Email feature - would send report to specified address")
                
                if st.button("🖨️ Print Report", use_container_width=True):
                    st.info("Print feature - would open print dialog")
            
            st.markdown("---")
            
            st.markdown("### Report Summary")
            
            # Create a text summary for download
            report_text = f"""
HYPERTENSION MANAGEMENT REPORT
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

PATIENT INFORMATION
==================
Name: {data.get('patient_name', 'N/A')}
Age: {data.get('age', 'N/A')} years
Sex: {data.get('sex', 'N/A')}
BMI: {data.get('bmi', 'N/A')} kg/m²

VITAL SIGNS
===========
Blood Pressure: {data.get('systolic', 'N/A')}/{data.get('diastolic', 'N/A')} mmHg
Heart Rate: {data.get('hr', 'N/A')} bpm
BP Classification: {classify_bp(data.get('systolic', 120), data.get('diastolic', 80))[0]}

RISK ASSESSMENT
===============
Risk Score: {data.get('risk_score', 0)}/20+
Risk Category: {data.get('risk_category', 'N/A')}

COMORBIDITIES
=============
Diabetes Mellitus: {'Yes' if data.get('diabetes') else 'No'}
Coronary Artery Disease: {'Yes' if data.get('cad') else 'No'}
Chronic Kidney Disease: {'Yes' if data.get('ckd') else 'No'}
Cerebrovascular Accident: {'Yes' if data.get('cva') else 'No'}

RISK FACTORS
============
Smoking: {'Yes' if data.get('smoking') else 'No'}
Physical Inactivity: {'Yes' if data.get('physical_inactivity') else 'No'}
Overweight/Obesity: {'Yes' if data.get('bmi', 0) >= 25 else 'No'}

TREATMENT RECOMMENDATIONS
=========================
1. Lifestyle Modifications:
   - DASH Diet
   - Sodium restriction (<2g/day)
   - Regular exercise (150 min/week)
   - Weight management
   - Stress reduction

2. Pharmacological Treatment:
   - Based on BP level and comorbidities
   - See detailed plan in treatment section

3. Follow-up Schedule:
   - Regular BP monitoring
   - Laboratory tests as indicated
   - Specialist referral if needed

NEXT STEPS
==========
- Complete baseline investigations
- Initiate/adjust treatment plan
- Schedule follow-up appointment
- Begin lifestyle modifications
- Start home BP monitoring

---
This report should be reviewed with a qualified healthcare provider.
            """
            
            st.download_button(
                label="📥 Download Text Report",
                data=report_text,
                file_name=f"hypertension_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.markdown("---")
            
            st.info("""
            **📌 Note:** This system is designed to assist healthcare providers in managing 
            hypertension. All treatment decisions should be made by qualified medical professionals 
            based on individual patient assessment and current clinical guidelines.
            """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Hypertension Management System v1.0</p>
        <p>⚠️ This tool is for healthcare professional use only. Not a substitute for clinical judgment.</p>
        <p>Always follow current clinical guidelines and institutional protocols.</p>
    </div>
""", unsafe_allow_html=True)with col1:
                st.markdown("#### Patient Considerations")
                st.write(f"**Age:** {data.get('age')} years")
                st.write(f"**BP:** {data.get('systolic')}/{data.get('diastolic')} mmHg")
                st.write(f"**BMI:** {data.get('bmi')} kg/m²")
                
                if data.get('diabetes'):
                    st.write("✅ Diabetes Mellitus present")
                if data.get('ckd'):
                    st.write("✅ Chronic Kidney Disease present")
                if data.get('cad'):
                    st.write("✅ Coronary Artery Disease present")
            
            with col2:
                st.markdown("#### Recommended Initial Therapy")
                
                recommendations = []
                
                if data.get('diabetes') or data.get('ckd'):
                    recommendations.append("**ACE Inhibitor or ARB** (renal/cardiac protection)")
                
                if data.get('age', 0) > 55 or data.get('sex') == "Male":
                    recommendations.append("**Calcium Channel Blocker** (effective in older adults)")
                
                if data.get('systolic', 120) >= 160 or data.get('diastolic', 80) >= 100:
                    recommendations.append("**Consider dual therapy** (ACEi/ARB + CCB or Diuretic)")
                
                if not recommendations:
                    recommendations.append("**Start with any first-line agent**")
                
                for rec in recommendations:
                    st.success(rec)
            
            st.markdown("---")
            
            st.markdown("#### Medication Options by Class")
            
            med_class = st.selectbox(
                "Select drug class for details",
                ["ACE Inhibitors", "ARB", "Calcium Channel Blockers", "Diuretics", "Beta Blockers"]
            )
            
            medications = {
                "ACE Inhibitors": {
                    "drugs": ["Lisinopril 5-40mg OD", "Enalapril 5-20mg BD", "Ramipril 2.5-10mg OD", "Perindopril 4-8mg OD"],
                    "indications": "Diabetes, CKD, Heart Failure, Post-MI",
                    "contraindications": "Pregnancy, Bilateral renal artery stenosis, History of angioedema",
                    "side_effects": "Dry cough, Hyperkalemia, Angioedema (rare)",
                    "monitoring": "Creatinine, Potassium at 1-2 weeks"
                },
                "ARB": {
                    "drugs": ["Losartan 50-100mg OD", "Telmisartan 40-80mg OD", "Valsartan 80-320mg OD", "Irbesartan 150-300mg OD"],
                    "indications": "Same as ACEi, alternative if ACEi causes cough",
                    "contraindications": "Pregnancy, Bilateral renal artery stenosis",
                    "side_effects": "Hyperkalemia, Dizziness, Less cough than ACEi",
                    "monitoring": "Creatinine, Potassium at 1-2 weeks"
                },
                "Calcium Channel Blockers": {
                    "drugs": ["Amlodipine 5-10mg OD", "Nifedipine XL 30-60mg OD", "Diltiazem 180-360mg OD"],
                    "indications": "Elderly, Isolated systolic HTN, Angina",
                    "contraindications": "Heart block (diltiazem/verapamil), Heart failure (diltiazem/verapamil)",
                    "side_effects": "Ankle edema, Headache, Flushing, Constipation",
                    "monitoring": "Heart rate (non-dihydropyridines), BP response"
                },
                "Diuretics": {
                    "drugs": ["Hydrochlorothiazide 12.5-25mg OD", "Chlorthalidone 12.5-25mg OD", "Indapamide 1.5-2.5mg OD"],
                    "indications": "Heart failure, Elderly, Volume overload",
                    "contraindications": "Gout, Hyponatremia, Hypokalemia",
                    "side_effects": "Hypokalemia, Hyponatremia, Hyperuricemia, Hyperglycemia",
                    "monitoring": "Electrolytes, Creatinine, Uric acid"
                },
                "Beta Blockers": {
                    "drugs": ["Metoprolol 50-200mg BD", "Atenolol 25-100mg OD", "Bisoprolol 5-10mg OD", "Carvedilol 6.25-25mg BD"],
                    "indications": "Post-MI, Heart failure, Angina, Tachycardia",
                    "contraindications": "Asthma, Bradycardia, Heart block, Peripheral vascular disease",
                    "side_effects": "Bradycardia, Fatigue, Cold extremities, Bronchospasm",
                    "monitoring": "Heart rate, BP, Signs of heart failure"
                }
            }
            
            med_info = medications[med_class]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Common Drugs:**")
                for drug in med_info["drugs"]:
                    st.write(f"- {drug}")
                
                st.markdown("**Indications:**")
                st.write(med_info["indications"])
            
            with col2:
                st.markdown("**Contraindications:**")
                st.write(med_info["contraindications"])
                
                st.markdown("**Common Side Effects:**")
                st.write(med_info["side_effects"])
            
            st.markdown("**Monitoring:**")
            st.write(med_info["monitoring"])
        
        with tabs[1]:
            st.markdown('<div class="section-header">Treatment Goals</div>', unsafe_allow_html=True)
            
            systolic = data.get('systolic', 130)
            diastolic = data.get('diastolic', 85)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Current Blood Pressure")
                st.metric("Systolic", f"{systolic} mmHg")
                st.metric("Diastolic", f"{diastolic} mmHg")
            
            with col2:
                st.markdown("#### Target Blood Pressure")
                
                # Determine target based on patient characteristics
                if data.get('diabetes') or data.get('ckd'):
                    target_sys = 130
                    target_dia = 80
                    st.metric("Target Systolic", f"<{target_sys} mmHg")
                    st.metric("Target Diastolic", f"<{target_dia} mmHg")
                    st.info("Intensive target due to diabetes/CKD")
                elif data.get('age', 0) >= 65:
                    target_sys = 140
                    target_dia = 90
                    st.metric("Target Systolic", f"<{target_sys} mmHg")
                    st.metric("Target Diastolic", f"<{target_dia} mmHg")
                    st.info("Standard target for elderly")
                else:
                    target_sys = 130
                    target_dia = 80
                    st.metric("Target Systolic", f"<{target_sys} mmHg")
                    st.metric("Target Diastolic", f"<{target_dia} mmHg")
                    st.info("Standard target for adults")
            
            st.markdown("---")
            
            st.markdown("#### Timeline for BP Control")
            st.write("""
            - **Initial response:** 2-4 weeks after starting medication
            - **Target achievement:** 3-6 months for most patients
            - **Resistant HTN:** May require 6-12 months with multiple agents
            """)
            
            st.markdown("#### Additional Treatment Goals")
            
            goals = []
            
            if data.get('bmi', 0) >= 25:
                goals.append(f"🎯 Weight reduction: Target BMI <25 kg/m² (Current: {data.get('bmi')} kg/m²)")
            
            if data.get('diabetes'):
                goals.append("🎯 HbA1c <7% for most patients")
            
            if data.get('smoking'):
                goals.append("🎯 Complete smoking cessation")
            
            goals.append("🎯 LDL cholesterol <100 mg/dL (or <70 if very high risk)")
            goals.append("🎯 Regular physical activity: 150 min/week moderate intensity")
            goals.append("🎯 Sodium intake <2g/day")
            
            for goal in goals:
                st.write(goal)
        
        with tabs[2]:
            st.markdown('<div class="section-header">Monitoring and Follow-up Plan</div>', unsafe_allow_html=True)
            
            st.markdown("#### Follow-up Schedule")
            
            risk_category = data.get('risk_category', 'Moderate Risk')
            
            if "Very High" in risk_category or "High" in risk_category:
                st.warning("**High/Very High Risk Patient** - Intensive monitoring required")
                st.write("- Week 2: Check BP, review medication tolerance")
                st.write("- Week 4: BP check, labs (Creatinine, K+, Na+)")
                st.write("- Month 2: BP check, assess for side effects")
                st.write("- Month 3: Comprehensive assessment, adjust therapy")
                st.write("- Then: Every 1-2 months until target achieved")
                st.write("- Maintenance: Every 3-4 months once stable")
            else:
                st.success("**Low/Moderate Risk Patient** - Standard monitoring")
                st.write("- Week 4: BP check, initial labs")
                st.write("- Month 2: BP check, assess tolerance")
                st.write("- Month 3: Comprehensive review")
                st.write("- Then: Every 2-3 months until target achieved")
                st.write("- Maintenance: Every 4-6 months once stable")
            
            st.markdown("---")
            
            st.markdown("#### Laboratory Monitoring")
            
            labs_df = pd.DataFrame({
                'Test': ['Basic Metabolic Panel', 'Lipid Profile', 'HbA1c', 'Urinalysis', 'ECG', 'Echocardiogram'],
                'Baseline': ['✓', '✓', '✓', '✓', '✓', '✓'],
                '1-2 weeks': ['✓', '', '', '', '', ''],
                '3 months': ['✓', '✓', '✓ (if DM)', '✓', '', ''],
                'Annually': ['✓', '✓', '✓ (if DM)', '✓', '✓', 'As needed']
            })
            
            st.dataframe(labs_df, use_container_width=True)
            
            st.markdown("---")
            
            st.markdown("#### Home Blood Pressure Monitoring")
            
            st.info("""
            **Recommended Home BP Monitoring Protocol:**
            - Measure BP twice daily (morning and evening)
            - Take 2 readings each time, 1 minute apart
            - Record all readings in a log
            - Average readings over 7 days
            - Bring log to each appointment
            
            **Target:** <135/85 mmHg at home (typically 5-10 mmHg lower than clinic)
            """)
            
            st.markdown("#### Red Flags - When to Seek Immediate Care")
            
            st.error("""
            Contact healthcare provider immediately if:
            - BP >180/120 mmHg
            - Severe headache
            - Chest pain
            - Shortness of breath
            - Vision changes
            - Severe dizziness
            - Numbness or weakness
            """)

# DIET ADVICE PAGE
elif page == "Diet Advice":
    st.markdown('<h1 class="main-header">🥗 Diet and Nutrition Advice</h1>', unsafe_allow_html=True)
    
    tabs = st.tabs(["DASH Diet", "Meal Planning", "Foods to Limit", "Sample Meal Plan"])
    
    with tabs[0]:
        st.markdown('<div class="section-header">DASH Diet (Dietary Approaches to Stop Hypertension)</div>', unsafe_allow_html=True)
        
        st.success("""
        The DASH diet has been proven to lower blood pressure by 8-14 mmHg. 
        It emphasizes fruits, vegetables, whole grains, and lean proteins while limiting sodium, 
        saturated fats, and added sugars.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Daily Recommendations")
            
            dash_recommendations = pd.DataFrame({
                'Food Group': [
                    'Grains (whole grain)',
                    'Vegetables',
                    'Fruits',
                    'Low-fat dairy',
                    'Lean meat, poultry, fish',
                    'Nuts, seeds, legumes',
                    'Fats and oils',
                    'Sweets'
                ],
                'Servings/Day': [
                    '6-8',
                    '4-5',
                    '4-5',
                    '2-3',
                    '≤6 oz',
                    '4-5 per week',
                    '2-3',
                    '≤5 per week'
                ],
                'Examples': [
                    '1 slice bread, 1/2 cup rice',
                    '1 cup raw leafy vegetables',
                    '1 medium fruit, 1/2 cup juice',
                    '1 cup milk or yogurt',
                    '3 oz cooked meat',
                    '1/3 cup nuts, 1/2 cup beans',
                    '1 tsp oil or butter',
                    '1 tbsp sugar or jam'
                ]
            })
            
            st.dataframe(dash_recommendations, use_container_width=True)
        
        with col2:
            st.markdown("#### Key Nutrients in DASH Diet")
            
            nutrients = {
                'Potassium': '4,700 mg/day - Helps counteract sodium effects',
                'Calcium': '1,250 mg/day - Supports BP regulation',
                'Magnesium': '500 mg/day - Relaxes blood vessels',
                'Fiber': '30 g/day - Improves heart health',
                'Sodium': '<2,000 mg/day - Ideally <1,500 mg/day'
            }
            
            for nutrient, info in nutrients.items():
                st.write(f"**{nutrient}:** {info}")
        
        st.markdown("---")
        
        st.markdown("#### Benefits of DASH Diet")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**Lowers BP**\n\n8-14 mmHg reduction in 2-8 weeks")
        
        with col2:
            st.info("**Weight Loss**\n\nPromotes healthy weight management")
        
        with col3:
            st.info("**Heart Health**\n\nReduces cardiovascular risk")
    
    with tabs[1]:
        st.markdown('<div class="section-header">Meal Planning Guidelines</div>', unsafe_allow_html=True)
        
        st.markdown("#### Sodium Reduction Strategies")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ DO:**")
            tips_do = [
                "Use fresh ingredients",
                "Cook at home more often",
                "Use herbs and spices for flavor",
                "Read nutrition labels",
                "Choose 'no salt added' products",
                "Rinse canned vegetables",
                "Use lemon, garlic, onion for seasoning",
                "Try salt-free seasoning blends"
            ]
            for tip in tips_do:
                st.write(f"✓ {tip}")
        
        with col2:
            st.markdown("**❌ AVOID:**")
            tips_avoid = [
                "Processed and packaged foods",
                "Canned soups and broths",
                "Deli meats and hot dogs",
                "Frozen dinners",
                "Salty snacks (chips, pretzels)",
                "Pickles and olives",
                "Soy sauce and teriyaki",
                "Fast food and restaurant meals"
            ]
            for tip in tips_avoid:
                st.write(f"✗ {tip}")
        
        st.markdown("---")
        
        st.markdown("#### Portion Control")
        
        portion_guide = pd.DataFrame({
            'Food': ['Meat/Protein', 'Rice/Pasta', 'Vegetables', 'Fruit', 'Cheese', 'Nuts'],
            'Serving Size': ['3 oz (deck of cards)', '1/2 cup (tennis ball)', '1 cup (baseball)', '1 medium (tennis ball)', '1.5 oz (4 dice)', '1/3 cup (golf ball)'],
            'Visual Guide': ['🎴', '🎾', '⚾', '🎾', '🎲', '⛳']
        })
        
        st.dataframe(portion_guide, use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("#### Grocery Shopping Tips")
        
        st.info("""
        **Smart Shopping:**
        1. Shop the perimeter of the store (fresh foods)
        2. Make a list and stick to it
        3. Read labels - look for sodium content
        4. Choose frozen vegetables without added salt
        5. Buy lean cuts of meat
        6. Select whole grain products
        7. Avoid items with >400mg sodium per serving
        8. Choose products with <5% Daily Value of sodium
        """)
    
    with tabs[2]:
        st.markdown('<div class="section-header">Foods to Limit or Avoid</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### High Sodium Foods")
            
            high_sodium = [
                "**Processed meats:** bacon, sausage, ham, deli meats",
                "**Canned foods:** soups, vegetables with salt",
                "**Frozen meals:** TV dinners, frozen pizza",
                "**Snack foods:** chips, pretzels, crackers",
                "**Condiments:** soy sauce, ketchup, BBQ sauce",
                "**Cheese:** especially processed cheese",
                "**Pickled foods:** pickles, sauerkraut, olives",
                "**Fast food:** burgers, fries, fried chicken"
            ]
            
            for item in high_sodium:
                st.write(f"🔴 {item}")
        
        with col2:
            st.markdown("#### Other Foods to Limit")
            
            limit_foods = [
                "**Saturated fats:** fatty meats, butter, full-fat dairy",
                "**Trans fats:** margarine, fried foods, baked goods",
                "**Added sugars:** soda, candy, desserts",
                "**Alcohol:** >2 drinks/day (men), >1 drink/day (women)",
                "**Caffeine:** excessive coffee consumption",
                "**Red meat:** limit to 2-3 times per week",
                "**Refined carbs:** white bread, white rice",
                "**High-cholesterol foods:** egg yolks (in excess)"
            ]
            
            for item in limit_foods:
                st.write(f"🟡 {item}")
        
        st.markdown("---")
        
        st.markdown("#### Alcohol Guidelines")
        
        st.warning("""
        **Moderate Alcohol Consumption:**
        - Men: ≤2 standard drinks per day
        - Women: ≤1 standard drink per day
        
        **One standard drink equals:**
        - 12 oz beer (5% alcohol)
        - 5 oz wine (12% alcohol)
        - 1.5 oz spirits (40% alcohol)
        
        ⚠️ Excessive alcohol can raise blood pressure and interfere with medications.
        """)
    
    with tabs[3]:
        st.markdown('<div class="section-header">Sample 7-Day DASH Meal Plan</div>', unsafe_allow_html=True)
        
        day = st.selectbox("Select Day", ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"])
        
        meal_plans = {
            "Day 1": {
                "Breakfast": "Oatmeal with berries, banana, almonds | 1 cup low-fat milk | Herbal tea",
                "Snack": "Apple slices with 1 tbsp almond butter",
                "Lunch": "Grilled chicken salad with mixed greens, tomatoes, cucumbers | Olive oil vinaigrette | Whole wheat roll",
                "Snack": "1 cup low-fat yogurt with walnuts",
                "Dinner": "Baked salmon (3 oz) | Quinoa (1/2 cup) | Steamed broccoli | Side salad",
                "Sodium": "~1,800 mg",
                "Calories": "~2,000"
            },
            "Day 2": {
                "Breakfast": "Whole wheat toast with avocado | Scrambled egg whites | Orange juice",
                "Snack": "Handful of unsalted mixed nuts",
                "Lunch": "Turkey sandwich on whole grain bread | Lettuce, tomato | Baby carrots | Fruit",
                "Snack": "Low-fat cottage cheese with pineapple",
                "Dinner": "Grilled chicken breast | Brown rice | Sautéed spinach with garlic | Mixed vegetables",
                "Sodium": "~1,700 mg",
                "Calories": "~1,950"
            },
            "Day 3": {
                "Breakfast": "Greek yogurt parfait with granola and berries | Green tea",
                "Snack": "Pear and string cheese",
                "Lunch": "Lentil soup (low-sodium) | Whole grain crackers | Side salad",
                "Snack": "Celery sticks with hummus",
                "Dinner": "Lean beef stir-fry with vegetables | Brown rice | Fortune cookie",
                "Sodium": "~1,850 mg",
                "Calories": "~2,050"
            },
            "Day 4": {
                "Breakfast": "Smoothie: banana, spinach, berries, low-fat milk, flax seeds",
                "Snack": "Orange and almonds",
                "Lunch": "Tuna salad (made with low-fat mayo) on whole wheat | Vegetable soup",
                "Snack": "Air-popped popcorn (unsalted)",
                "Dinner": "Baked tilapia | Sweet potato | Green beans | Whole grain roll",
                "Sodium": "~1,750 mg",
                "Calories": "~1,900"
            },
            "Day 5": {
                "Breakfast": "Whole grain cereal with low-fat milk | Banana | Coffee",
                "Snack": "Trail mix (unsalted nuts and dried fruit)",
                "Lunch": "Chicken and vegetable wrap | Apple | Low-fat yogurt",
                "Snack": "Cucumber slices with tzatziki",
                "Dinner": "Turkey meatballs with marinara | Whole wheat pasta | Caesar salad (light dressing)",
                "Sodium": "~1,800 mg",
                "Calories": "~2,000"
            },
            "Day 6": {
                "Breakfast": "Veggie omelet with tomatoes, peppers, mushrooms | Whole wheat toast | Orange",
                "Snack": "Low-fat milk and graham crackers",
                "Lunch": "Quinoa Buddha bowl: chickpeas, vegetables, avocado, tahini dressing",
                "Snack": "Grapes and cheese",
                "Dinner": "Grilled pork tenderloin | Roasted Brussels sprouts | Wild rice | Side salad",
                "Sodium": "~1,700 mg",
                "Calories": "~1,950"
            },
            "Day 7": {
                "Breakfast": "Whole grain pancakes with fresh berries | Low-fat yogurt",
                "Snack": "Peach and handful of walnuts",
                "Lunch": "Minestrone soup | Whole grain bread | Mixed green salad",
                "Snack": "Carrot sticks with guacamole",
                "Dinner": "Herb-roasted chicken | Mashed cauliflower | Roasted vegetables | Dinner roll",
                "Sodium": "~1,750 mg",
                "Calories": "~1,900"
            }
        }
        
        selected_plan = meal_plans[day]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Meals")
            
            for meal, details in selected_plan.items():
                if meal not in ['Sodium', 'Calories']:
                    with st.expander(f"**{meal}**"):
                        st.write(details)
        
        with col2:
            st.markdown("### Daily Totals")
            st.metric("Sodium", selected_plan['Sodium'])
            st.metric("Calories", selected_plan['Calories'])
            
            st.markdown("---")
            
            st.info("""
            **💡 Tips:**
            - Drink 8 glasses of water daily
            - Prepare meals ahead
            - Use meal prep containers
            - Keep healthy snacks ready
            """)

# EXERCISE PLAN PAGE
elif page == "Exercise Plan":
    st.markdown('<h1 class="main-header">🏃 Exercise and Physical Activity Plan</h1>', unsafe_allow_html=True)
    
    tabs = st.tabs(["Exercise Guidelines", "Weekly Plan", "Safety Tips", "Progress Tracking"])
    
    with tabs[0]:
        st.markdown('<div class="section-header">Exercise Benefits for Hypertension</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("**Lowers BP**\n\n5-8 mmHg reduction")
        
        with col2:
            st.success("**Weight Loss**\n\nBurns calories")
        
        with col3:
            st.success("**Heart Health**\n\nStrengthens cardiovascular system")
        
        st.markdown("---")
        
        st.markdown("#### Recommended Exercise Guidelines")
        
        st.info("""
        **American Heart Association Recommendations:**
        
        **Aerobic Exercise:**
        - At least 150 minutes per week of moderate-intensity OR
        - 75 minutes per week of vigorous-intensity
        - Spread throughout the week (e.g., 30 min × 5 days)
        
        **Strength Training:**
        - At least 2 days per week
        - Work all major muscle groups
        - 2-3 sets of 8-12 repetitions
        
        **Flexibility & Balance:**
        - Daily stretching
        - Yoga or tai chi 2-3 times per week
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Moderate-Intensity Activities")
            
            moderate_activities = [
                "Brisk walking (3-4 mph)",
                "Water aerobics",
                "Recreational swimming",
                "Ballroom dancing",
                "Gardening",
                "Tennis (doubles)",
                "Cycling on level terrain (<10 mph)",
                "Light yard work"
            ]
            
            for activity in moderate_activities:
                st.write(f"✓ {activity}")
        
        with col2:
            st.markdown("#### Vigorous-Intensity Activities")
            
            vigorous_activities = [
                "Jogging or running",
                "Swimming laps",
                "Aerobics classes",
                "Tennis (singles)",
                "Cycling fast (>10 mph)",
                "Basketball",
                "Jump rope",
                "Hiking uphill"
            ]
            
            for activity in vigorous_activities:
                st.write(f"✓ {activity}")
        
        st.markdown("---")
        
        st.markdown("#### Understanding Exercise Intensity")
        
        intensity_guide = pd.DataFrame({
            'Intensity': ['Light', 'Moderate', 'Vigorous'],
            'Heart Rate (% of Max)': ['<50%', '50-70%', '70-85%'],
            'Talk Test': ['Can sing', 'Can talk, not sing', 'Can say few words'],
            'Breathing': ['Normal', 'Slightly breathless', 'Quite breathless'],
            'RPE (1-10 scale)': ['2-3', '4-6', '7-8']
        })
        
        st.dataframe(intensity_guide, use_container_width=True)
        
        if st.session_state.patient_data:
            age = st.session_state.patient_data.get('age', 50)
            max_hr = 220 - age
            target_min = int(max_hr * 0.5)
            target_max = int(max_hr * 0.85)
            
            st.info(f"""
            **Your Target Heart Rate Zones (Age {age}):**
            - Maximum Heart Rate: {max_hr} bpm
            - Moderate Intensity: {target_min}-{int(max_hr * 0.7)} bpm
            - Vigorous Intensity: {int(max_hr * 0.7)}-{target_max} bpm
            """)
    
    with tabs[1]:
        st.markdown('<div class="section-header">Sample Weekly Exercise Plan</div>', unsafe_allow_html=True)
        
        fitness_level = st.selectbox(
            "Select Your Current Fitness Level",
            ["Beginner", "Intermediate", "Advanced"]
        )
        
        beginner_plan = {
            'Monday': '20 min brisk walk | 10 min stretching',
            'Tuesday': 'Rest or gentle yoga (15 min)',
            'Wednesday': '20 min brisk walk | Light strength training (15 min)',
            'Thursday': 'Rest or gentle stretching',
            'Friday': '25 min brisk walk | 10 min stretching',
            'Saturday': 'Light strength training (20 min) | Stretching',
            'Sunday': 'Rest or leisure walk (15-20 min)'
        }
        
        intermediate_plan = {
            'Monday': '30 min brisk walk/jog | Core exercises (10 min)',
            'Tuesday': 'Strength training - Upper body (30 min)',
            'Wednesday': '40 min cycling or swimming | Stretching (10 min)',
            'Thursday': 'Strength training - Lower body (30 min)',
            'Friday': '35 min aerobic exercise | Core work (10 min)',
            'Saturday': 'Full body strength training (35 min) | Yoga',
            'Sunday': 'Active recovery: light walk or yoga (30 min)'
        }
        
        advanced_plan = {
            'Monday': '45 min run or high-intensity interval training | Core',
            'Tuesday': 'Strength training - Upper body (45 min)',
            'Wednesday': '60 min cycling, swimming, or aerobics class',
            'Thursday': 'Strength training - Lower body (45 min)',
            'Friday': '50 min run or HIIT workout | Core exercises',
            'Saturday': 'Full body strength circuit (50 min) | Flexibility',
            'Sunday': 'Active recovery: yoga, swimming, or light cardio (40 min)'
        }
        
        plans = {
            'Beginner': beginner_plan,
            'Intermediate': intermediate_plan,
            'Advanced': advanced_plan
        }
        
        selected_plan = plans[fitness_level]
        
        for day, workout in selected_plan.items():
            with st.expander(f"**{day}**"):
                st.write(workout)
        
        st.markdown("---")
        
        st.markdown("#### Progression Guidelines")
        
        if fitness_level == "Beginner":
            st.info("""
            **Getting Started:**
            - Start with 10-15 minutes if needed
            - Increase duration by 5 minutes each week
            - Focus on consistency over intensity
            - Listen to your body
            - Aim to reach 30 minutes per session by week 6-8
            """)
        elif fitness_level == "Intermediate":
            st.info("""
            **Building Endurance:**
            - Increase intensity gradually
            - Add interval training 1-2x per week
            - Increase weights by 5-10% when comfortable
            - Vary activities to prevent boredom
            - Challenge yourself but avoid overtraining
            """)
        else:
            st.info("""
            **Advanced Training:**
            - Periodize your training
            - Incorporate HIIT 2-3x per week
            - Focus on progressive overload
            - Include sport-specific training
            - Ensure adequate recovery
            """)
    
    with tabs[2]:
        st.markdown('<div class="section-header">Safety Guidelines</div>', unsafe_allow_html=True)
        
        st.error("""
        **⚠️ When to Stop Exercising Immediately:**
        - Chest pain or pressure
        - Severe shortness of breath
        - Dizziness or lightheadedness
        - Irregular or rapid heartbeat
        - Nausea
        - Cold sweat
        - Pain in jaw, neck, or arm
        
        If you experience any of these, stop and seek medical attention.
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Before Exercise")
            
            st.success("""
            **Pre-Exercise Checklist:**
            ✓ Check blood pressure if available
            ✓ Take medications as prescribed
            ✓ Stay hydrated (drink water)
            ✓ Wear comfortable clothing
            ✓ Wear proper footwear
            ✓ Warm up for 5-10 minutes
            ✓ Have medical ID if needed
            """)
        
        with col2:
            st.markdown("#### After Exercise")
            
            st.success("""
            **Post-Exercise Care:**
            ✓ Cool down for 5-10 minutes
            ✓ Stretch major muscle groups
            ✓ Rehydrate adequately
            ✓ Monitor how you feel
            ✓ Record your activity
            ✓ Rest and recover
            """)
        
        st.markdown("---")
        
        st.markdown("#### Special Considerations")
        
        st.warning("""
        **If you have hypertension:**
        - Avoid heavy lifting or straining (Valsalva maneuver)
        - Don't hold your breath during exercise
        - Avoid exercises where head is below heart for extended periods
        - Be cautious with hot weather exercise
        - Stay well hydrated
        - Monitor blood pressure before and after exercise initially
        
        **Medication considerations:**
        - Beta blockers may lower your heart rate - use RPE instead
        - Some medications may cause dizziness - stand up slowly
        - Diuretics may increase fluid loss - hydrate well
        
        **Get medical clearance if:**
        - BP >180/110 mmHg (wait until controlled)
        - Recent heart attack or procedure
        - Unstable angina
        - Uncontrolled diabetes
        - Starting vigorous exercise program
        """)
    
    with tabs[3]:
        st.markdown('<div class="section-header">Progress Tracking</div>', unsafe_allow_html=True)
        
        st.write("Use this section to log and track your exercise progress:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            exercise_date = st.date_input("Date")
            activity_type = st.selectbox("Activity", 
                ["Walking", "Jogging", "Cycling", "Swimming", "Strength Training", 
                 "Yoga", "Dancing", "Sports", "Other"])
        
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=180, value=30)
            intensity = st.selectbox("Intensity", ["Light", "Moderate", "Vigorous"])
        
        with col3:
            how_felt = st.selectbox("How did you feel?", 
                ["Great", "Good", "Fair", "Tired", "Difficult"])
            bp_before = st.text_input("BP before (optional)", placeholder="120/80")
        
        notes = st.text_area("Notes", placeholder="Any observations or comments...")
        
        if st.button("Log Exercise Session"):
            st.success("✅ Exercise session logged successfully!")
        
        st.markdown("---")
        
        st.markdown("#### Weekly Summary</div>")
        
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("This Week", "120 min", "30 min")
        
        with summary_col2:
            st.metric("Sessions", "4", "1")
        
        with summary_col3:
            st.metric("Goal Progress", "80%", "20%")
        
        with summary_col4:
            st.metric("Calories Burned", "~600", "~150")
        
        st.info("💡 **Tip:** Consistency is key! Aim for at least 150 minutes of moderate activity per week.")

# REPORTS PAGE
elif page == "Reports":
    st.markdown('<h1 class="main-header">📊 Patient Reports</h1>', unsafe_allow_html=True)
    
    if not st.session_state.patient_data:
        st.warning("⚠️ No patient data available. Please complete the Patient Assessment first.")
    else:
        data = st.session_state.patient_data
        
        tabs = st.tabs(["Summary Report", "Risk Assessment", "Treatment Plan", "Export"])
        
        with tabs[0]:
            st.markdown('<div class="section-header">Patient Summary Report</div>', unsafe_allow_html=True)
            
            st.write(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
            st.write(f"**Assessment Date:** {data.get('assessment_date', 'N/A')}")
            
            st.markdown("---")
            
            st.markdown("### Patient Information")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**Name:** {data.get('patient_name', 'N/A')}")
                st.write(f"**Age:** {data.get('age', 'N/A')} years")
            
            with col2:
                st.write(f"**Sex:** {data.get('sex', 'N/A')}")
                st.write(f"**BMI:** {data.get('bmi', 'N/A')} kg/m²")
            
            with col3:
                st.write(f"**BP:** {data.get('systolic', 'N/A')}/{data.get('diastolic', 'N/A')} mmHg")
                st.write(f"**HR:** {data.get('hr', 'N/A')} bpm")
            
            with col4:
                bp_class, _ = classify_bp(data.get('systolic', 120), data.get('diastolic', 80))
                st.write(f"**BP Class:** {bp_class}")
                st.write(f"**HTN Duration:** {data.get('duration_htn', 0)} years")
            
            st.markdown("---")
            
            st.markdown("### Cardiovascular Risk Assessment")
            
            risk_score = data.get('risk_score', 0)
            risk_category, risk_level = get_risk_category(risk_score)
            
            col1, col2 = st.columns(2)
