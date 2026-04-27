from flask import Flask, render_template, request, redirect, url_for, jsonify
import pickle
import numpy as np
import sqlite3
from openai import OpenAI
from pymongo import MongoClient
from datetime import datetime
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = "secret123"
# ---------------- MONGODB CONNECTION ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["carevista"]
collection = db["reports"]
users_collection = db["users"]

# ================= RULE-BASED CORRECTION =================

def apply_medical_rules(symptoms, prediction, risk, heart_rate, oxygen, condition):

    hr = int(heart_rate) if heart_rate else None
    ox = int(oxygen) if oxygen else None

    if "chest_pain" in symptoms and hr and hr > 120:
        return "Heart Disease", "High"

    if "breathing_issue" in symptoms and "cough" in symptoms:
        return "Asthma", "Medium"

    if ox and ox < 92:
        return "Respiratory Issue", "High"

    if "fever" in symptoms and "cough" in symptoms:
        return "Flu", "Medium"

    # Existing conditions logic
    if condition == "diabetes":
        if "vomiting" in symptoms or "fatigue" in symptoms:
            return "Diabetic Complication", "High"

    if condition == "bp":
        if "headache" in symptoms and "dizziness" in symptoms:
            return "Hypertension Risk", "High"

    return prediction, risk


# ================= ADVANCED RECOMMENDATION =================

