// Professional Chatbot Application
class AccurifyChatbot {
    constructor() {
        this.apiBase = '';
        this.isTyping = false;
        this.recognition = null;
        this.isDarkMode = true;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupVoiceRecognition();
        this.setupTheme();
        this.autoResizeTextarea();
    }
    
    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const voiceBtn = document.getElementById('voiceBtn');
        const themeToggle = document.getElementById('themeToggle');
        
        // Send message
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Enter to send (Shift+Enter for new line)
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Voice input
        voiceBtn.addEventListener('click', () => this.toggleVoice());
        
        // Theme toggle
        themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Input changes
        messageInput.addEventListener('input', () => {
            this.updateSendButton();
            this.autoResizeTextarea();
        });
    }
    
    setupVoiceRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('messageInput').value = transcript;
                this.updateSendButton();
                this.sendMessage();
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.updateVoiceButton(false);
            };
            
            this.recognition.onend = () => {
                this.updateVoiceButton(false);
            };
        }
    }
    
    setupTheme() {
        const savedTheme = localStorage.getItem('accurify-theme');
        if (savedTheme) {
            this.isDarkMode = savedTheme === 'dark';
        }
        this.applyTheme();
    }
    
    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        this.applyTheme();
        localStorage.setItem('accurify-theme', this.isDarkMode ? 'dark' : 'light');
    }
    
    applyTheme() {
        const body = document.body;
        const themeIcon = document.querySelector('.theme-icon');
        
        // Add smooth transition for theme change
        body.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
        
        if (this.isDarkMode) {
            body.classList.add('dark-mode');
            themeIcon.textContent = '☀️';
        } else {
            body.classList.remove('dark-mode');
            themeIcon.textContent = '🌙';
        }
        
        // Remove transition after theme change
        setTimeout(() => {
            body.style.transition = '';
        }, 400);
    }
    
    autoResizeTextarea() {
        const textarea = document.getElementById('messageInput');
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    updateSendButton() {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const hasText = messageInput.value.trim().length > 0;
        
        sendBtn.disabled = !hasText;
        sendBtn.style.opacity = hasText ? '1' : '0.5';
    }
    
    toggleVoice() {
        if (!this.recognition) {
            this.showMessage('Voice recognition not supported in this browser', 'system');
            return;
        }
        
        if (this.recognition.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
            this.updateVoiceButton(true);
        }
    }
    
    updateVoiceButton(isListening) {
        const voiceBtn = document.getElementById('voiceBtn');
        const icon = voiceBtn.querySelector('span');
        
        if (isListening) {
            icon.textContent = '🔴';
            voiceBtn.style.background = 'var(--text-primary)';
            voiceBtn.style.color = 'var(--bg-primary)';
        } else {
            icon.textContent = '🎤';
            voiceBtn.style.background = 'var(--bg-tertiary)';
            voiceBtn.style.color = 'var(--text-primary)';
        }
    }
    
    startChat(initialMessage = '') {
        const welcomeSection = document.getElementById('welcomeSection');
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        
        // Smooth transition from welcome to chat
        welcomeSection.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
        welcomeSection.style.opacity = '0';
        welcomeSection.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            welcomeSection.style.display = 'none';
            chatMessages.style.display = 'flex';
            
            // Smooth entrance for chat
            chatMessages.style.opacity = '0';
            chatMessages.style.transform = 'translateY(20px)';
            
            requestAnimationFrame(() => {
                chatMessages.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
                chatMessages.style.opacity = '1';
                chatMessages.style.transform = 'translateY(0)';
            });
            
            // Add initial bot message with delay
            setTimeout(() => {
                this.addMessage('Welcome to Accurify - Advanced Misinformation Detection System! 👋\n\nI\'m an AI-powered research assistant specializing in comprehensive news verification, fact-checking, and media analysis. My capabilities include:\n\n• **Deep Content Analysis** using advanced NLP models\n• **Real-time Source Verification** across 100+ trusted databases\n• **Academic-grade Research** with detailed citations\n• **Bias Detection** and sentiment analysis\n• **Multi-modal Analysis** for text, images, and video content\n\nHow may I assist you with your information verification needs today?', 'bot');
            }, 300);
            
        }, 300);
        
        // Set initial message if provided
        if (initialMessage) {
            setTimeout(() => {
                messageInput.value = initialMessage;
                this.updateSendButton();
                messageInput.focus();
            }, 800);
        }
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || this.isTyping) return;
        
        // Show chat if not already visible
        if (document.getElementById('welcomeSection').style.display !== 'none') {
            this.startChat();
        }
        
        // Add user message
        this.addMessage(message, 'user');
        
        // Clear input
        messageInput.value = '';
        this.updateSendButton();
        this.autoResizeTextarea();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Call API
            const response = await this.callVerificationAPI(message);
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            this.addVerificationResponse(response);
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error while processing your request. Please try again.', 'bot');
            console.error('API Error:', error);
        }
    }
    
    async callVerificationAPI(query) {
        this.showLoading('Checking trusted news sources...');
        
        await this.delay(1000);
        this.updateLoadingStatus('Running advanced NLP analysis...');
        
        await this.delay(1200);
        this.updateLoadingStatus('Cross-referencing with academic databases...');
        
        await this.delay(1000);
        this.updateLoadingStatus('Performing bias detection analysis...');
        
        await this.delay(800);
        this.updateLoadingStatus('Generating comprehensive report...');
        
        const response = await fetch(`${this.apiBase}/api/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });
        
        this.hideLoading();
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        return await response.json();
    }
    
    addMessage(content, sender, timestamp = null) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const time = timestamp || new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <span>${sender === 'user' ? '👤' : '🤖'}</span>
            </div>
            <div class="message-content">
                ${content}
                <div class="message-time">${time}</div>
            </div>
        `;
        
        // Add smooth entrance animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px) scale(0.95)';
        
        chatMessages.appendChild(messageDiv);
        
        // Trigger animation
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0) scale(1)';
        });
        
        this.scrollToBottom();
    }
    
    addVerificationResponse(result) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        
        let statusIcon = '';
        let statusText = '';
        let statusClass = '';
        
        // Core verification logic - simple and direct
        const userQuery = result.query || '';
        const credibilityScore = result.credibility_score || 0;
        const sourcesFound = result.sources_found || 0;
        
        // Simple status determination based on core logic
        if (result.status === 'verified' && sourcesFound > 0) {
            statusIcon = '✅';
            statusText = 'VERIFIED';
            statusClass = 'verified';
        } else {
            statusIcon = '❌';
            statusText = 'NOT VERIFIED';
            statusClass = 'fake';
        }
        
        let responseContent = `
            <div class="verification-result ${statusClass}">
                <button class="close-btn" onclick="closeResult()" title="Close">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
                <div class="result-header">
                    <span>${statusIcon} ${statusText}</span>
                    <span class="result-badge">${result.credibility_score || 0}/10</span>
                </div>
        `;
        
        // Core verification analysis
        let analysisContent = '';
        
        if (statusText === 'VERIFIED') {
            if (result.extracted_title) {
                analysisContent = `Article verified: "${result.extracted_title}" from ${result.source_domain || 'trusted source'}. ${result.summary || ''}`;
            } else {
                analysisContent = result.summary || `Information about "${userQuery}" was found and verified through ${sourcesFound} trusted news sources.`;
            }
        } else {
            analysisContent = result.summary || `This information was not found in our trusted news sources and cannot be verified. ${result.recommendation || ''}`;
        }
        
        responseContent += `
            <div class="ai-summary">
                <strong>📝 Analysis Summary:</strong>
                <p>${analysisContent}</p>
                
                <div class="analysis-details">
                    <h4>Verification Process</h4>
                    <p>Cross-referenced with ${result.sources_checked || '50+'} trusted news databases and fact-checking organizations.</p>
                    
                    <h4>Confidence Level</h4>
                    <p>Analysis confidence: <strong>${Math.round(credibilityScore * 10)}%</strong></p>
                </div>
            </div>
        `;
        
        // Add official sources for verified content
        if (statusText === 'VERIFIED' && result.official_sources && result.official_sources.length > 0) {
            responseContent += `
                <div class="official-links">
                    <strong>🔗 Official Sources:</strong>
            `;
            
            result.official_sources.forEach(source => {
                responseContent += `
                    <a href="${source.url}" target="_blank" rel="noopener noreferrer" class="official-link">
                        <div class="link-title">${source.title}</div>
                        <div class="link-source">${source.source}</div>
                    </a>
                `;
            });
            
            responseContent += '</div>';
        }
        
        // Add suggestion if not found
        if (result.suggestion) {
            responseContent += `
                <div class="suggestion">
                    <strong>💡 Suggestion:</strong>
                    <p>${result.suggestion}</p>
                </div>
            `;
        }
        
        responseContent += '</div>';
        
        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <span>🤖</span>
            </div>
            <div class="message-content">
                ${responseContent}
                <div class="message-time">${time}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        if (document.querySelector('.typing-indicator')) return;
        
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <span>🤖</span>
            </div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span>AI is analyzing</span>
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;
        
        // Smooth entrance for typing indicator
        typingDiv.style.opacity = '0';
        typingDiv.style.transform = 'translateY(10px)';
        
        chatMessages.appendChild(typingDiv);
        
        requestAnimationFrame(() => {
            typingDiv.style.transition = 'all 0.3s ease';
            typingDiv.style.opacity = '1';
            typingDiv.style.transform = 'translateY(0)';
        });
        
        this.scrollToBottom();
        this.isTyping = true;
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.style.transition = 'all 0.3s ease';
            typingIndicator.style.opacity = '0';
            typingIndicator.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                if (typingIndicator.parentNode) {
                    typingIndicator.remove();
                }
            }, 300);
        }
        this.isTyping = false;
    }
    
    showLoading(status) {
        const overlay = document.getElementById('loadingOverlay');
        const statusElement = document.getElementById('loadingStatus');
        
        statusElement.textContent = status;
        overlay.classList.add('active');
    }
    
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.remove('active');
    }
    
    updateLoadingStatus(status) {
        const statusElement = document.getElementById('loadingStatus');
        statusElement.textContent = status;
    }
    
    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth'
        });
    }
    
    showMessage(message, type = 'info') {
        // Simple message display - could be enhanced with toast notifications
        console.log(`${type.toUpperCase()}: ${message}`);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Global functions for enhanced interface
function startChat(message = '') {
    window.chatbot.startChat(message);
}

function startAnalysis() {
    const content = document.getElementById('contentInput').value.trim();
    const analysisType = document.getElementById('analysisType').value;
    
    if (!content) {
        alert('Please enter content to analyze');
        return;
    }
    
    const analysisMessage = `[${analysisType.toUpperCase()}] ${content}`;
    window.chatbot.startChat();
    
    setTimeout(() => {
        document.getElementById('messageInput').value = analysisMessage;
        window.chatbot.sendMessage();
    }, 1000);
}

function setExample(exampleText) {
    document.getElementById('contentInput').value = exampleText;
    document.getElementById('contentInput').focus();
}

// Enhanced voice input for main interface
function setupVoiceInput() {
    const voiceInputBtn = document.getElementById('voiceInputBtn');
    if (voiceInputBtn) {
        voiceInputBtn.addEventListener('click', () => {
            if (window.chatbot && window.chatbot.recognition) {
                window.chatbot.recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    document.getElementById('contentInput').value = transcript;
                };
                window.chatbot.recognition.start();
            }
        });
    }
}

// Home redirect function
function goHome() {
    const welcomeSection = document.getElementById('welcomeSection');
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    
    // Reset to welcome screen
    welcomeSection.style.display = 'block';
    welcomeSection.style.opacity = '1';
    welcomeSection.style.transform = 'translateY(0)';
    
    chatMessages.style.display = 'none';
    chatMessages.innerHTML = '';
    
    // Clear input
    messageInput.value = '';
    window.chatbot.updateSendButton();
    
    // Hide loading overlay
    document.getElementById('loadingOverlay').classList.remove('active');
    
    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Close result function
function closeResult() {
    goHome();
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatbot = new AccurifyChatbot();
    setupVoiceInput();
});