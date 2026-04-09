# RxCheck — AI-Powered Drug Interaction Checker

## Live Demo
Try it here: [rxcheck.streamlit.app](https://rxcheck.streamlit.app)

## The Problem
Clinicians and pharmacists managing patients on multiple medications face a real risk of harmful drug interactions. Checking interactions manually is time-consuming, inconsistent, and often fails to account for patient-specific factors like kidney function, ethnicity, or comorbidities that significantly affect drug metabolism and risk.

## The Product
RxCheck is an AI-powered drug interaction checker built for clinical and pharma environments. It takes a list of medications and a structured patient profile, and returns a plain-language interaction report with severity classification, pairwise analysis, patient-specific risks, and actionable recommendations.

## Key Product Decisions
- **Structured patient intake over free text** — replaced an open text field with discrete clinical fields (age, sex, ethnicity, weight, kidney function, liver function, pregnancy status, allergies) to improve data completeness and analysis consistency
- **Patient-specific analysis** — the AI factors in the full patient profile, not just the drugs in isolation, producing recommendations tailored to that patient's clinical context
- **Severity classification** — interactions are classified as None / Mild / Moderate / Severe with colour-coded output for fast clinical triage
- **Plain language output** — findings are written for clinicians and non-technical users, not just pharmacists

## Features
- Multi-drug interaction checking (2+ medications)
- Pairwise interaction analysis with mechanism, clinical effect, and recommendation per pair
- Overall risk banner with severity score
- Patient-specific risk flags
- Monitoring parameters
- Medical disclaimer built in

## Tech Stack
HTML, CSS, JavaScript, Claude AI API (claude-sonnet)


## Target Users
Pharmacists, clinicians, and pharma teams who need fast, patient-contextualised drug interaction checks in regulated healthcare environments.
