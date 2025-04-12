from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import requests
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import time
import random

app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
app.secret_key = 'medilink_secret_key'
app.config['UPLOAD_FOLDER'] = 'app/uploads'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Mock Mistral API function (replace with actual API when available)
def mistral_api_call(prompt, max_tokens=500):
    # This is a mock function that simulates an API response
    # Replace with actual Mistral API call when implemented
    time.sleep(1)  # Simulate API latency
    
    responses = {
        "prescription": "Based on the uploaded prescription, you've been prescribed:\n- Medication A: Take 1 tablet twice daily with food\n- Medication B: Apply topically to affected area once daily\nThese medications are for treating your diagnosed condition. Please follow the prescribed dosage carefully.",
        "symptoms": "Based on your symptoms, it could be a common cold or mild flu. Rest, stay hydrated, and monitor your temperature. If symptoms worsen or persist for more than 3 days, please consult a healthcare provider.",
        "language": "Translation complete.",
        "forum": "Many patients have reported similar experiences. This is normally not a cause for concern, but you should monitor the symptoms. If they persist, consult your doctor at your next appointment.",
        "scheme": "Based on the information provided, you may be eligible for the Healthcare Assistance Program. This program offers financial support for medical expenses to qualifying individuals.",
        "chatbot": "I'd recommend discussing this with your healthcare provider. While I can provide general information, your doctor has your complete medical history and can offer personalized advice."
    }
    
    for key in responses:
        if key in prompt.lower():
            return {"response": responses[key]}
    
    return {"response": "I've processed your request. Please consult with a healthcare professional for personalized advice."}

# Mock data for the application
mood_data = []
vitals_data = []

# Authentication routes
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == 'user' and password == 'password':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Login required decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Main dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# OCR Prescription Support
@app.route('/ocr_prescription', methods=['GET', 'POST'])
@login_required
def ocr_prescription():
    if request.method == 'POST':
        if 'prescription' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['prescription']
        
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                # Extract text using OCR
                img = Image.open(filepath)
                extracted_text = pytesseract.image_to_string(img)
                
                # Send to Mistral API
                explanation = mistral_api_call(f"prescription: {extracted_text}")
                
                return render_template('ocr_prescription.html', 
                                      extracted_text=extracted_text,
                                      explanation=explanation['response'],
                                      image_path=os.path.join('uploads', filename))
            except Exception as e:
                flash(f'Error processing image: {str(e)}', 'danger')
                return redirect(request.url)
    
    return render_template('ocr_prescription.html')

# Multilingual UI Support
@app.route('/multilingual', methods=['GET', 'POST'])
@login_required
def multilingual():
    languages = ['English', 'Spanish', 'French', 'German', 'Chinese', 'Hindi']
    content = {
        'title': 'MediLink - Healthcare Accessibility',
        'welcome': 'Welcome to MediLink, your healthcare companion',
        'description': 'MediLink helps you manage your healthcare needs easily and efficiently.'
    }
    
    translated_content = content.copy()
    
    if request.method == 'POST':
        selected_language = request.form.get('language', 'English')
        
        if selected_language != 'English':
            # In a real app, we would call the Mistral API to translate the content
            # For now, we'll simulate a translation
            translation = mistral_api_call(f"language: Translate the following to {selected_language}: {json.dumps(content)}")
            flash(f'Content translated to {selected_language}', 'success')
    
    return render_template('multilingual.html', languages=languages, content=translated_content)

