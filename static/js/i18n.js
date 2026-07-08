/**
 * Internationalization (i18n) Module for AirPollutionAI
 * Handles language switching, translations, and text-to-speech
 */

class I18nManager {
    constructor() {
        this.currentLanguage = 'en';
        this.translations = {};
        this.languages = [
            { code: 'en', name: 'English', native: 'English', flag: '🇺🇸' },
            { code: 'hi', name: 'Hindi', native: 'हिंदी', flag: '🇮🇳' },
            { code: 'ta', name: 'Tamil', native: 'தமிழ்', flag: '🇮🇳' },
            { code: 'ml', name: 'Malayalam', native: 'മലയാളം', flag: '🇮🇳' },
            { code: 'te', name: 'Telugu', native: 'తెలుగు', flag: '🇮🇳' }
        ];
        this.speechSynthesis = window.speechSynthesis;
        this.initialized = false;
    }

    /**
     * Initialize the i18n system
     */
    async init() {
        // Load saved language preference or detect from browser
        const savedLang = this.getSavedLanguage();
        if (savedLang) {
            await this.setLanguage(savedLang, false);
        } else {
            // Try to detect browser language
            const browserLang = this.detectBrowserLanguage();
            await this.setLanguage(browserLang, false);
        }
        
        this.initialized = true;
        this.updatePageTranslations();
        console.log(`I18n initialized with language: ${this.currentLanguage}`);
    }

    /**
     * Get saved language from localStorage
     */
    getSavedLanguage() {
        return localStorage.getItem('airpollutionai_language');
    }

    /**
     * Save language preference
     */
    saveLanguage(lang) {
        localStorage.setItem('airpollutionai_language', lang);
    }

    /**
     * Detect browser language
     */
    detectBrowserLanguage() {
        const browserLang = navigator.language || navigator.userLanguage;
        const langCode = browserLang.split('-')[0];
        
        // Check if we support this language
        if (this.languages.some(l => l.code === langCode)) {
            return langCode;
        }
        return 'en';
    }

