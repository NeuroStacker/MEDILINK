// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the chatbot if the chat form exists
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        initializeChatbot();
    }
    
    // Initialize accessibility features if they exist
    const speechToTextBtn = document.getElementById('speech-to-text');
    if (speechToTextBtn) {
        initializeAccessibilityFeatures();
    }
    
    // Initialize any date inputs to default to today
    const dateInputs = document.querySelectorAll('input[type="date"]');
    if (dateInputs.length > 0) {
        const today = new Date().toISOString().substr(0, 10);
        dateInputs.forEach(input => {
            if (!input.value) {
                input.value = today;
            }
        });
    }
});

// Chatbot functionality
function initializeChatbot() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatContainer = document.getElementById('chat-container');
    
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input
        chatInput.value = '';
        
        // Show loading indicator
        addLoadingIndicator();
        
        // Send message to server
        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `message=${encodeURIComponent(message)}`
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            removeLoadingIndicator();
            
            // Add bot response to chat
            addMessageToChat('bot', data.response);
            
            // Scroll to bottom of chat
            chatContainer.scrollTop = chatContainer.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            removeLoadingIndicator();
            addMessageToChat('bot', 'Sorry, there was an error processing your request. Please try again.');
        });
    });
    
    function addMessageToChat(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message');
        messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        messageElement.textContent = message;
        chatContainer.appendChild(messageElement);
        
        // Scroll to bottom of chat
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function addLoadingIndicator() {
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('chat-message', 'bot-message', 'loading-indicator');
        loadingElement.textContent = 'Typing...';
        loadingElement.id = 'loading-indicator';
        chatContainer.appendChild(loadingElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function removeLoadingIndicator() {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }
}

// Accessibility features
function initializeAccessibilityFeatures() {
    const speechToTextBtn = document.getElementById('speech-to-text');
    const textToSpeechBtn = document.getElementById('text-to-speech');
    const targetInput = document.querySelector('.speech-input');
    const pageContent = document.querySelector('.feature-content');
    
    // Speech to text functionality
    if (speechToTextBtn && 'webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        speechToTextBtn.addEventListener('click', function() {
            recognition.start();
            speechToTextBtn.classList.add('listening');
            speechToTextBtn.innerHTML = '<i class="fas fa-microphone-alt"></i>';
        });
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            if (targetInput) {
                targetInput.value = transcript;
            }
        };
        
        recognition.onend = function() {
            speechToTextBtn.classList.remove('listening');
            speechToTextBtn.innerHTML = '<i class="fas fa-microphone"></i>';
        };
    }
    
    // Text to speech functionality
    if (textToSpeechBtn && 'speechSynthesis' in window) {
        textToSpeechBtn.addEventListener('click', function() {
            let textToRead = '';
            
            if (pageContent) {
                // Get visible text content from the page
                textToRead = pageContent.textContent.trim();
            }
            
            if (textToRead) {
                const utterance = new SpeechSynthesisUtterance(textToRead);
                window.speechSynthesis.speak(utterance);
                
                textToSpeechBtn.classList.add('speaking');
                textToSpeechBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                
                utterance.onend = function() {
                    textToSpeechBtn.classList.remove('speaking');
                    textToSpeechBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                };
            }
        });
    }
}

// For wearable device simulation
function simulateWearableData() {
    const heartRateInput = document.getElementById('heart_rate');
    const bloodOxygenInput = document.getElementById('blood_oxygen');
    const temperatureInput = document.getElementById('temperature');
    const stepsInput = document.getElementById('steps');
    
    if (heartRateInput && bloodOxygenInput && temperatureInput && stepsInput) {
        // Generate random values
        const heartRate = Math.floor(Math.random() * (100 - 60 + 1)) + 60;
        const bloodOxygen = Math.floor(Math.random() * (100 - 94 + 1)) + 94;
        const temperature = (Math.random() * (37.5 - 36.5) + 36.5).toFixed(1);
        const steps = Math.floor(Math.random() * 10000);
        
        // Set values
        heartRateInput.value = heartRate;
        bloodOxygenInput.value = bloodOxygen;
        temperatureInput.value = temperature;
        stepsInput.value = steps;
    }
}

// For emergency alert
function getLocation() {
    const locationInput = document.getElementById('location');
    
    if (locationInput && 'geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            // Use reverse geocoding to get address (in a real app)
            // Here we'll just use coordinates
            locationInput.value = `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
        }, function(error) {
            console.error('Error getting location:', error);
            locationInput.placeholder = 'Could not get location. Please enter manually.';
        });
    }
} 