def generate_recommendation(symptoms, prediction, risk, temp, heart_rate, oxygen):

    advice = []
    alerts = []

    # 🚨 CRITICAL ALERTS
    if "chest_pain" in symptoms:
        alerts.append("⚠️ Chest pain detected — seek emergency care immediately")

    if "breathing_issue" in symptoms:
        alerts.append("⚠️ Breathing difficulty — urgent medical attention required")

    if oxygen:
        ox = int(oxygen)
        if ox < 85:
            alerts.append("⚠️ CRITICAL: Oxygen extremely low — ICU care required")
        elif ox < 92:
            alerts.append("⚠️ Low oxygen — consult doctor immediately")

    if heart_rate:
        hr = int(heart_rate)
        if hr > 130:
            alerts.append("⚠️  Very high heart rate — emergency evaluation needed")
        elif hr < 50:
            alerts.append("⚠️ Low heart rate — possible cardiac issue")

    if temp:
        if float(temp) > 104:
            alerts.append("⚠️  High fever — immediate treatment required")

    # ================= DISEASE-SPECIFIC =================

    if prediction == "Food Poisoning":
        advice += [
            "Drink ORS every 15–20 minutes",
            "Avoid solid food for few hours",
            "Eat bland food (rice, banana)",
            "Avoid spicy and oily food",
            "Seek medical care if symptoms worsen",
            "For Vomiting (Anti-emetic) - Ondansetron (Ondem)",
            "For Diarrhea (Anti-diarrheal) - Loperamide (Imodium)",
            "For Abdominal Pain (Antispasmodic) - Hyoscine Butylbromide (Buscopan)",
            "For Fever (Antipyretic) - Paracetamol (Tylenol)",
            "For Dehydration (IV Fluids) - Normal Saline or Ringer's Lactate",
            "Avoid oily and spicy food, dairy products, caffeine, and alcohol until recovery"

        ]

    elif prediction == "Flu":
        advice += [
            "Take complete rest",
            "Use paracetamol",
            "Drink warm fluids",
            "Steam inhalation",
            "Avoid cold drinks and smoking",
            "For Fever (Antipyretic) - Paracetamol (Tylenol)",
            "For Cough (Antitussive) - Dextromethorphan (Robitussin)",
            "For Body Pain (Analgesic) - Ibuprofen (Advil)",
            "For Nasal Congestion (Decongestant) - Pseudoephedrine (Sudafed)",
            "For Sore Throat (Lozenges) - Benzocaine Lozenges (Cepacol)",
            "Avoid cold drinks, smoking, and alcohol until recovery"
        ]

    elif prediction == "Heart Disease":
        advice += [
            "Immediate hospital visit",
            "Avoid physical activity",
            "Monitor heart rate & BP",
            "Follow low-salt diet",
            "For Chest Pain (Nitrate) - Nitroglycerin (Nitrostat)",
            "For High Blood Pressure (Antihypertensive) - Lisinopril (Prinivil)",
            "For High Cholesterol (Statin) - Atorvastatin (Lipitor)",
            "For Blood Thinner - Aspirin (Bayer)",
            "For Heart Failure (Diuretic) - Furosemide (Lasix)",
            "Avoid smoking, alcohol, and high-fat foods",
            "⚠️ Should visit cardiologist within 24 hours for further evaluation and management"  
        ]

    elif prediction == "Asthma": 
        advice += [
            "Use inhaler",
            "Avoid dust and smoke",
            "Practice breathing exercises",
            "For Acute Attack (Bronchodilator) - Albuterol (Ventolin)",
            "For Inflammation (Corticosteroid) - Fluticasone (Flovent)",
            "For Severe Cases (Oral Steroid) - Prednisone",
            "For Allergic Triggers (Antihistamine) - Loratadine (Claritin)",
            "Avoid allergens, cold air, and strenuous exercise"
        ]

    elif prediction == "COVID-19":
        advice += [
            "Isolate immediately",
            "Monitor oxygen regularly",
            "Stay hydrated",
            "Use paracetamol for fever",
            "For Fever (Antipyretic) - Paracetamol (Tylenol)", 
            "For Cough (Antitussive) - Dextromethorphan (Robitussin)",
            "For Body Pain (Analgesic) - Ibuprofen (Advil)",        
            "For Nasal Congestion (Decongestant) - Pseudoephedrine (Sudafed)",
            "For Sore Throat (Lozenges) - Benzocaine Lozenges (Cepacol)",
            "Avoid smoking, alcohol, and crowded places until recovery"
        ]

    elif prediction == "Migraine":
        advice += [
            "Rest in dark room",
            "Avoid noise and stress",
            "Stay hydrated",
            "For Pain (Analgesic) - Ibuprofen (Advil)",
            "For Nausea (Antiemetic) - Metoclopramide (Reglan)",
            "For Severe Migraine (Triptan) - Sumatriptan (Imitre x)",
            "For Preventive (Beta-blocker) - Propranolol (Inderal)",   
            "Avoid triggers like certain foods, strong smells, and bright lights"
            ]

    elif prediction == "Tuberculosis":
        advice += [
            "Follow long-term medication",
            "Maintain nutrition",
            "Avoid spreading infection",
            "For Active TB (Antibiotics) - Isoniazid, Rifampin, Ethambutol, Pyrazinamide",
            "For Latent TB (Single Antibiotic) - Isoniazid",
            "For Drug-Resistant TB (Second-line Drugs) - Bedaquiline, Delamanid",
            "For Symptom Relief (Supportive Care) - Pain relievers, Cough suppressants",
            "Avoid close contact with others until treatment is underway and effective"
        ]

    # ================= SYMPTOM-BASED =================

    if "fever" in symptoms:
        advice.append("Monitor temperature regularly")

    if "cough" in symptoms:
        advice.append("Avoid cold drinks")

    if "vomiting" in symptoms:
        advice.append("Prevent dehydration")

    if "fatigue" in symptoms:
        advice.append("Ensure proper rest")

    # ================= RISK =================

    if risk == "High":
        alerts.append("⚠️  HIGH RISK — Immediate hospital consultation required")
        advice.append("Do not delay treatment")

    elif risk == "Medium":
        advice.append("Consult doctor within 24 hours")

    else:
        advice.append("Condition mild — home care sufficient")

    # ================= GENERAL =================

    advice += [
        "Stay hydrated",
        "Eat healthy",
        "Get proper sleep",
        "Avoid smoking and alcohol",
        "Seek medical care if symptoms worsen or new symptoms develop"
    ]

    return advice, alerts


# ---------------- LOAD MODEL ----------------

model = pickle.load(open("model.pkl", "rb"))

# ---------------- SYMPTOMS ----------------

symptom_list = [
"fever","cough","headache","fatigue","chest_pain","breathing_issue",
"nausea","vomiting","dizziness","runny_nose","sneezing","sore_throat",
"body_pain","chills","loss_of_taste","loss_of_smell","joint_pain",
"muscle_pain","blurred_vision","rapid_heartbeat","skin_rash",
"night_sweats","weight_loss","weight_gain","anxiety","depression",
"insomnia","confusion","memory_loss"
]


# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Check if user exists in MongoDB
        user = users_collection.find_one({"email": email})
        
        if user and check_password_hash(user["password"], password):
            # Password is correct
            session["email"] = email
            session["user_id"] = str(user["_id"])
            return redirect(url_for("patient_details"))
        else:
            # User doesn't exist or password is wrong
            return render_template("login.html", error="Invalid email or password")
    
    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return render_template("register.html", error="Email already registered")
        
        # Check if passwords match
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        # Check password length
        if len(password) < 6:
            return render_template("register.html", error="Password must be at least 6 characters")
        
        # Create new user
        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            "email": email,
            "password": hashed_password,
            "created_at": datetime.now()
        })
        
        return redirect(url_for("login"))
    
    return render_template("register.html")