# Medical Test Booking
@app.route('/test_booking', methods=['GET', 'POST'])
@login_required
def test_booking():
    tests = [
        {'id': 1, 'name': 'Complete Blood Count (CBC)', 'price': '$30'},
        {'id': 2, 'name': 'Comprehensive Metabolic Panel', 'price': '$45'},
        {'id': 3, 'name': 'Lipid Panel', 'price': '$35'},
        {'id': 4, 'name': 'Thyroid Function Tests', 'price': '$60'},
        {'id': 5, 'name': 'Hemoglobin A1C', 'price': '$40'}
    ]
    
    if request.method == 'POST':
        test_id = request.form.get('test_id')
        date = request.form.get('date')
        time = request.form.get('time')
        
        test_name = next((test['name'] for test in tests if str(test['id']) == test_id), None)
        
        if test_name and date and time:
            flash(f'Booking confirmed for {test_name} on {date} at {time}', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Please fill all required fields', 'danger')
    
    return render_template('test_booking.html', tests=tests)

# Accessibility Features
@app.route('/accessibility')
@login_required
def accessibility():
    return render_template('accessibility.html')

# Therapy Tracker
@app.route('/therapy_tracker', methods=['GET', 'POST'])
@login_required
def therapy_tracker():
    global mood_data
    
    if request.method == 'POST':
        date = request.form.get('date')
        mood = int(request.form.get('mood'))
        notes = request.form.get('notes', '')
        
        mood_data.append({'date': date, 'mood': mood, 'notes': notes})
        flash('Mood recorded successfully!', 'success')
    
    # Generate graph if we have data
    graph_data = None
    if mood_data:
        plt.figure(figsize=(10, 5))
        dates = [entry['date'] for entry in mood_data]
        moods = [entry['mood'] for entry in mood_data]
        plt.plot(dates, moods, marker='o')
        plt.title('Mood Tracker')
        plt.xlabel('Date')
        plt.ylabel('Mood (1-10)')
        plt.ylim(0, 11)
        plt.grid(True)
        
        # Convert plot to base64 string for HTML display
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graph_data = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
    
    return render_template('therapy_tracker.html', mood_data=mood_data, graph_data=graph_data)

# AI Symptom Checker
@app.route('/symptom_checker', methods=['GET', 'POST'])
@login_required
def symptom_checker():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '')
        duration = request.form.get('duration', '')
        severity = request.form.get('severity', '')
        
        prompt = f"symptoms: Patient reports: {symptoms}. Duration: {duration}. Severity: {severity}/10."
        response = mistral_api_call(prompt)
        
        return render_template('symptom_checker.html', 
                              symptoms=symptoms,
                              duration=duration,
                              severity=severity,
                              advice=response['response'])
    
    return render_template('symptom_checker.html')

# Wearable Device Integration
@app.route('/wearable_integration', methods=['GET', 'POST'])
@login_required
def wearable_integration():
    global vitals_data
    
    if request.method == 'POST':
        heart_rate = int(request.form.get('heart_rate', 0))
        blood_oxygen = int(request.form.get('blood_oxygen', 0))
        temperature = float(request.form.get('temperature', 0))
        steps = int(request.form.get('steps', 0))
        
        vitals_data.append({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'heart_rate': heart_rate,
            'blood_oxygen': blood_oxygen,
            'temperature': temperature,
            'steps': steps
        })
        
        # Check for abnormal values
        alerts = []
        if heart_rate > 100 or heart_rate < 50:
            alerts.append('Abnormal heart rate detected!')
        if blood_oxygen < 95:
            alerts.append('Low blood oxygen level detected!')
        if temperature > 37.5 or temperature < 36.0:
            alerts.append('Abnormal body temperature detected!')
        
        for alert in alerts:
            flash(alert, 'danger')
        
        if not alerts:
            flash('Vitals recorded successfully. All readings are normal.', 'success')
    
    return render_template('wearable_integration.html', vitals_data=vitals_data)

# Pharmacy Integration
@app.route('/pharmacy', methods=['GET', 'POST'])
@login_required
def pharmacy():
    pharmacies = [
        {'id': 1, 'name': 'MediCare Pharmacy', 'address': '123 Main St', 'phone': '555-1234'},
        {'id': 2, 'name': 'Health Plus Drugs', 'address': '456 Oak Ave', 'phone': '555-5678'},
        {'id': 3, 'name': 'Community Pharmacy', 'address': '789 Pine Rd', 'phone': '555-9012'},
        {'id': 4, 'name': 'Quick Meds', 'address': '101 Maple Dr', 'phone': '555-3456'}
    ]
    
    if request.method == 'POST':
        if 'prescription' in request.files:
            file = request.files['prescription']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract medications (in a real app, this would use OCR and more processing)
                medications = ['Medication A - 10mg', 'Medication B - 25mg', 'Medication C - 5mg']
                
                pharmacy_id = request.form.get('pharmacy')
                pharmacy_name = next((p['name'] for p in pharmacies if str(p['id']) == pharmacy_id), None)
                
                if pharmacy_name:
                    flash(f'Prescription sent to {pharmacy_name}. They will contact you soon.', 'success')
                    return render_template('pharmacy.html', 
                                          pharmacies=pharmacies, 
                                          medications=medications,
                                          selected_pharmacy=pharmacy_id,
                                          prescription_uploaded=True)
    
    return render_template('pharmacy.html', pharmacies=pharmacies)

# Emergency Alert
@app.route('/emergency', methods=['GET', 'POST'])
@login_required
def emergency():
    if request.method == 'POST':
        emergency_type = request.form.get('emergency_type')
        location = request.form.get('location', 'Unknown location')
        
        # In a real app, this would trigger an actual emergency alert
        flash(f'Emergency alert for {emergency_type} sent! Help is on the way to {location}.', 'danger')
    
    return render_template('emergency.html')

