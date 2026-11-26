"""Taxonomy và trọng số cho nhóm ngành Y tế & Sức khỏe (Healthcare, Nursing, Medical, Fitness)."""

HEALTHCARE_TAXONOMY = {
    "clinical_and_patient_care": {
        "Patient Care & Assessment": ["patient care", "patient assessment", "vital signs", "triage", "chăm sóc bệnh nhân"],
        "Nursing & Clinical": ["nursing", "clinical", "registered nurse", "bedside", "điều dưỡng", "lâm sàng"],
        "Medical Terminology": ["medical terminology", "diagnosis", "treatment plan", "chẩn đoán", "thuật ngữ y khoa"],
        "Medication & Pharmacy": ["medication", "medications", "pharmacy", "pharmacology", "dispensing", "dược phẩm", "thuốc"],
        "Emergency & CPR": ["cpr", "first aid", "bls", "acls", "emergency", "sơ cứu", "cấp cứu"],
        "Wellness & Rehabilitation": ["wellness", "fitness", "nutrition", "rehabilitation", "physical therapy", "dinh dưỡng", "phục hồi chức năng"],
    },
    "healthcare_operations": {
        "EMR / EHR Systems": ["emr", "ehr", "electronic medical records", "epic", "cerner", "bệnh án điện tử"],
        "HIPAA & Compliance": ["hipaa", "osha", "fda", "regulatory compliance", "patient safety", "an toàn người bệnh"],
        "Medical Billing & Insurance": ["medical billing", "coding", "icd-10", "insurance", "claims", "bảo hiểm y tế"],
        "Scheduling & Coordination": ["scheduling", "care coordination", "intake", "admissions", "điều phối lịch khám"],
        "Quality Assurance": ["quality assurance", "quality control", "infection control", "kiểm soát nhiễm khuẩn"],
    },
    "tools_and_research": {
        "Clinical Documentation": ["documentation", "charting", "medical records", "hồ sơ bệnh án"],
        "Laboratory & Diagnostics": ["laboratory", "lab", "diagnostics", "xét nghiệm"],
        "Office & Reporting": ["excel", "microsoft office", "reporting", "database", "báo cáo"],
    },
    "soft_and_interpersonal": {
        "Patient Communication": ["communication", "customer service", "counseling", "empathy", "tư vấn bệnh nhân"],
        "Team Collaboration": ["teamwork", "interdisciplinary", "physicians", "phối hợp đa chuyên khoa"],
        "Leadership & Training": ["leadership", "supervising", "training", "quản lý"],
    },
}

HEALTHCARE_WEIGHTS = {
    "clinical_and_patient_care": 0.40,
    "healthcare_operations": 0.25,
    "tools_and_research": 0.20,
    "soft_and_interpersonal": 0.15,
}
assert abs(sum(HEALTHCARE_WEIGHTS.values()) - 1.0) < 1e-6

HEALTHCARE_CORE_SKILLS = {
    "clinical_and_patient_care": ["Patient Care & Assessment", "Emergency & CPR", "Medical Terminology"],
    "healthcare_operations": ["HIPAA & Compliance", "Scheduling & Coordination"],
    "tools_and_research": ["Clinical Documentation", "Office & Reporting"],
    "soft_and_interpersonal": ["Patient Communication", "Team Collaboration"],
}

HEALTHCARE_TARGET_COUNTS = {
    "clinical_and_patient_care": 3,
    "healthcare_operations": 2,
    "tools_and_research": 2,
    "soft_and_interpersonal": 2,
}

HEALTHCARE_DOMAIN_TERMS = {
    "patient", "patients", "clinical", "medical", "nursing", "diagnosis",
    "treatment", "medication", "cpr", "hipaa", "emr", "ehr", "triage",
    "vital signs", "charting", "hospital", "pharmacy", "rehabilitation",
    "wellness", "safety", "bệnh nhân", "lâm sàng", "điều trị", "xét nghiệm",
    "bệnh án", "chẩn đoán", "dược",
}
