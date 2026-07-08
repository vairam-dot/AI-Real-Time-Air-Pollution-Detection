// Voice Authentication & Voice Commands Module for AirPollutionAI
class VoiceAuthentication {
    constructor() {
        this.recognition = null;
        this.isListening = false;
        this.transcript = '';
        this.synthesis = window.speechSynthesis;
        this.setupRecognition();
    }

    setupRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn('Speech Recognition not supported in this browser');
            this.showVoiceMessage('Voice recognition not supported in your browser', 'danger');
            return;
        }
        
        this.recognition = new SpeechRecognition();
        this.recognition.lang = 'en-US';
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.maxAlternatives = 3;
        
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateButtonState('listening');
            console.log('Voice recognition started...');
            this.showVoiceMessage('🎤 Listening... Speak a command', 'info');
        };
        
        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            if (finalTranscript) {
                this.transcript = finalTranscript.toLowerCase().trim();
                console.log('Final Transcript:', this.transcript);
                this.processVoiceCommand(this.transcript);
            } else if (interimTranscript) {
                console.log('Interim:', interimTranscript);
            }
        };
        
        this.recognition.onerror = (event) => {
            console.error('Voice recognition error:', event.error);
            let message = 'Voice error occurred';
            
            switch(event.error) {
                case 'no-speech':
                    message = 'No speech detected. Try again.';
                    break;
                case 'audio-capture':
                    message = 'Microphone not found. Please check permissions.';
                    break;
                case 'not-allowed':
                    message = 'Microphone permission denied. Please allow access.';
                    break;
                case 'network':
                    message = 'Network error. Please check your connection.';
                    break;
                default:
                    message = `Error: ${event.error}`;
            }
            
            this.showVoiceMessage(message, 'danger');
            this.updateButtonState('idle');
        };
        
        this.recognition.onend = () => {
            this.isListening = false;
            this.updateButtonState('idle');
            // Auto-restart if still in listening mode
            if (this.autoRestart) {
                setTimeout(() => {
                    if (this.isListening) this.startListening();
                }, 500);
            }
        };
    }

    startListening() {
        if (!this.recognition) {
            this.showVoiceMessage('Voice recognition not supported in your browser', 'danger');
            return;
        }
        
        if (this.isListening) {
            this.recognition.stop();
            return;
        }
        
        try {
            this.transcript = '';
            this.recognition.start();
        } catch (e) {
            console.error('Error starting recognition:', e);
        }
    }

    // Toggle continuous listening mode
    toggleContinuous() {
        this.autoRestart = !this.autoRestart;
        this.showVoiceMessage(this.autoRestart ? 'Continuous mode ON' : 'Continuous mode OFF', 
            this.autoRestart ? 'success' : 'info');
    }

    // Text to Speech - speak the response
    speak(text) {
        if (!this.synthesis) return;
        
        // Cancel any ongoing speech
        this.synthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        
        // Try to get a natural voice
        const voices = this.synthesis.getVoices();
        const preferredVoice = voices.find(v => v.lang.includes('en-US') && v.name.includes('Google'));
        if (preferredVoice) utterance.voice = preferredVoice;
        
        this.synthesis.speak(utterance);
    }

    processVoiceCommand(transcript) {
        console.log('Processing command:', transcript);
        
        // Check current page
        const currentPath = window.location.pathname;
        
        // Login page voice commands
        if (currentPath.includes('login')) {
            this.handleLoginVoiceCommands(transcript);
        }
        // Dashboard voice commands
        else if (currentPath.includes('dashboard')) {
            this.handleDashboardVoiceCommands(transcript);
        }
        // Home page voice commands
        else {
            this.handleHomeVoiceCommands(transcript);
        }
    }

    handleLoginVoiceCommands(transcript) {
        // Command: "login with [username] [password]" or "authenticate [username] [password]"
        if (transcript.includes('login') || transcript.includes('authenticate') || transcript.includes('sign in')) {
            // Try to extract username and password
            const usernameMatch = transcript.match(/(?:username|user|name)\s+(?:is\s+)?(\w+)/i);
            const passwordMatch = transcript.match(/(?:password|pass)\s+(?:is\s+)?(\w+)/i);
            
            if (usernameMatch && passwordMatch) {
                const username = usernameMatch[1];
                const password = passwordMatch[1];
                this.submitLoginForm(username, password);
                return;
            }
            
            this.showVoiceMessage('Say: "login with username [name] password [pass]"', 'info');
            this.speak('Please say: login with username, then your username, then password, then your password');
        }
    }

    handleHomeVoiceCommands(transcript) {
        // Navigation commands
        if (transcript.includes('login') || transcript.includes('sign in') || transcript.includes('go to login')) {
            this.showVoiceMessage('Navigating to login...', 'success');
            this.speak('Opening login page');
            setTimeout(() => window.location.href = '/login', 800);
            return;
        }
        
        if (transcript.includes('dashboard') || transcript.includes('go to dashboard') || transcript.includes('go to the dashboard')) {
            this.showVoiceMessage('Opening Dashboard...', 'success');
            this.speak('Opening the dashboard');
            setTimeout(() => window.location.href = '/dashboard', 800);
            return;
        }
        
        // Check AQI - get current air quality
        if (transcript.includes('aqi') || transcript.includes('air quality') || transcript.includes('pollution') || transcript.includes('how is the air')) {
            this.handleHomeAQI();
            return;
        }
        
        // Weather commands
        if (transcript.includes('weather') || transcript.includes('temperature') || transcript.includes('how is the weather')) {
            this.handleHomeWeather();
            return;
        }
        
        // Location commands
        if (transcript.includes('location') || transcript.includes('where')) {
            this.showHomeLocation();
            return;
        }
        
        // Theme commands
        if (transcript.includes('dark mode') || transcript.includes('light mode') || transcript.includes('theme')) {
            const themeBtn = document.getElementById('themeToggle');
            if (themeBtn) {
                themeBtn.click();
                this.showVoiceMessage('Theme changed!', 'success');
                this.speak('Theme changed');
            }
            return;
        }
        
        // Help - show all commands
        if (transcript.includes('help') || transcript.includes('commands') || transcript.includes('what can you do')) {
            this.showHomeVoiceHelp();
            return;
        }
        
        // Subscribe newsletter
        if (transcript.includes('subscribe') || transcript.includes('newsletter') || transcript.includes('sign up')) {
            this.showVoiceMessage('Scroll down to subscribe to our newsletter!', 'info');
            this.speak('Scroll down to subscribe to our newsletter');
            document.getElementById('newsletterEmail')?.scrollIntoView({ behavior: 'smooth' });
            return;
        }
        
        // Scroll commands
        if (transcript.includes('scroll down') || transcript.includes('more')) {
            window.scrollBy({ top: 500, behavior: 'smooth' });
            this.showVoiceMessage('Scrolling down...', 'info');
            return;
        }
        
        if (transcript.includes('scroll up') || transcript.includes('top')) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            this.showVoiceMessage('Scrolling to top...', 'info');
            return;
        }
        
        // Features info
        if (transcript.includes('feature') || transcript.includes('specification') || transcript.includes('what do you do')) {
            this.showVoiceMessage('Features: Real-time AQI, AI Predictions, Safe Routes, and Live Maps!', 'info');
            this.speak('Our features include real time air quality monitoring, AI predictions, safe route planning, and interactive maps');
            document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
            return;
        }
        
        // Contact info
        if (transcript.includes('contact') || transcript.includes('support') || transcript.includes('help')) {
            this.showVoiceMessage('Contact info at the bottom of the page!', 'info');
            this.speak('Contact information is at the bottom of the page');
            document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' });
            return;
        }
        
        // Default - show what user can say
        this.showHomeVoiceHelp();
    }

    handleHomeAQI() {
        const aqiEl = document.getElementById('liveAQI');
        if (aqiEl && aqiEl.textContent && aqiEl.textContent !== '---') {
            const aqi = aqiEl.textContent;
            let quality = '';
            let advice = '';
            
            const aqiNum = parseInt(aqi);
            if (aqiNum <= 50) {
                quality = 'Good';
                advice = 'Air quality is excellent. Perfect for outdoor activities!';
            } else if (aqiNum <= 100) {
                quality = 'Moderate';
                advice = 'Air quality is acceptable. Sensitive individuals may experience minor effects.';
            } else if (aqiNum <= 150) {
                quality = 'Unhealthy for Sensitive Groups';
                advice = 'Sensitive people should limit outdoor activities.';
            } else if (aqiNum <= 200) {
                quality = 'Unhealthy';
                advice = 'Everyone may experience health effects. Avoid outdoor exercises.';
            } else if (aqiNum <= 300) {
                quality = 'Very Unhealthy';
                advice = 'Health warnings of emergency conditions. Stay indoors.';
            } else {
                quality = 'Hazardous';
                advice = 'Emergency warning! Everyone should stay indoors.';
            }
            
            this.showVoiceMessage(`Current AQI: ${aqi} - ${quality}`, 'info');
            this.speak(`Current air quality index is ${aqi}. ${quality}. ${advice}`);
        } else {
            this.showVoiceMessage('Loading AQI data... Try again in a moment!', 'info');
            this.speak('The air quality data is still loading. Please try again in a moment.');
        }
    }

    handleHomeWeather() {
        const tempEl = document.getElementById('temperature');
        const humidityEl = document.getElementById('humidity');
        const windEl = document.getElementById('wind');
        
        if (tempEl && tempEl.textContent && tempEl.textContent !== '--°C') {
            const temp = tempEl.textContent;
            const humidity = humidityEl ? humidityEl.textContent : '--';
            const wind = windEl ? windEl.textContent : '--';
            
            this.showVoiceMessage(`Weather: ${temp}, Humidity: ${humidity}, Wind: ${wind}`, 'info');
            this.speak(`Current temperature is ${temp}, humidity is ${humidity}, and wind speed is ${wind}`);
        } else {
            this.showVoiceMessage('Loading weather data...', 'info');
            this.speak('Weather data is loading. Please try again.');
        }
    }

    showHomeLocation() {
        // Try to get location from page
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude.toFixed(2);
                    const lon = position.coords.longitude.toFixed(2);
                    this.showVoiceMessage(`Your location: Latitude ${lat}, Longitude ${lon}`, 'info');
                    this.speak(`Your approximate location is latitude ${lat}, longitude ${lon}`);
                },
                () => {
                    this.showVoiceMessage('Using default location (Delhi, India)', 'info');
                    this.speak('Using default location in Delhi, India');
                }
            );
        }
    }

    showHomeVoiceHelp() {
        const helpText = `
🎤 VOICE COMMANDS:

🗺️ Navigation:
• "Go to Dashboard" - Open dashboard
• "Login" - Go to login page

🌬️ Info:
• "AQI" / "Air quality" - Current AQI
• "Weather" - Current weather
• "Location" - Your location

📱 Actions:
• "Dark mode" - Toggle theme
• "Scroll down" - View more
• "Subscribe" - Newsletter
• "Features" - View features
• "Contact" - Contact info

💡 Tip: Say "Help" anytime!
        `;
        
        this.showVoiceMessage(helpText, 'info');
        this.speak('You can navigate to dashboard, check air quality, weather, and more. Say help anytime to see all commands!');
    }

    handleDashboardVoiceCommands(transcript) {
        console.log('Processing dashboard command:', transcript);
        
        // ============ NAVIGATION COMMANDS ============
        if (transcript.includes('home') || transcript.includes('go home') || transcript.includes('go to home')) {
            this.showVoiceMessage('Going to home page...', 'success');
            this.speak('Going to home page');
            setTimeout(() => window.location.href = '/', 800);
            return;
        }
        
        if (transcript.includes('logout') || transcript.includes('sign out') || transcript.includes('log out')) {
            this.showVoiceMessage('Logging out...', 'success');
            this.speak('Logging out');
            setTimeout(() => window.location.href = '/logout', 800);
            return;
        }
        
        // ============ REFRESH COMMANDS ============
        if (transcript.includes('refresh') || transcript.includes('reload') || transcript.includes('update')) {
            this.handleRefresh();
            return;
        }
        
        // ============ LOCATION COMMANDS ============
        if (transcript.includes('location') || transcript.includes('where') || transcript.includes('place')) {
            if (transcript.includes('change') || transcript.includes('set') || transcript.includes('go to') || transcript.includes('navigate to')) {
                this.handleChangeLocation(transcript);
                return;
            }
            // Tell current location
            const locationEl = document.getElementById('locationName');
            if (locationEl) {
                const locationText = locationEl.textContent;
                this.showVoiceMessage('Current: ' + locationText, 'info');
                this.speak('Your current location is ' + locationText);
            }
            return;
        }
        
        // ============ AQI COMMANDS ============
        if (transcript.includes('aqi') || transcript.includes('air quality') || transcript.includes('pollution')) {
            this.handleAQICommand(transcript);
            return;
        }
        
        // ============ WEATHER COMMANDS ============
        if (transcript.includes('weather') || transcript.includes('temperature') || transcript.includes('humidity') || transcript.includes('wind')) {
            this.handleWeatherCommand(transcript);
            return;
        }
        
        // ============ MAP COMMANDS ============
        if (transcript.includes('map') || transcript.includes('show map')) {
            this.showVoiceMessage('Showing pollution map...', 'success');
            this.speak('Showing the pollution map');
            document.getElementById('map')?.scrollIntoView({ behavior: 'smooth' });
            return;
        }
        
        // ============ HISTORY COMMANDS ============
        if (transcript.includes('history') || transcript.includes('chart') || transcript.includes('graph') || transcript.includes('trend')) {
            this.showVoiceMessage('Showing AQI history...', 'success');
            this.speak('Showing the AQI history chart');
            const historyCard = document.querySelector('.card h2');
            if (historyCard && historyCard.textContent.includes('History')) {
                historyCard.scrollIntoView({ behavior: 'smooth' });
            }
            return;
        }
        
        // ============ ROUTE COMMANDS ============
        if (transcript.includes('route') || transcript.includes('direction') || transcript.includes('navigate')) {
            this.handleRouteCommand(transcript);
            return;
        }
        
        // ============ ALERTS COMMANDS ============
        if (transcript.includes('alert') || transcript.includes('warning')) {
            const alertEl = document.getElementById('alertMessage');
            if (alertEl) {
                const alertText = alertEl.textContent;
                this.showVoiceMessage('Alert: ' + alertText, 'warning');
                this.speak('Current alert: ' + alertText);
            }
            return;
        }
        
        // ============ MASK & HEALTH COMMANDS ============
        if (transcript.includes('mask') || transcript.includes('health') || transcript.includes('exercise') || transcript.includes('purifier')) {
            this.handleHealthCommand();
            return;
        }
        
        // ============ PREDICTION COMMANDS ============
        if (transcript.includes('predict') || transcript.includes('forecast') || transcript.includes('tomorrow') || transcript.includes('future')) {
            const predEl = document.getElementById('predictedAQI');
            if (predEl) {
                const predText = predEl.textContent;
                this.showVoiceMessage('Predicted AQI: ' + predText, 'info');
                this.speak('The predicted air quality index is ' + predText);
            }
            return;
        }
        
        // ============ HELP COMMAND ============
        if (transcript.includes('help') || transcript.includes('what can you do') || transcript.includes('commands')) {
            this.showVoiceCommandsList();
            return;
        }
        
        // ============ THEME COMMANDS ============
        if (transcript.includes('dark mode') || transcript.includes('light mode') || transcript.includes('theme')) {
            const themeBtn = document.getElementById('themeToggle');
            if (themeBtn) {
                themeBtn.click();
                this.showVoiceMessage('Theme toggled', 'success');
                this.speak('Theme changed');
            }
            return;
        }
        
        // ============ SCROLL COMMANDS ============
        if (transcript.includes('scroll up')) {
            window.scrollBy({ top: -300, behavior: 'smooth' });
            this.showVoiceMessage('Scrolling up', 'info');
            return;
        }
        if (transcript.includes('scroll down')) {
            window.scrollBy({ top: 300, behavior: 'smooth' });
            this.showVoiceMessage('Scrolling down', 'info');
            return;
        }
        
        // ============ STOP/LISTEN CONTROL ============
        if (transcript.includes('stop') || transcript.includes('pause')) {
            this.showVoiceMessage('Voice paused', 'info');
            this.autoRestart = false;
            return;
        }
        
        // ============ CONTINUOUS MODE ============
        if (transcript.includes('keep listening') || transcript.includes('continuous')) {
            this.toggleContinuous();
            return;
        }
        
        // Default - show help
        this.showVoiceMessage('Command not recognized. Say "help" for available commands.', 'info');
    }

    handleRefresh() {
        this.showVoiceMessage('Refreshing data...', 'success');
        this.speak('Refreshing air quality data');
        
        // Trigger refresh
        const refreshBtn = document.getElementById('refreshLocation');
        if (refreshBtn) {
            refreshBtn.click();
        }
        
        // Also try socket update
        if (typeof socket !== 'undefined' && window.currentLat && window.currentLon) {
            socket.emit('request_update', { lat: window.currentLat, lon: window.currentLon });
        }
    }

    handleAQICommand(transcript) {
        const aqiEl = document.getElementById('currentAQI');
        const categoryEl = document.getElementById('aqiCategory');
        
        if (aqiEl && categoryEl) {
            const aqi = aqiEl.textContent;
            const category = categoryEl.textContent;
            
            this.showVoiceMessage(`Current AQI: ${aqi} - ${category}`, 'info');
            
            // Provide more details based on AQI level
            let advice = '';
            const aqiNum = parseInt(aqi);
            if (aqiNum <= 50) {
                advice = 'Air quality is good. Perfect for outdoor activities!';
            } else if (aqiNum <= 100) {
                advice = 'Air quality is moderate. Sensitive people should limit outdoor activities.';
            } else if (aqiNum <= 150) {
                advice = 'Unhealthy for sensitive groups. Consider wearing a mask outdoors.';
            } else if (aqiNum <= 200) {
                advice = 'Air quality is unhealthy. Avoid outdoor exercises.';
            } else if (aqiNum <= 300) {
                advice = 'Very unhealthy. Stay indoors and use air purifier.';
            } else {
                advice = 'Hazardous conditions! Emergency warnings in effect.';
            }
            
            this.speak(`Current air quality index is ${aqi}. ${category}. ${advice}`);
        } else {
            this.showVoiceMessage('AQI data not available', 'danger');
        }
    }

    handleWeatherCommand(transcript) {
        const tempEl = document.getElementById('weatherTemp');
        const humidityEl = document.getElementById('weatherHumidity');
        const windEl = document.getElementById('weatherWind');
        
        if (tempEl && humidityEl && windEl) {
            const temp = tempEl.textContent;
            const humidity = humidityEl.textContent;
            const wind = windEl.textContent;
            
            let weatherInfo = '';
            if (transcript.includes('temperature') || transcript.includes('temp')) {
                weatherInfo = `Temperature is ${temp}`;
            } else if (transcript.includes('humidity') || transcript.includes('humid')) {
                weatherInfo = `Humidity is ${humidity}`;
            } else if (transcript.includes('wind')) {
                weatherInfo = `Wind speed is ${wind}`;
            } else {
                weatherInfo = `Temperature ${temp}, Humidity ${humidity}, Wind ${wind}`;
            }
            
            this.showVoiceMessage(weatherInfo, 'info');
            this.speak(weatherInfo);
        }
    }

    handleHealthCommand() {
        const maskEl = document.getElementById('maskAdvice');
        const exerciseEl = document.getElementById('exerciseAdvice');
        const purifierEl = document.getElementById('purifierAdvice');
        
        if (maskEl && exerciseEl && purifierEl) {
            const mask = maskEl.textContent;
            const exercise = exerciseEl.textContent;
            const purifier = purifierEl.textContent;
            
            const healthInfo = `Mask: ${mask}, Exercise: ${exercise}, Air Purifier: ${purifier}`;
            this.showVoiceMessage(healthInfo, 'info');
            this.speak(`Health advice: Mask needed ${mask}. Outdoor exercise ${exercise}. Air purifier ${purifier}.`);
        }
    }

    handleRouteCommand(transcript) {
        // Scroll to route section
        const routeCard = document.querySelector('.card h2');
        if (routeCard && routeCard.textContent.includes('Route')) {
            routeCard.scrollIntoView({ behavior: 'smooth' });
            this.showVoiceMessage('Route planner opened. Say a city name to navigate.', 'success');
            this.speak('Route planner is now open. Select your start and destination to find the safest route.');
        }
        
        // Check for specific city commands
        const cities = ['chennai', 'coimbatore', 'madurai', 'trichy', 'sivakasi', 'ooty', 'kanyakumari', 'vellore'];
        for (const city of cities) {
            if (transcript.includes(city)) {
                this.showVoiceMessage(`Planning route to ${city}...`, 'info');
                // Could auto-select city here
                break;
            }
        }
    }

    handleChangeLocation(transcript) {
        // Extract city name from transcript
        const cityMatch = transcript.match(/(?:to|in|at)\s+(\w+)/i);
        if (cityMatch) {
            const city = cityMatch[1];
            this.showVoiceMessage(`Changing location to ${city}...`, 'success');
            this.speak(`Searching for ${city}`);
            
            // Trigger the correct location function
            const correctBtn = document.getElementById('correctLocation');
            if (correctBtn) {
                // Store the city name for the prompt
                window.pendingLocation = city;
                correctBtn.click();
            }
        } else {
            this.showVoiceMessage('Say "change location to [city name]"', 'info');
            this.speak('Please say the city name you want to navigate to');
            
            // Open the location correction
            const correctBtn = document.getElementById('correctLocation');
            if (correctBtn) correctBtn.click();
        }
    }

    showVoiceCommandsList() {
        const commands = `
🎤 AVAILABLE VOICE COMMANDS:

📍 Location:
- "Where am I" / "my location"
- "Change location to [city name]"

🌬️ Air Quality:
- "What is AQI" / "air quality"
- "Tell me pollution level"

🌡️ Weather:
- "Temperature" / "weather"
- "Humidity" / "wind"

🗺️ Navigation:
- "Go to home" / "logout"
- "Show map" / "show history"

🔄 Actions:
- "Refresh" / "update data"
- "Plan route" / "find directions"

💚 Health:
- "Do I need mask"
- "Can I exercise outside"

🌙 Theme:
- "Dark mode" / "light mode"

❓ Other:
- "Help" / "commands"
- "Scroll up" / "scroll down"
        `;
        
        this.showVoiceMessage(commands, 'info');
        this.speak('Here are the available voice commands. Check the screen for full list.');
    }

    submitLoginForm(username, password) {
        const form = document.querySelector('form[method="post"]');
        if (form) {
            const usernameInput = form.querySelector('input[name="username"]');
            const passwordInput = form.querySelector('input[name="password"]');
            
            if (usernameInput && passwordInput) {
                usernameInput.value = username;
                passwordInput.value = password;
                
                this.showVoiceMessage(`Logging in as ${username}...`, 'success');
                this.speak(`Logging in as ${username}`);
                setTimeout(() => form.submit(), 800);
            }
        }
    }

    updateButtonState(state) {
        const btn = document.getElementById('voiceAuthBtn');
        if (!btn) return;
        
        if (state === 'listening') {
            btn.classList.add('listening');
            btn.innerHTML = '<i class="fas fa-microphone-slash"></i> Listening...';
        } else {
            btn.classList.remove('listening');
            btn.innerHTML = '<i class="fas fa-microphone"></i> Voice';
        }
    }

    showVoiceMessage(message, type = 'info') {
        let container = document.getElementById('voiceMessageContainer');
        
        if (!container) {
            container = document.createElement('div');
            container.id = 'voiceMessageContainer';
            container.style.cssText = `
                position: fixed;
                top: 80px;
                left: 50%;
                transform: translateX(-50%);
                z-index: 10000;
                max-width: 450px;
                width: 90%;
            `;
            document.body.appendChild(container);
        }
        
        const msg = document.createElement('div');
        msg.className = `voice-message voice-message-${type}`;
        msg.innerHTML = message.replace(/\n/g, '<br>');
        msg.style.cssText = `
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            animation: slideDown 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            text-align: left;
        `;
        
        if (type === 'success') {
            msg.style.background = 'linear-gradient(135deg, #48bb78, #38a169)';
            msg.style.color = 'white';
        } else if (type === 'danger') {
            msg.style.background = 'linear-gradient(135deg, #f56565, #e53e3e)';
            msg.style.color = 'white';
        } else if (type === 'warning') {
            msg.style.background = 'linear-gradient(135deg, #ed8936, #dd6b20)';
            msg.style.color = 'white';
        } else {
            msg.style.background = 'linear-gradient(135deg, #667eea, #764ba2)';
            msg.style.color = 'white';
        }
        
        container.appendChild(msg);
        
        // Auto remove
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            msg.style.transition = 'all 0.3s ease-out';
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    }
}

