/**
 * AirPollutionAI Chatbot - Meta AI Style
 * Sleek, modern chat interface inspired by Meta AI
 */

class AirPollutionChatbot {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.messages = [];
        this.quickQuestions = [];
        
        this.init();
    }
    
    init() {
        this.createChatButton();
        this.createChatWindow();
        this.loadQuickQuestions();
        this.loadChatHistory();
        this.bindEvents();
    }
    
    createChatButton() {
        // Meta AI style floating button - circular with gradient
        const btn = document.createElement('div');
        btn.id = 'meta-chatbot-btn';
        btn.innerHTML = `
            <div class="meta-avatar">
                <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
            </div>
            <span class="meta-dot" id="meta-chat-dot"></span>
        `;
        
        btn.style.cssText = `
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4);
            z-index: 9998;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        `;
        
        // Add hover effect
        const style = document.createElement('style');
        style.textContent = `
            #meta-chatbot-btn:hover {
                transform: scale(1.08);
                box-shadow: 0 6px 28px rgba(168, 85, 247, 0.5);
            }
            .meta-avatar {
                width: 32px;
                height: 32px;
                background: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #A855F7;
            }
            .meta-dot {
                position: absolute;
                top: 4px;
                right: 4px;
                width: 12px;
                height: 12px;
                background: #10B981;
                border-radius: 50%;
                border: 2px solid white;
                animation: meta-pulse 2s infinite;
                display: none;
            }
            @keyframes meta-pulse {
                0%, 100% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.1); opacity: 0.8; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(btn);
    }
    
    createChatWindow() {
        const window = document.createElement('div');
        window.id = 'meta-chat-window';
        window.innerHTML = `
            <!-- Meta AI Header -->
            <div class="meta-header">
                <div class="meta-header-left">
                    <div class="meta-header-avatar">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                        </svg>
                    </div>
                    <div class="meta-header-info">
                        <div class="meta-header-title">AirPollutionAI</div>
                        <div class="meta-header-status">
                            <span class="meta-status-dot"></span>
                            <span>Online</span>
                        </div>
                    </div>
                </div>
                <div class="meta-header-actions">
                    <button class="meta-action-btn" id="meta-clear-btn" title="New conversation">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                        </svg>
                    </button>
                    <button class="meta-action-btn" id="meta-minimize-btn" title="Minimize">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                            <path d="M19 13H5v-2h14v2z"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <!-- Chat Messages -->
            <div class="meta-messages" id="meta-messages">
                <div class="meta-welcome">
                    <div class="meta-welcome-avatar">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                        </svg>
                    </div>
                    <div class="meta-welcome-text">
                        <div class="meta-welcome-title">AirPollutionAI</div>
                        <div class="meta-welcome-desc">Ask me anything about air quality, weather, and pollution! 🌿</div>
                    </div>
                </div>
                <div class="meta-typing" id="meta-typing" style="display: none;">
                    <div class="meta-typing-dot"></div>
                    <div class="meta-typing-dot"></div>
                    <div class="meta-typing-dot"></div>
                </div>
            </div>
            
            <!-- Quick Questions -->
            <div class="meta-quick-questions" id="meta-quick-questions">
                <!-- Populated dynamically -->
            </div>
            
            <!-- Chat Input -->
            <div class="meta-input-container">
                <input type="text" id="meta-chat-input" placeholder="Ask AirPollutionAI..." autocomplete="off">
                <button id="meta-send-btn" class="meta-send-btn">
                    <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
        `;
        
        // Add all styles
        const style = document.createElement('style');
        style.textContent = `
            #meta-chat-window {
                position: fixed;
                bottom: 100px;
                right: 24px;
                width: 380px;
                height: 560px;
                background: #FFFFFF;
                border-radius: 20px;
                box-shadow: 0 8px 40px rgba(0,0,0,0.15);
                display: none;
                flex-direction: column;
                z-index: 9999;
                overflow: hidden;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                border: 1px solid rgba(0,0,0,0.08);
            }
            
            #meta-chat-window.open {
                display: flex;
                animation: meta-slide-up 0.3s ease-out;
            }
            
            @keyframes meta-slide-up {
                from { opacity: 0; transform: translateY(20px) scale(0.95); }
                to { opacity: 1; transform: translateY(0) scale(1); }
            }
            
            /* Meta Header */
            .meta-header {
                background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%);
                color: white;
                padding: 14px 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .meta-header-left {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .meta-header-avatar {
                width: 36px;
                height: 36px;
                background: white;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #A855F7;
            }
            
            .meta-header-info {
                display: flex;
                flex-direction: column;
            }
            
            .meta-header-title {
                font-weight: 600;
                font-size: 15px;
            }
            
            .meta-header-status {
                display: flex;
                align-items: center;
                gap: 5px;
                font-size: 12px;
                opacity: 0.9;
            }
            
            .meta-status-dot {
                width: 6px;
                height: 6px;
                background: #10B981;
                border-radius: 50%;
            }
            
            .meta-header-actions {
                display: flex;
                gap: 4px;
            }
            
            .meta-action-btn {
                background: rgba(255,255,255,0.2);
                border: none;
                color: white;
                cursor: pointer;
                padding: 8px;
                border-radius: 50%;
                transition: background 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .meta-action-btn:hover {
                background: rgba(255,255,255,0.3);
            }
            
            /* Messages */
            .meta-messages {
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                display: flex;
                flex-direction: column;
                gap: 12px;
                background: #F9FAFB;
            }
            
            .meta-welcome {
                display: flex;
                gap: 12px;
                padding: 12px;
                background: white;
                border-radius: 16px;
                margin-bottom: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            }
            
            .meta-welcome-avatar {
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                flex-shrink: 0;
            }
            
            .meta-welcome-text {
                display: flex;
                flex-direction: column;
            }
            
            .meta-welcome-title {
                font-weight: 600;
                font-size: 14px;
                color: #111;
                margin-bottom: 4px;
            }
            
            .meta-welcome-desc {
                font-size: 13px;
                color: #666;
                line-height: 1.4;
            }
            
            /* Message Bubbles */
            .meta-message {
                max-width: 85%;
                padding: 10px 14px;
                border-radius: 18px;
                font-size: 14px;
                line-height: 1.45;
                word-wrap: break-word;
            }
            
            .meta-message.user {
                align-self: flex-end;
                background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%);
                color: white;
                border-bottom-right-radius: 4px;
            }
            
            .meta-message.bot {
                align-self: flex-start;
                background: white;
                color: #111;
                border-bottom-left-radius: 4px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            }
            
            .meta-message-time {
                font-size: 10px;
                opacity: 0.7;
                margin-top: 4px;
                text-align: right;
            }
            
            /* Typing Indicator */
            .meta-typing {
                display: flex;
                gap: 4px;
                padding: 12px 16px;
                background: white;
                border-radius: 18px;
                align-self: flex-start;
                box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            }
            
            .meta-typing-dot {
                width: 8px;
                height: 8px;
                background: #A855F7;
                border-radius: 50%;
                animation: meta-typing-bounce 1.4s infinite;
            }
            
            .meta-typing-dot:nth-child(2) { animation-delay: 0.2s; }
            .meta-typing-dot:nth-child(3) { animation-delay: 0.4s; }
            
            @keyframes meta-typing-bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-6px); }
            }
            
            /* Quick Questions */
            .meta-quick-questions {
                padding: 12px;
                background: white;
                border-top: 1px solid #F3F4F6;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            
            .meta-quick-btn {
                background: #F3F4F6;
                border: none;
                padding: 8px 14px;
                border-radius: 20px;
                font-size: 13px;
                color: #374151;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .meta-quick-btn:hover {
                background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%);
                color: white;
            }
            
            /* Input */
            .meta-input-container {
                padding: 12px 16px;
                background: white;
                border-top: 1px solid #F3F4F6;
                display: flex;
                gap: 10px;
                align-items: center;
            }
            
            #meta-chat-input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #E5E7EB;
                border-radius: 24px;
                outline: none;
                font-size: 14px;
                transition: border-color 0.2s;
                background: #F9FAFB;
            }
            
            #meta-chat-input:focus {
                border-color: #A855F7;
                background: white;
            }
            
            .meta-send-btn {
                width: 42px;
                height: 42px;
                background: linear-gradient(135deg, #A855F7 0%, #6366F1 100%);
                border: none;
                border-radius: 50%;
                color: white;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s, box-shadow 0.2s;
                box-shadow: 0 2px 8px rgba(168, 85, 247, 0.3);
            }
            
            .meta-send-btn:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 12px rgba(168, 85, 247, 0.4);
            }
            
            .meta-send-btn:active {
                transform: scale(0.95);
            }
            
            /* Dark mode */
            body.dark-mode #meta-chat-window {
                background: #1F2937;
                border-color: #374151;
            }
            
            body.dark-mode .meta-messages {
                background: #111827;
            }
            
            body.dark-mode .meta-message.bot {
                background: #374151;
                color: #F3F4F6;
            }
            
            body.dark-mode .meta-welcome {
                background: #374151;
            }
            
            body.dark-mode .meta-welcome-title {
                color: #F3F4F6;
            }
            
            body.dark-mode .meta-welcome-desc {
                color: #9CA3AF;
            }
            
            body.dark-mode .meta-quick-questions {
                background: #1F2937;
                border-color: #374151;
            }
            
            body.dark-mode .meta-quick-btn {
                background: #374151;
                color: #D1D5DB;
            }
            
            body.dark-mode .meta-input-container {
                background: #1F2937;
                border-color: #374151;
            }
            
            body.dark-mode #meta-chat-input {
                background: #374151;
                border-color: #4B5563;
                color: #F3F4F6;
            }
            
            /* Mobile */
            @media (max-width: 480px) {
                #meta-chat-window {
                    width: calc(100% - 16px);
                    right: 8px;
                    bottom: 90px;
                    height: calc(100% - 110px);
                }
                
                #meta-chatbot-btn {
                    width: 54px;
                    height: 54px;
                    bottom: 16px;
                    right: 16px;
                }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(window);
    }
    
    bindEvents() {
        // Event delegation for better reliability
        document.addEventListener('click', (e) => {
            // Toggle chat
            if (e.target.closest('#meta-chatbot-btn')) {
                this.toggleChat();
            }
            // Minimize
            if (e.target.closest('#meta-minimize-btn')) {
                this.closeChat();
            }
            // Clear
            if (e.target.closest('#meta-clear-btn')) {
                this.clearChat();
            }
            // Send
            if (e.target.closest('#meta-send-btn')) {
                this.sendMessage();
            }
        });
        
        // Enter to send
        const chatInput = document.getElementById('meta-chat-input');
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }
    
    toggleChat() {
        const chatWindow = document.getElementById('meta-chat-window');
        const toggleBtn = document.getElementById('meta-chatbot-btn');
        
        if (this.isOpen) {
            chatWindow.classList.remove('open');
        } else {
            chatWindow.classList.add('open');
            // Focus input
            setTimeout(() => {
                document.getElementById('meta-chat-input').focus();
            }, 300);
        }
        
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            setTimeout(() => {
                const messagesContainer = document.getElementById('meta-messages');
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 100);
        }
    }
    
    closeChat() {
        const chatWindow = document.getElementById('meta-chat-window');
        chatWindow.classList.remove('open');
        this.isOpen = false;
    }
    
    async loadQuickQuestions() {
        try {
            const response = await fetch('/api/chat/quick-questions');
            const data = await response.json();
            this.quickQuestions = data.questions.slice(0, 8); // Limit to 8
            this.renderQuickQuestions();
        } catch (error) {
            this.quickQuestions = [
                "AQI in Delhi?",
                "Air quality in Mumbai?",
                "Weather in Chennai?",
                "Pollution in Bangalore?",
                "Safe to exercise?",
                "Need a mask?",
                "AQI in Coimbatore?",
                "Health tips"
            ];
            this.renderQuickQuestions();
        }
    }
    
    renderQuickQuestions() {
        const container = document.getElementById('meta-quick-questions');
        container.innerHTML = this.quickQuestions.map(q => {
            return `<button class="meta-quick-btn" data-msg="${encodeURIComponent(q)}">${q}</button>`;
        }).join('');
        
        container.querySelectorAll('.meta-quick-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = decodeURIComponent(btn.dataset.msg);
                this.sendQuickMessage(message);
            });
        });
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch('/api/chat/history');
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                const messagesContainer = document.getElementById('meta-messages');
                messagesContainer.innerHTML = '';
                
                data.history.forEach(msg => {
                    this.addMessage(msg.content, msg.role === 'user' ? 'user' : 'bot', false);
                });
            }
        } catch (error) {
            console.log('No chat history');
        }
    }
    
    sendQuickMessage(message) {
        const chatInput = document.getElementById('meta-chat-input');
        chatInput.value = message;
        this.sendMessage();
    }
    
    async sendMessage() {
        const chatInput = document.getElementById('meta-chat-input');
        const message = chatInput.value.trim();
        
        if (!message || this.isTyping) return;
        
        this.addMessage(message, 'user');
        chatInput.value = '';
        
        this.showTyping();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            this.hideTyping();
            this.addMessage(data.response, 'bot');
            
        } catch (error) {
            this.hideTyping();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }
    }
    
    addMessage(text, sender, animate = true) {
        const messagesContainer = document.getElementById('meta-messages');
        
        // Remove welcome
        const welcome = messagesContainer.querySelector('.meta-welcome');
        if (welcome) welcome.remove();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `meta-message ${sender}`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = `
            <div class="meta-message-content">${formattedText}</div>
            <div class="meta-message-time">${time}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        
        if (animate) {
            messageDiv.style.opacity = '0';
            messageDiv.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                messageDiv.style.transition = 'all 0.3s ease';
                messageDiv.style.opacity = '1';
                messageDiv.style.transform = 'translateY(0)';
            }, 10);
        }
        
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    showTyping() {
        this.isTyping = true;
        const typingIndicator = document.getElementById('meta-typing');
        typingIndicator.style.display = 'flex';
        
        const messagesContainer = document.getElementById('meta-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    hideTyping() {
        this.isTyping = false;
        const typingIndicator = document.getElementById('meta-typing');
        typingIndicator.style.display = 'none';
    }
    
    async clearChat() {
        try {
            await fetch('/api/chat/clear', { method: 'POST' });
            
            const messagesContainer = document.getElementById('meta-messages');
            messagesContainer.innerHTML = `
                <div class="meta-welcome">
                    <div class="meta-welcome-avatar">
                        <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                        </svg>
                    </div>
                    <div class="meta-welcome-text">
                        <div class="meta-welcome-title">AirPollutionAI</div>
                        <div class="meta-welcome-desc">Ask me anything about air quality, weather, and pollution! 🌿</div>
                    </div>
                </div>
                <div class="meta-typing" id="meta-typing" style="display: none;">
                    <div class="meta-typing-dot"></div>
                    <div class="meta-typing-dot"></div>
                    <div class="meta-typing-dot"></div>
                </div>
            `;
        } catch (error) {
            console.error('Error clearing chat:', error);
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new AirPollutionChatbot();
});

if (document.readyState === 'complete' || document.readyState === 'interactive') {
    window.chatbot = new AirPollutionChatbot();
}
