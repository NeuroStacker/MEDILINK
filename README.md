# MediLink - Healthcare Accessibility Platform

MediLink is a Flask-based healthcare accessibility application designed to make healthcare more accessible through various AI-powered features.

## Features

- OCR Prescription Support: Upload and analyze prescriptions
- Multilingual UI Support: Use the platform in different languages
- Medical Test Booking: Schedule medical tests easily
- Accessibility Features: Text-to-speech and speech-to-text integration
- Therapy Tracker: Track mood and therapy progress
- AI Symptom Checker: Get preliminary health advice
- Wearable Device Integration: Connect health devices and monitor vitals
- Pharmacy Integration: Order medications online
- Emergency Alert: Quick emergency assistance
- Personalized Analytics: View health trends
- Community Forum: Connect with other patients
- Secure Health Record Sharing: Share medical reports securely
- Government Scheme Integration: Check eligibility for healthcare programs
- Health Chatbot: Get answers to health queries

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/medilink.git
cd medilink
```

2. Create a virtual environment and activate it:
```
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install the required packages:
```
pip install -r requirements.txt
```

4. Install Tesseract OCR:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki and add to PATH
   - macOS: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

## Usage

1. Run the Flask application:
```
python app.py
```

2. Access the application in your web browser at `http://localhost:5000`

3. Login with the demo credentials:
   - Username: `user`
   - Password: `password`

## Configuration

- OCR settings can be adjusted in the app.py file
- Upload paths can be configured in the app configuration section

## Dependencies

- Flask: Web framework
- Pillow: Image processing
- pytesseract: OCR functionality
- matplotlib: Data visualization
- requests: HTTP requests for API calls

## Note

This application uses simulated API responses for demonstration purposes. In a production environment, you would integrate with real healthcare APIs and services. 