// Add CSS animation if not exists
const voiceStyle = document.createElement('style');
voiceStyle.textContent = `
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(voiceStyle);

// Initialize when DOM is ready
function initVoiceAuth() {
    window.voiceAuth = new VoiceAuthentication();
    
    // Attach click handler to voice auth button with long-press detection
    const voiceBtn = document.getElementById('voiceAuthBtn');
    if (voiceBtn) {
        // Remove any existing listeners
        const newBtn = voiceBtn.cloneNode(true);
        voiceBtn.parentNode.replaceChild(newBtn, voiceBtn);
        
        let pressTimer;
        const LONG_PRESS_DURATION = 800; // 800ms for long press
        
        // Mouse down - start timer
        newBtn.addEventListener('mousedown', (e) => {
            pressTimer = setTimeout(() => {
                // Long press - show commands card
                if (typeof showVoiceCommands === 'function') {
                    showVoiceCommands();
                    window.voiceAuth.showVoiceMessage('🎤 Voice Commands opened!', 'info');
                }
            }, LONG_PRESS_DURATION);
        });
        
        // Mouse up - cancel timer if short press
        newBtn.addEventListener('mouseup', (e) => {
            clearTimeout(pressTimer);
            if (!newBtn.dataset.longPressed) {
                // Short press - start voice listening
                e.preventDefault();
                window.voiceAuth.startListening();
            }
            newBtn.dataset.longPressed = '';
        });
        
        // Mouse leave - cancel timer
        newBtn.addEventListener('mouseleave', () => {
            clearTimeout(pressTimer);
        });
        
        // Touch events for mobile
        newBtn.addEventListener('touchstart', (e) => {
            pressTimer = setTimeout(() => {
                newBtn.dataset.longPressed = 'true';
                if (typeof showVoiceCommands === 'function') {
                    showVoiceCommands();
                    window.voiceAuth.showVoiceMessage('🎤 Voice Commands opened!', 'info');
                }
            }, LONG_PRESS_DURATION);
        });
        
        newBtn.addEventListener('touchend', (e) => {
            clearTimeout(pressTimer);
            if (!newBtn.dataset.longPressed) {
                e.preventDefault();
                window.voiceAuth.startListening();
            }
            setTimeout(() => { delete newBtn.dataset.longPressed; }, 100);
        });
    }
    
    // Add keyboard shortcut: Press V for voice
    document.addEventListener('keydown', (e) => {
        if (e.key === 'v' && !e.ctrlKey && !e.metaKey && !e.altKey && 
            document.activeElement.tagName !== 'INPUT' && 
            document.activeElement.tagName !== 'TEXTAREA') {
            window.voiceAuth.startListening();
        }
        
        // Press ? to show help
        if (e.key === '?' || (e.shiftKey && e.key === '/')) {
            if (typeof showVoiceCommands === 'function') {
                showVoiceCommands();
            }
        }
    });
    
    console.log('Voice Authentication initialized with long-press support');
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVoiceAuth);
} else {
    initVoiceAuth();
}
