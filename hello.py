from flask import Flask, render_template, jsonify, request
import random
import smtplib
import pyttsx3  # For voice alerts
import joblib  # To load an ML model
import numpy as np

app = Flask(__name__)

# Load a pre-trained ML model (assuming it's saved as 'water_quality_model.pkl')
try:
    model = joblib.load("water_quality_model.pkl")
except:
    model = None  # Fallback to basic logic if model is unavailable

def calculate_safety_percentage(ph, turbidity, tds):
    """Calculate water safety percentage based on thresholds."""
    ph_score = max(0, min(100, (8.5 - abs(7 - ph)) * 20))  # 100% if pH is 7, decreases outward
    turbidity_score = max(0, min(100, (5 - turbidity) * 20))  # 100% if turbidity is 0, decreases
    tds_score = max(0, min(100, (500 - tds) / 5))  # 100% if TDS is 0, decreases
    
    avg_safety = (ph_score + turbidity_score + tds_score) / 3
    return round(avg_safety, 2)

def predict_water_quality(ph, turbidity, tds):
    """Enhanced AI-based model for water safety prediction"""
    safety_percentage = calculate_safety_percentage(ph, turbidity, tds)
    if model:
        prediction = model.predict(np.array([[ph, turbidity, tds]]))[0]
        status = "Safe" if prediction == 1 else "Unsafe"
    else:
        status = "Unsafe" if ph < 6.5 or ph > 8.5 or turbidity > 5 or tds > 500 else "Safe"
    
    return status, safety_percentage

def send_alert_email(receiver_email, status, safety_percentage):
    """Sends an email alert with water safety percentage to a user-specified email"""
    sender_email = "hritishasapu@gmail.com"
    password = "Anushri@17"
    
    subject = "Water Quality Report"
    message = f"""Subject: {subject}\n\nWater Quality Status: {status}\nSafety Percentage: {safety_percentage}%\n\n"""
    if status == "Unsafe":
        message += "⚠️ The water is not safe for drinking. Please purify it before use."
    else:
        message += "✅ The water is safe to drink."
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)
        server.quit()
    except:
        print("Email alert failed")

#def voice_alert(message):
 #   """Text-to-Speech (TTS) alert"""
  #  engine = pyttsx3.init()
   # engine.say(message)
    #engine.runAndWait()

@app.route('/')
def home():
    """Serve the HTML page."""
    return render_template('index.html')

@app.route('/check_water', methods=['GET'])
def check_water():
    """API to check water quality based on sensor inputs."""
    ph = float(request.args.get("ph", random.uniform(6, 9)))
    turbidity = float(request.args.get("turbidity", random.uniform(0, 10)))
    tds = float(request.args.get("tds", random.uniform(100, 600)))
    receiver_email = request.args.get("email", "user_email@gmail.com")

    status, safety_percentage = predict_water_quality(ph, turbidity, tds)
    message = f"💧 Water Quality: {status} ({safety_percentage}% Safe)"
    
    send_alert_email(receiver_email, status, safety_percentage)
    #voice_alert(message)
    
    return jsonify({"ph": ph, "turbidity": turbidity, "tds": tds, "status": status, "safety_percentage": safety_percentage, "message": message})

if __name__ == "__main__":
    app.run(debug=True)