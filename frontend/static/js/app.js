// Trustify AI Frontend Application
class TrustifyApp {
    constructor() {
        this.apiBase = '';  // Same origin
        this.isListening = false;
        this.recognition = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupVoiceRecognition();
        this.startRotatingText();
        this.loadWelcomeMessage();
    }
    
    setupEventListeners() {
        // Send button
        const sendBtn = document.getElementById('sendBtn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        // Chat input
        const chatInput = document.getElementById('chatInput');
        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }
        
        // Voice button
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.toggleVoice());
        }
        
        // Example queries
        document.querySelectorAll('.example').forEach(example => {
            example.addEventListener('click', () => {
                const text = example.textContent;
                const chatInput = document.getElementById('chatInput');
                if (chatInput) {
                    chatInput.value = text;
                    this.sendMessage();
                }
            });
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
                const chatInput = document.getElementById('chatInput');
                if (chatInput) {
                    chatInput.value = transcript;
                    this.sendMessage(true); // true indicates voice input
                }
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
    
    toggleVoice() {
        if (!this.recognition) {
            alert('Speech recognition not supported in this browser');
            return;
        }
        
        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
            this.updateVoiceButton(true);
        }
    }
    
    updateVoiceButton(isListening) {
        this.isListening = isListening;
        const voiceBtn = document.getElementById('voiceBtn');
        if (voiceBtn) {
            voiceBtn.textContent = isListening ? '🔴' : '🎤';
            voiceBtn.style.background = isListening ? '#ff4757' : '#667eea';
        }
    }
    
    async sendMessage(isVoiceInput = false) {
        const chatInput = document.getElementById('chatInput');
        const message = chatInput?.value.trim();
        
        if (!message) return;
        
        // Add user message
        this.addMessage(message, 'user');
        chatInput.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Call API
            const response = await fetch(`${this.apiBase}/api/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Add verification result
            this.addVerificationResult(result);
            
            // Voice output if voice input was used
            if (isVoiceInput && 'speechSynthesis' in window) {
                this.speakResult(result);
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('❌ Sorry, I encountered an error. Please try again.', 'bot');
            console.error('API Error:', error);
        }
    }
    
    addMessage(content, sender) {
        const chatMessages = document.getElementById('chatMessages') || document.getElementById('fullChatMessages');
        if (!chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = content;
        
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Animate message appearance
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        
        requestAnimationFrame(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        });
    }
    
    addVerificationResult(result) {
        if (result.error) {
            this.addMessage(`❌ Error: ${result.error}`, 'bot');
            return;
        }
        
        let statusIcon = '';
        let statusClass = '';
        let statusText = '';
        
        switch(result.status) {
            case 'verified':
                statusIcon = '✅';
                statusClass = 'verified';
                statusText = 'VERIFIED';
                break;
            case 'partially-verified':
                statusIcon = '⚠️';
                statusClass = 'partially-verified';
                statusText = 'PARTIALLY VERIFIED';
                break;
            case 'unverified':
                statusIcon = '❌';
                statusClass = 'unverified';
                statusText = 'UNVERIFIED';
                break;
            default:
                statusIcon = '❓';
                statusClass = 'unknown';
                statusText = 'UNKNOWN';
        }
        
        const response = `
            <div class="verification-result ${statusClass}">
                <div class="result-header">
                    <strong>${statusIcon} ${statusText}</strong>
                    <span class="confidence-score">${result.credibility_score}/10</span>
                </div>
                
                <div class="result-details">
                    ${result.ai_summary ? `
                        <div class="ai-summary-section">
                            <h4>📝 AI Summary</h4>
                            <p class="ai-summary-text">${result.ai_summary}</p>
                        </div>
                    ` : ''}
                    
                    ${result.official_links && result.official_links.length > 0 ? `
                        <div class="official-links-section">
                            <h4>🔗 Official Sources - Read More</h4>
                            <div class="official-links">
                                ${result.official_links.map(link => `
                                    <a href="${link.url}" target="_blank" class="official-link">
                                        <div class="link-title">${link.title}</div>
                                        <div class="link-source">${link.source} • Credibility: ${link.credibility}/10</div>
                                    </a>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                    
                    ${result.suggestion ? `
                        <div class="suggestion-section">
                            <p class="suggestion">💡 ${result.suggestion}</p>
                        </div>
                    ` : ''}
                    
                    ${result.ml_analysis ? `
                        <div class="ml-analysis">
                            <small><strong>🤖 AI Analysis:</strong> ${result.ml_analysis.prediction || 'N/A'} 
                            (${Math.round((result.ml_analysis.confidence || 0) * 100)}% confidence)</small>
                        </div>
                    ` : ''}
                </div>
                
                <div class="result-footer">
                    <small>Processed in ${result.processing_time_ms || 'N/A'}ms • 
                    ${new Date().toLocaleTimeString()}</small>
                </div>
            </div>
        `;
        
        this.addMessage(response, 'bot');
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="typing-animation">
                    <span></span><span></span><span></span>
                </div>
                Analyzing with AI models...
            </div>
        `;
        
        const chatMessages = document.getElementById('chatMessages') || document.getElementById('fullChatMessages');
        if (chatMessages) {
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    speakResult(result) {
        if (!('speechSynthesis' in window)) return;
        
        const text = `Verification complete. Status: ${result.status}. 
                     Credibility score: ${result.credibility_score} out of 10. 
                     ${result.explanation}`;
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 0.8;
        
        speechSynthesis.speak(utterance);
    }
    
    startRotatingText() {
        const rotatingTexts = [
            "Verify to Trust AI",
            "See Truth, Not Just Headlines",
            "Verify Instantly. Trust Confidently",
            "AI That Fights Misinformation, For You"
        ];
        
        const rotatingElement = document.getElementById('rotating-text');
        if (!rotatingElement) return;
        
        let currentIndex = 0;
        
        setInterval(() => {
            rotatingElement.style.opacity = '0';
            
            setTimeout(() => {
                currentIndex = (currentIndex + 1) % rotatingTexts.length;
                rotatingElement.textContent = rotatingTexts[currentIndex];
                rotatingElement.style.opacity = '1';
            }, 500);
        }, 3000);
    }
    
    loadWelcomeMessage() {
        setTimeout(() => {
            const welcomeMessage = `
                Welcome! I can help you verify:
                <br>• News headlines and claims
                <br>• Website links and articles  
                <br>• Social media posts
                <br>• Breaking news stories
                <br><br>Just type, paste, or speak your query!
            `;
            this.addMessage(welcomeMessage, 'bot');
        }, 1000);
    }
}

// Authentication functions
function showAuth() {
    document.getElementById('authModal').style.display = 'block';
}

function closeAuth() {
    document.getElementById('authModal').style.display = 'none';
}

function showLogin() {
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('signupForm').classList.add('hidden');
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.querySelectorAll('.tab-btn')[1].classList.remove('active');
}

function showSignup() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('signupForm').classList.remove('hidden');
    document.querySelectorAll('.tab-btn')[0].classList.remove('active');
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
}

function sendExample(element) {
    const text = element.textContent;
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = text;
        window.trustifyApp.sendMessage();
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('authModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.trustifyApp = new TrustifyApp();
});

// Smooth scrolling for navigation links
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});