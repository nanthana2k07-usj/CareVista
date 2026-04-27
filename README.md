CareVista – AI-Driven Health Monitoring & Disease Management System
Overview

CareVista is an AI-based healthcare system designed to assist in disease prediction, continuous health monitoring, and treatment management. The system enables patients to input symptoms and health details, which are analyzed using machine learning to predict diseases, assess risk levels, and provide personalized suggestions.

A key feature of CareVista is the Treatment Burden Index (TBI), which evaluates how difficult it is for a patient to follow a treatment plan in real-life conditions.

Features
User registration and login system
Patient health data entry (symptoms, vitals, treatment details)
Disease prediction using Machine Learning
Risk level analysis (Low / Moderate / High)
Treatment Burden Index (TBI) calculation
Personalized health suggestions
Patient history 

Tech Stack

1)Frontend
HTML
CSS
JavaScript

2)Backend
Python
Flask

3)Database
MongoDB

4)Machine Learning
Scikit-learn
Pandas
NumPy

Project Structure
CareVista/
│── templates/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── patient_details.html
│   ├── symptoms.html
│   ├── result.html
│   ├── tbi.html
│ 
│
│── app.py
│── dataset.csv
│── tbi_dataset.csv
│── model.pkl
│── tbi_model.pkl
│── le_disease.pkl
│── le_lifestyle.pkl
│── le_treatment.pkl
│── train_model.py
│── generate_dataset.py
│── venv/

Working Flow

User logs into the system
Enters patient details and symptoms
Machine learning model predicts disease
Risk level is displayed
User proceeds to TBI analysis
Treatment burden score is calculated
System shows suggestions and insights

Installation & Setup

Clone the repository:
git clone https://github.com/your-username/carevista.git
cd carevista

Create virtual environment:
python -m venv venv
Activate virtual environment:
venv\Scripts\activate
Install dependencies:
pip install -r requirements.txt

Run the application:
python app.py

Open in browser:
http://127.0.0.1:5000/

Future Enhancements

Mobile application development
Integration with wearable devices
Advanced AI models for better accuracy
Enhanced security and data privacy
Expansion to multiple disease domains

Conclusion
CareVista focuses on improving healthcare by combining artificial intelligence with continuous patient monitoring. It enhances treatment adherence, reduces patient burden, and supports better long-term health outcomes.
