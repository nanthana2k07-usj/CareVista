import pandas as pd
import random

# =============================
# SYMPTOMS (MUST MATCH app.py)
# =============================
symptoms = [
"fever","cough","headache","fatigue","chest_pain","breathing_issue",
"nausea","vomiting","dizziness","runny_nose","sneezing","sore_throat",
"body_pain","chills","loss_of_taste","loss_of_smell","joint_pain",
"muscle_pain","blurred_vision","rapid_heartbeat","skin_rash",
"night_sweats","weight_loss","weight_gain","anxiety","depression",
"insomnia","confusion","memory_loss"
]

# =============================
# 15 DISEASES
# =============================
diseases = [
"Flu","COVID-19","Food Poisoning","Migraine",
"Asthma","Tuberculosis","Heart Disease","Common Cold",
"Dengue","Malaria","Pneumonia",
"Sinusitis","Bronchitis","Anxiety Disorder","Typhoid"
]

# =============================
# CORE SYMPTOMS (VERY IMPORTANT)
# =============================
core_map = {

"Flu": ["fever","chills","body_pain","fatigue"],
"COVID-19": ["fever","cough","loss_of_taste","breathing_issue"],
"Food Poisoning": ["nausea","vomiting","dizziness"],
"Migraine": ["headache","nausea","dizziness"],
"Asthma": ["breathing_issue","cough"],
"Tuberculosis": ["cough","weight_loss","night_sweats"],
"Heart Disease": ["chest_pain","rapid_heartbeat"],
"Common Cold": ["cough","runny_nose","sneezing"],

"Dengue": ["fever","joint_pain","body_pain","skin_rash"],
"Malaria": ["fever","chills","fatigue"],
"Pneumonia": ["cough","fever","breathing_issue"],
"Sinusitis": ["headache","runny_nose"],
"Bronchitis": ["cough","fatigue","breathing_issue"],
"Anxiety Disorder": ["anxiety","insomnia","rapid_heartbeat"],
"Typhoid": ["fever","fatigue","body_pain"]

}

# =============================
# GENERATE ROW
# =============================
def generate_row(core):
    row = []
    for s in symptoms:
        if s in core:
            row.append(1 if random.random() > 0.2 else 0)  # strong
        else:
            row.append(1 if random.random() < 0.08 else 0) # noise
    return row

# =============================
# CREATE DATASET
# =============================
data = []

for disease in diseases:
    for _ in range(350):  # balanced
        row = generate_row(core_map[disease])
        row.append(disease)
        data.append(row)

df = pd.DataFrame(data, columns=symptoms + ["disease"])

df.to_csv("dataset.csv", index=False)

print("✅ Dataset created:", df.shape)