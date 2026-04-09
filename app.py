import streamlit as st
import anthropic
import json

st.set_page_config(
    page_title="RxCheck — Drug Interaction Checker",
    page_icon="💊",
    layout="centered"
)

st.markdown("""
<style>
    .brand { font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: #888780; margin-bottom: 4px; }
    .severity-severe { background-color: #FCEBEB; border: 1px solid #F7C1C1; border-radius: 8px; padding: 16px; margin-bottom: 16px; color: #7F1D1D; }
    .severity-moderate { background-color: #FAEEDA; border: 1px solid #FAC775; border-radius: 8px; padding: 16px; margin-bottom: 16px; color: #78350F; }
    .severity-mild { background-color: #E6F1FB; border: 1px solid #B5D4F4; border-radius: 8px; padding: 16px; margin-bottom: 16px; color: #1E3A5F; }
    .severity-none { background-color: #EAF3DE; border: 1px solid #C0DD97; border-radius: 8px; padding: 16px; margin-bottom: 16px; color: #1A3A0F; }
    .pair-card { background-color: #1E1E1E; border: 1px solid #444; border-radius: 8px; padding: 16px; margin-bottom: 12px; color: #F0F0F0; }
    .disclaimer { font-size: 12px; color: #888780; background-color: #F1EFE8; border: 1px solid #D3D1C7; border-radius: 6px; padding: 12px; margin-top: 16px; }
    div[data-testid="stForm"] { border: none; padding: 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="brand">RxCheck</p>', unsafe_allow_html=True)
st.title("Drug Interaction Checker")
st.markdown("Enter medications and patient details to check for interactions, understand the risks, and get plain-language clinical guidance.")

st.divider()

# STEP 1 - MEDICATIONS
st.subheader("Step 1 — Medications")
st.caption("Enter all medications the patient is currently taking.")

if "drug_count" not in st.session_state:
    st.session_state.drug_count = 2

drugs = []
for i in range(st.session_state.drug_count):
    drug = st.text_input(f"Medication {i+1}", key=f"drug_{i}", placeholder="e.g. Warfarin")
    if drug.strip():
        drugs.append(drug.strip())

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("+ Add"):
        st.session_state.drug_count += 1
        st.rerun()

st.divider()

# STEP 2 - PATIENT PROFILE
st.subheader("Step 2 — Patient Profile")
st.caption("Complete patient details improve the accuracy and relevance of the analysis.")

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age *", min_value=0, max_value=120, value=None, placeholder="e.g. 67")
with col2:
    sex = st.selectbox("Biological sex *", ["", "Male", "Female", "Intersex", "Prefer not to say"])

col1, col2 = st.columns(2)
with col1:
    ethnicity = st.selectbox("Ethnicity / Race", [
        "", "White / Caucasian", "Black / African American", "Hispanic / Latino",
        "East Asian", "South Asian", "Southeast Asian", "Indigenous / First Nations",
        "Middle Eastern / North African", "Mixed ethnicity", "Prefer not to say"
    ])
with col2:
    weight = st.text_input("Weight", placeholder="e.g. 72 kg or 158 lbs")

conditions = st.text_input("Existing medical conditions *", placeholder="e.g. Atrial fibrillation, Type 2 diabetes, hypertension")

col1, col2 = st.columns(2)
with col1:
    kidney = st.selectbox("Kidney function", [
        "Unknown / Not tested", "Normal (eGFR >60)", "Mild impairment (eGFR 45-60)",
        "Moderate impairment (eGFR 30-44)", "Severe impairment (eGFR <30)", "End-stage renal disease"
    ])
with col2:
    liver = st.selectbox("Liver function", [
        "Unknown / Not tested", "Normal", "Mild impairment (Child-Pugh A)",
        "Moderate impairment (Child-Pugh B)", "Severe impairment (Child-Pugh C)"
    ])

col1, col2 = st.columns(2)
with col1:
    pregnancy = st.selectbox("Pregnancy status", [
        "Not applicable / Unknown", "Not pregnant", "Pregnant — 1st trimester",
        "Pregnant — 2nd trimester", "Pregnant — 3rd trimester", "Breastfeeding"
    ])
with col2:
    allergies = st.text_input("Known allergies", placeholder="e.g. Penicillin, sulfa drugs")

extra = st.text_input("Additional context", placeholder="e.g. Post-surgery, undergoing chemotherapy")

st.divider()

# VALIDATION & SUBMIT
ready = len(drugs) >= 2 and age and sex and conditions.strip()

if not ready:
    st.caption("Please enter at least 2 medications, age, sex, and existing conditions to continue.")

if st.button("Generate Interaction Report", disabled=not ready, type="primary", use_container_width=True):

    patient_parts = []
    if age: patient_parts.append(f"age {age}")
    if sex: patient_parts.append(f"sex: {sex}")
    if ethnicity: patient_parts.append(f"ethnicity: {ethnicity}")
    if weight: patient_parts.append(f"weight: {weight}")
    if conditions: patient_parts.append(f"conditions: {conditions}")
    if kidney != "Unknown / Not tested": patient_parts.append(f"kidney function: {kidney}")
    if liver != "Unknown / Not tested": patient_parts.append(f"liver function: {liver}")
    if pregnancy != "Not applicable / Unknown": patient_parts.append(f"pregnancy: {pregnancy}")
    if allergies: patient_parts.append(f"allergies: {allergies}")
    if extra: patient_parts.append(f"additional context: {extra}")
    patient_str = ", ".join(patient_parts)

    prompt = f"""You are a senior clinical pharmacist. Analyze drug interactions for the following:

Medications: {", ".join(drugs)}
Patient: {patient_str}

Return ONLY valid JSON, no markdown, no extra text:
{{"overallSeverity":"<None|Mild|Moderate|Severe>","overallSummary":"<2-3 sentence plain-language summary tailored to this specific patient>","pairs":[{{"drug1":"<name>","drug2":"<name>","severity":"<None|Mild|Moderate|Severe>","mechanism":"<plain English explanation, 1-2 sentences>","clinicalEffect":"<what happens to this patient considering their profile, 1-2 sentences>","recommendation":"<specific action, 1-2 sentences>"}}],"patientSpecificRisks":["<risk 1>","<risk 2>","<risk 3>"],"recommendations":["<rec 1>","<rec 2>","<rec 3>","<rec 4>"],"monitoringParams":["<monitor 1>","<monitor 2>","<monitor 3>"]}}"""

    with st.spinner("Analyzing interactions..."):
        try:
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = message.content[0].text.replace("```json", "").replace("```", "").strip()
            result = json.loads(raw)

            # RESULTS
            st.divider()
            st.subheader("Interaction Report")
            st.caption(f"Checking: {', '.join(drugs)}")

            sev = result.get("overallSeverity", "Unknown")
            sev_class = sev.lower() if sev.lower() in ["severe", "moderate", "mild", "none"] else "none"
            sev_icons = {"severe": "⚠️", "moderate": "◆", "mild": "●", "none": "✓"}
            icon = sev_icons.get(sev_class, "●")

            st.markdown(f'<div class="severity-{sev_class}"><strong>{icon} Overall Risk: {sev}</strong><br><br>{result.get("overallSummary", "")}</div>', unsafe_allow_html=True)

            st.subheader("Pairwise Analysis")
            for pair in result.get("pairs", []):
                ps = pair.get("severity", "")
                with st.container():
                    st.markdown(f'<div class="pair-card"><strong>{pair.get("drug1")} + {pair.get("drug2")}</strong> &nbsp;&nbsp; <code>{ps}</code><br><br><strong>Why they interact:</strong> {pair.get("mechanism", "")}<br><br><strong>Clinical effect:</strong> {pair.get("clinicalEffect", "")}<br><br><strong>What to do:</strong> {pair.get("recommendation", "")}</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Recommendations")
                for rec in result.get("recommendations", []):
                    st.markdown(f"→ {rec}")

            with col2:
                st.subheader("What to Monitor")
                for m in result.get("monitoringParams", []):
                    st.markdown(f"● {m}")

            st.subheader("Patient-Specific Risks")
            for risk in result.get("patientSpecificRisks", []):
                st.warning(risk)

            st.markdown('<div class="disclaimer">⚕ RxCheck is for informational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional or pharmacist before making any medication decisions.</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error("Something went wrong generating the analysis. Please try again.")