    /**
     * Set the current language
     * @param {string} lang - Language code (en, hi, ta, te)
     * @param {boolean} updateServer - Whether to update server session
     */
    async setLanguage(lang, updateServer = true) {
        if (!this.languages.some(l => l.code === lang)) {
            console.warn(`Language ${lang} not supported, falling back to English`);
            lang = 'en';
        }

        this.currentLanguage = lang;
        this.saveLanguage(lang);

        // Update server session if needed
        if (updateServer) {
            try {
                await fetch('/api/set-language', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ language: lang })
                });
            } catch (e) {
                console.warn('Could not update server language:', e);
            }
        }

        // Load translations for this language
        await this.loadTranslations(lang);

        // Update the page
        this.updatePageTranslations();
        this.updateVoiceRecognition();
        
        // Update language selector UI if exists
        this.updateLanguageSelector();
    }

    /**
     * Load translations for a specific language from server
     */
    async loadTranslations(lang) {
        try {
            const response = await fetch(`/api/translations?lang=${lang}`);
            if (response.ok) {
                this.translations = await response.json();
            } else {
                console.warn(`Failed to load translations for ${lang}`);
            }
        } catch (e) {
            console.warn('Could not load translations:', e);
        }
    }

    /**
     * Get translation for a key
     */
    t(key) {
        return this.translations[key] || key;
    }

    /**
     * Update all translatable elements on the page
     */
    updatePageTranslations() {
        // Update elements with data-i18n attribute
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.t(key);
            if (translation !== key) {
                element.textContent = translation;
            }
        });

        // Update elements with data-i18n-placeholder attribute
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            const translation = this.t(key);
            if (translation !== key) {
                element.placeholder = translation;
            }
        });

        // Update elements with data-i18n-title attribute
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            const translation = this.t(key);
            if (translation !== key) {
                element.title = translation;
            }
        });

        // Update document title if there's a translation
        const titleKey = document.body.getAttribute('data-page-title');
        if (titleKey) {
            const title = this.t(titleKey);
            if (title !== titleKey) {
                document.title = title + ' - AirPollutionAI';
            }
        }

        // Update voice recognition language
        this.updateVoiceRecognition();

        // Dispatch event for custom handlers
        document.dispatchEvent(new CustomEvent('languageChanged', { 
            detail: { language: this.currentLanguage } 
        }));
    }

    /**
     * Update voice recognition language
     */
    updateVoiceRecognition() {
        if (window.voiceAuth && window.voiceAuth.recognition) {
            const voiceCodes = {
                'en': 'en-US',
                'hi': 'hi-IN',
                'ta': 'ta-IN',
                'te': 'te-IN'
            };
            window.voiceAuth.recognition.lang = voiceCodes[this.currentLanguage] || 'en-US';
            console.log(`Voice recognition language set to: ${window.voiceAuth.recognition.lang}`);
        }
    }

    /**
     * Create and add language selector to the navbar
     */
    addLanguageSelectorToNavbar(navbarSelector = '.nav-links') {
        const navbar = document.querySelector(navbarSelector);
        if (!navbar) {
            console.warn('Navbar not found');
            return;
        }

        // Check if selector already exists
        if (document.getElementById('languageSelector')) {
            return;
        }

        const selector = document.createElement('div');
        selector.id = 'languageSelector';
        selector.className = 'language-selector';
        selector.style.cssText = `
            display: inline-flex;
            align-items: center;
            margin-left: 1rem;
            position: relative;
        `;

        // Create dropdown button
        const currentLang = this.languages.find(l => l.code === this.currentLanguage) || this.languages[0];
        selector.innerHTML = `
            <button class="lang-btn" style="
                background: transparent;
                border: 1px solid rgba(255,255,255,0.3);
                color: white;
                padding: 6px 12px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 6px;
            ">
                <span>${currentLang.flag}</span>
                <span class="lang-code">${currentLang.code.toUpperCase()}</span>
                <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
            </button>
            <div class="lang-dropdown" style="
                display: none;
                position: absolute;
                top: 100%;
                right: 0;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                min-width: 150px;
                z-index: 1000;
                overflow: hidden;
                margin-top: 5px;
            ">
                ${this.languages.map(lang => `
                    <button class="lang-option" data-lang="${lang.code}" style="
                        display: flex;
                        align-items: center;
                        gap: 8px;
                        width: 100%;
                        padding: 10px 15px;
                        border: none;
                        background: ${lang.code === this.currentLanguage ? '#f0f4ff' : 'white'};
                        color: #333;
                        cursor: pointer;
                        text-align: left;
                        font-size: 0.9rem;
                        transition: background 0.2s;
                    ">
                        <span>${lang.flag}</span>
                        <span>${lang.native}</span>
                    </button>
                `).join('')}
            </div>
        `;

        navbar.appendChild(selector);

        // Add event listeners
        const btn = selector.querySelector('.lang-btn');
        const dropdown = selector.querySelector('.lang-dropdown');

        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            dropdown.style.display = 'none';
        });

        // Handle language selection
        selector.querySelectorAll('.lang-option').forEach(option => {
            option.addEventListener('click', async (e) => {
                const lang = e.currentTarget.getAttribute('data-lang');
                await this.setLanguage(lang);
                dropdown.style.display = 'none';
            });
        });
    }

    /**
     * Update language selector UI
     */
    updateLanguageSelector() {
        const selector = document.getElementById('languageSelector');
        if (!selector) return;

        const currentLang = this.languages.find(l => l.code === this.currentLanguage) || this.languages[0];
        
        // Update button
        const btn = selector.querySelector('.lang-btn');
        btn.innerHTML = `
            <span>${currentLang.flag}</span>
            <span class="lang-code">${currentLang.code.toUpperCase()}</span>
            <i class="fas fa-chevron-down" style="font-size: 0.7rem;"></i>
        `;

        // Update dropdown options
        selector.querySelectorAll('.lang-option').forEach(option => {
            const isActive = option.getAttribute('data-lang') === this.currentLanguage;
            option.style.background = isActive ? '#f0f4ff' : 'white';
        });
    }

    /**
     * Speak text using text-to-speech
     */
    speak(text, lang = null) {
        if (!this.speechSynthesis) {
            console.warn('Speech synthesis not supported');
            return;
        }

        // Cancel any ongoing speech
        this.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang || this.currentLanguage;
        utterance.rate = 0.9;
        utterance.pitch = 1;

        this.speechSynthesis.speak(utterance);
    }

    /**
     * Speak the current AQI value
     */
    speakAQI(aqi, category) {
        const lang = this.currentLanguage;
        
        let message = '';
        if (lang === 'hi') {
            message = `वर्तमान वायु गुणवत्ता सूचकांक ${aqi} है। ${category}।`;
        } else if (lang === 'ta') {
            message = `தற்போதைய காற்று தரம் ${aqi} ஆகும். ${category}.`;
        } else if (lang === 'te') {
            message = `Currently AQI is ${aqi}. ${category}.`;
        } else {
            message = `Current air quality index is ${aqi}. ${category}.`;
        }

        this.speak(message);
    }

    /**
     * Get current language code
     */
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    /**
     * Get available languages
     */
    getLanguages() {
        return this.languages;
    }
}

// Create global instance
window.i18n = new I18nManager();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.i18n.init();
    });
} else {
    window.i18n.init();
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = I18nManager;
}