@app.route("/patient_details", methods=["GET","POST"])
def patient_details():
    if request.method == "POST":
        session["name"] = request.form.get("name")
        session["age"] = request.form.get("age")
        session["gender"] = request.form.get("gender")
        return redirect(url_for("symptoms"))
    return render_template("patient_details.html")



@app.route("/symptoms")
def symptoms():
    return render_template("symptoms.html")


# ================= PREDICT =================

@app.route("/predict", methods=["POST"])
def predict():

    symptoms = request.form.getlist("symptoms")
    extra_symptoms = request.form.get("extra_symptoms")
    existing_conditions = request.form.get("existing_conditions")

    temperature = request.form.get("temperature")
    heart_rate = request.form.get("heart_rate")
    oxygen = request.form.get("oxygen")

    # 🔥 Extra symptoms
    if extra_symptoms:
        for s in extra_symptoms.split(","):
            symptoms.append(s.strip().lower().replace(" ","_"))

    # 🔥 Condition detect
    condition = None
    if existing_conditions:
        text = existing_conditions.lower()
        if "diabetes" in text:
            condition = "diabetes"
        elif "bp" in text:
            condition = "bp"

    # ❗ No input safety
    if len(symptoms) == 0:
        return render_template("symptoms.html", error="Enter at least one symptom")

    # 🔥 Convert to ML input
    input_data = [1 if s in symptoms else 0 for s in symptom_list]
    input_array = np.array(input_data).reshape(1,-1)

    # 🔥 ML prediction
    prediction = model.predict(input_array)[0]

    confidence = 90
    top_predictions = [(prediction, confidence)]

    # 🔥 BOOST RULES (fix ML weakness)

    if "loss_of_taste" in symptoms:
        prediction = "COVID-19"

    elif "night_sweats" in symptoms and "weight_loss" in symptoms:
        prediction = "Tuberculosis"

    elif "chest_pain" in symptoms and "rapid_heartbeat" in symptoms:
        prediction = "Heart Disease"

    elif "vomiting" in symptoms and "nausea" in symptoms:
        prediction = "Food Poisoning"

    elif "breathing_issue" in symptoms and "cough" in symptoms:
        prediction = "Asthma"

    # 🔥 Risk level

    if prediction in ["Heart Disease","COVID-19","Tuberculosis"]:
        risk = "High"
    elif prediction in ["Flu","Migraine","Asthma"]:
        risk = "Medium"
    else:
        risk = "Low"

    # 🔥 Apply rules
    prediction, risk = apply_medical_rules(
        symptoms, prediction, risk, heart_rate, oxygen, condition
    )

    # Doctor
    if prediction == "Heart Disease":
        doctor = "Cardiologist"
        hospital = "Apollo Hospital"
    else:
        doctor = "General Physician"
        hospital = "Nearby Clinic"

    # Recommendations
    recommendations, alerts = generate_recommendation(
        symptoms, prediction, risk, temperature, heart_rate, oxygen
    )
    session["symptoms"] = symptoms
    session["disease"] = prediction

    return render_template(
        "result.html",
        prediction=prediction,
        symptoms=symptoms,
        temperature=temperature,
        heart_rate=heart_rate,
        oxygen=oxygen,
        risk=risk,
        doctor=doctor,
        hospital=hospital,
        confidence=confidence,
        top_predictions=top_predictions,
        recommendations=recommendations,
        alerts=alerts
    )

# ----------------- TBI CALCULATOR ----------------
@app.route('/tbi', methods=['POST'])
def tbi():
    disease = request.form.get('disease')
    treatment = request.form.get('treatment')
    lifestyle = request.form.get('lifestyle')

    # 🔥 SIMPLE SCORE LOGIC
    score = 50

    if treatment and "multiple" in treatment.lower():
        score += 20

    if lifestyle and "strict" in lifestyle.lower():
        score += 15

    if score > 100:
        score = 100

    # 🔥 LEVEL
    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Moderate"
    else:
        level = "Low"

    # 🔥 SAVE TO MONGODB
    collection.insert_one({
        "name": session.get("name"),
        "age": session.get("age"),
        "gender": session.get("gender"),
        "disease": disease,
        "score": score,
        "level": level,
        "created_at": datetime.now()
    })

    # 🔥 RETURN UPDATED PAGE
    return render_template(
        "tbi.html",
        disease=disease,
        treatment=treatment,
        lifestyle=lifestyle,
        score=score,
        level=level
    )
# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)