# Personalized Analytics
@app.route('/analytics')
@login_required
def analytics():
    # Generate random health data for demonstration
    dates = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    weight_data = [round(random.uniform(70, 80), 1) for _ in range(6)]
    bp_systolic = [random.randint(110, 130) for _ in range(6)]
    bp_diastolic = [random.randint(70, 85) for _ in range(6)]
    glucose_data = [random.randint(80, 120) for _ in range(6)]
    
    # Generate weight chart
    plt.figure(figsize=(8, 4))
    plt.plot(dates, weight_data, marker='o', color='blue')
    plt.title('Weight Trend')
    plt.ylabel('Weight (kg)')
    plt.grid(True)
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    weight_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Generate blood pressure chart
    plt.figure(figsize=(8, 4))
    plt.plot(dates, bp_systolic, marker='o', color='red', label='Systolic')
    plt.plot(dates, bp_diastolic, marker='o', color='blue', label='Diastolic')
    plt.title('Blood Pressure Trend')
    plt.ylabel('mmHg')
    plt.legend()
    plt.grid(True)
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    bp_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Generate glucose chart
    plt.figure(figsize=(8, 4))
    plt.plot(dates, glucose_data, marker='o', color='green')
    plt.title('Blood Glucose Trend')
    plt.ylabel('mg/dL')
    plt.grid(True)
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    glucose_chart = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return render_template('analytics.html', 
                          weight_chart=weight_chart,
                          bp_chart=bp_chart,
                          glucose_chart=glucose_chart)

# Community Forum
@app.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    forum_posts = [
        {'id': 1, 'title': 'Managing Diabetes', 'content': 'What are some tips for managing type 2 diabetes?', 'author': 'HealthSeeker', 'date': '2023-05-10'},
        {'id': 2, 'title': 'Chronic Back Pain', 'content': 'Has anyone found relief from chronic lower back pain?', 'author': 'BackPainSufferer', 'date': '2023-05-12'},
        {'id': 3, 'title': 'Medication Side Effects', 'content': 'I\'m experiencing dizziness from my blood pressure medication. Is this normal?', 'author': 'ConcernedPatient', 'date': '2023-05-15'}
    ]
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        
        # Use Mistral API to generate a response
        prompt = f"forum: User query about health topic: {query}"
        response = mistral_api_call(prompt)
        
        return render_template('forum.html', 
                              forum_posts=forum_posts,
                              query=query,
                              response=response['response'])
    
    return render_template('forum.html', forum_posts=forum_posts)

# Secure Health Record Sharing
@app.route('/health_records', methods=['GET', 'POST'])
@login_required
def health_records():
    sample_records = [
        {'id': 1, 'name': 'Annual Physical Results', 'date': '2023-01-15', 'type': 'PDF'},
        {'id': 2, 'name': 'Blood Test Report', 'date': '2023-03-20', 'type': 'PDF'},
        {'id': 3, 'name': 'X-Ray Image', 'date': '2023-04-10', 'type': 'Image'},
        {'id': 4, 'name': 'Specialist Consultation', 'date': '2023-05-05', 'type': 'PDF'}
    ]
    
    if request.method == 'POST':
        if 'health_record' in request.files:
            file = request.files['health_record']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                flash('Health record uploaded successfully', 'success')
    
    return render_template('health_records.html', records=sample_records)

# Government Scheme Integration
@app.route('/gov_schemes', methods=['GET', 'POST'])
@login_required
def gov_schemes():
    schemes = [
        {'id': 1, 'name': 'Healthcare Assistance Program', 'description': 'Financial support for medical expenses'},
        {'id': 2, 'name': 'Medication Subsidy Scheme', 'description': 'Subsidies for essential medications'},
        {'id': 3, 'name': 'Disability Support Program', 'description': 'Support services for individuals with disabilities'},
        {'id': 4, 'name': 'Senior Care Initiative', 'description': 'Healthcare services for elderly citizens'}
    ]
    
    if request.method == 'POST':
        scheme_id = request.form.get('scheme_id')
        age = request.form.get('age')
        income = request.form.get('income')
        condition = request.form.get('condition')
        
        scheme_name = next((s['name'] for s in schemes if str(s['id']) == scheme_id), None)
        
        if scheme_name:
            prompt = f"scheme: Check eligibility for {scheme_name}. Age: {age}, Annual Income: {income}, Medical Condition: {condition}"
            response = mistral_api_call(prompt)
            
            return render_template('gov_schemes.html', 
                                  schemes=schemes,
                                  selected_scheme=scheme_id,
                                  eligibility_result=response['response'])
    
    return render_template('gov_schemes.html', schemes=schemes)

# Chatbot
@app.route('/chatbot', methods=['GET', 'POST'])
@login_required
def chatbot():
    if request.method == 'POST':
        message = request.form.get('message', '')
        
        if message:
            prompt = f"chatbot: {message}"
            response = mistral_api_call(prompt)
            
            return jsonify({'message': message, 'response': response['response']})
    
    return render_template('chatbot.html')

if __name__ == '__main__':
    app.run(debug=True) 