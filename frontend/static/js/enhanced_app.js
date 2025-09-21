// Enhanced Trustify AI Frontend Application
class EnhancedTrustifyApp {
    constructor() {
        this.apiBase = '';
        this.currentQuery = '';
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupAnimations();
    }
    
    setupEventListeners() {
        // Verify button
        const verifyBtn = document.getElementById('verifyBtn');
        const newsInput = document.getElementById('newsInput');
        
        verifyBtn.addEventListener('click', () => this.verifyNews());
        
        // Enter key support
        newsInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.verifyNews();
            }
        });
        
        // Input focus effects
        newsInput.addEventListener('focus', () => {
            document.querySelector('.search-box').style.transform = 'translateY(-2px)';
        });
        
        newsInput.addEventListener('blur', () => {
            document.querySelector('.search-box').style.transform = 'translateY(0)';
        });
    }
    
    setupAnimations() {
        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(255, 255, 255, 0.98)';
                navbar.style.boxShadow = '0 1px 3px 0 rgb(0 0 0 / 0.1)';
            } else {
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                navbar.style.boxShadow = 'none';
            }
        });
    }
    
    async verifyNews() {
        const newsInput = document.getElementById('newsInput');
        const query = newsInput.value.trim();
        
        if (!query) {
            this.showError('Please enter a news headline or URL');
            return;
        }
        
        this.currentQuery = query;
        this.showLoading();
        
        try {
            // Step 1: Show fetching APIs
            this.updateLoadingStep(1, 'Fetching from trusted news APIs...');
            await this.delay(1000);
            
            // Step 2: Show AI analysis
            this.updateLoadingStep(2, 'Running AI fake news detection...');
            await this.delay(1500);
            
            // Step 3: Show summarization
            this.updateLoadingStep(3, 'Generating AI summary...');
            await this.delay(1000);
            
            // Make API call
            const response = await fetch(`${this.apiBase}/api/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            this.hideLoading();
            this.showResults(result);
            
        } catch (error) {
            console.error('Verification error:', error);
            this.hideLoading();
            this.showNotFound();
        }
    }
    
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.add('active');
        
        // Reset steps
        document.querySelectorAll('.step').forEach((step, index) => {
            step.classList.remove('active', 'completed');
            if (index === 0) step.classList.add('active');
        });
    }
    
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.remove('active');
    }
    
    updateLoadingStep(stepNumber, text) {
        const loadingText = document.getElementById('loadingText');
        const steps = document.querySelectorAll('.step');
        
        loadingText.textContent = text;
        
        // Update step states
        steps.forEach((step, index) => {
            step.classList.remove('active');
            if (index < stepNumber - 1) {
                step.classList.add('completed');
            } else if (index === stepNumber - 1) {
                step.classList.add('active');
            }
        });
    }
    
    showResults(result) {
        const resultsSection = document.getElementById('results');
        const resultsContent = document.getElementById('resultsContent');
        const verificationBadge = document.getElementById('verificationBadge');
        
        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
        // Update verification badge
        this.updateVerificationBadge(result.status);
        
        // Generate results content
        if (result.status === 'verified' || result.status === 'partially-verified') {
            resultsContent.innerHTML = this.generateVerifiedContent(result);
        } else if (result.status === 'unverified') {
            resultsContent.innerHTML = this.generateFakeContent(result);
        } else {
            resultsContent.innerHTML = this.generateNotFoundContent();
        }
    }
    
    updateVerificationBadge(status) {
        const badge = document.getElementById('verificationBadge');
        const badgeIcon = badge.querySelector('.badge-icon');
        const badgeText = badge.querySelector('.badge-text');
        
        // Remove all status classes\n        badge.classList.remove('verified', 'fake', 'not-found', 'analyzing');\n        \n        switch(status) {\n            case 'verified':\n                badge.classList.add('verified');\n                badgeIcon.textContent = '✅';\n                badgeText.textContent = 'Verified';\n                break;\n            case 'partially-verified':\n                badge.classList.add('verified');\n                badgeIcon.textContent = '⚠️';\n                badgeText.textContent = 'Partially Verified';\n                break;\n            case 'unverified':\n                badge.classList.add('fake');\n                badgeIcon.textContent = '❌';\n                badgeText.textContent = 'Potentially Fake';\n                break;\n            default:\n                badge.classList.add('not-found');\n                badgeIcon.textContent = '❓';\n                badgeText.textContent = 'Not Found';\n        }\n    }\n    \n    generateVerifiedContent(result) {\n        const summary = result.ai_summary || 'This news appears to be from credible sources.';\n        const officialLinks = result.official_links || [];\n        \n        let linksHtml = '';\n        if (officialLinks.length > 0) {\n            const primaryLink = officialLinks[0];\n            linksHtml = `\n                <div class=\"read-more-section\">\n                    <a href=\"${primaryLink.url}\" target=\"_blank\" class=\"read-more-btn\">\n                        <span>📖 Read Full Article</span>\n                        <span>→</span>\n                    </a>\n                    <p style=\"margin-top: 1rem; color: var(--text-secondary); font-size: 0.9rem;\">\n                        Source: ${primaryLink.source} • Credibility: ${primaryLink.credibility}/10\n                    </p>\n                </div>\n            `;\n        }\n        \n        return `\n            <div class=\"summary-section\">\n                <h3>📝 AI Summary</h3>\n                <div class=\"summary-text\">\n                    ${summary}\n                </div>\n            </div>\n            ${linksHtml}\n            ${this.generateAdditionalSources(result.official_links)}\n        `;\n    }\n    \n    generateFakeContent(result) {\n        const explanation = result.explanation || 'This article may contain misleading information.';\n        \n        return `\n            <div class=\"warning-message\">\n                <h3 style=\"margin-bottom: 1rem;\">⚠️ Warning: Potentially Misleading</h3>\n                <p>${explanation}</p>\n                <div style=\"margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(239, 68, 68, 0.2);\">\n                    <strong>Recommendation:</strong> Please verify this information with trusted news sources before sharing.\n                </div>\n            </div>\n            ${this.generateFactCheckResources()}\n        `;\n    }\n    \n    generateNotFoundContent() {\n        return `\n            <div class=\"not-found-message\">\n                <h3 style=\"margin-bottom: 1rem;\">🔍 Not Found</h3>\n                <p>Sorry, we couldn't find this news in our trusted sources database.</p>\n                <div style=\"margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(245, 158, 11, 0.2);\">\n                    <strong>Please verify the source where you found this information.</strong>\n                    <br><br>\n                    Consider checking:\n                    <ul style=\"text-align: left; margin-top: 0.5rem; padding-left: 1.5rem;\">\n                        <li>Official news websites</li>\n                        <li>Government sources</li>\n                        <li>Established media outlets</li>\n                    </ul>\n                </div>\n            </div>\n            ${this.generateTrustedSources()}\n        `;\n    }\n    \n    generateAdditionalSources(officialLinks) {\n        if (!officialLinks || officialLinks.length <= 1) return '';\n        \n        const additionalLinks = officialLinks.slice(1, 4);\n        \n        return `\n            <div style=\"margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--border-color);\">\n                <h4 style=\"margin-bottom: 1rem; color: var(--text-primary);\">📰 Additional Sources</h4>\n                <div style=\"display: grid; gap: 0.75rem;\">\n                    ${additionalLinks.map(link => `\n                        <a href=\"${link.url}\" target=\"_blank\" style=\"\n                            display: flex;\n                            justify-content: space-between;\n                            align-items: center;\n                            padding: 0.75rem;\n                            background: var(--bg-secondary);\n                            border-radius: 8px;\n                            text-decoration: none;\n                            color: var(--text-primary);\n                            transition: all 0.3s ease;\n                            border-left: 3px solid var(--primary-color);\n                        \" onmouseover=\"this.style.background='rgba(37, 99, 235, 0.05)'\" onmouseout=\"this.style.background='var(--bg-secondary)'\">\n                            <div>\n                                <div style=\"font-weight: 500; margin-bottom: 0.25rem;\">${link.title}</div>\n                                <div style=\"font-size: 0.85rem; color: var(--text-secondary);\">${link.source}</div>\n                            </div>\n                            <span style=\"color: var(--primary-color);\">→</span>\n                        </a>\n                    `).join('')}\n                </div>\n            </div>\n        `;\n    }\n    \n    generateFactCheckResources() {\n        return `\n            <div style=\"margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(239, 68, 68, 0.2);\">\n                <h4 style=\"margin-bottom: 1rem; color: var(--text-primary);\">🔍 Fact-Check Resources</h4>\n                <div style=\"display: grid; gap: 0.5rem;\">\n                    <a href=\"https://www.snopes.com\" target=\"_blank\" class=\"resource-link\">Snopes.com</a>\n                    <a href=\"https://www.factcheck.org\" target=\"_blank\" class=\"resource-link\">FactCheck.org</a>\n                    <a href=\"https://www.politifact.com\" target=\"_blank\" class=\"resource-link\">PolitiFact</a>\n                </div>\n            </div>\n        `;\n    }\n    \n    generateTrustedSources() {\n        return `\n            <div style=\"margin-top: 2rem; padding-top: 2rem; border-top: 1px solid rgba(245, 158, 11, 0.2);\">\n                <h4 style=\"margin-bottom: 1rem; color: var(--text-primary);\">🏛️ Trusted News Sources</h4>\n                <div style=\"display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.5rem;\">\n                    <a href=\"https://reuters.com\" target=\"_blank\" class=\"resource-link\">Reuters</a>\n                    <a href=\"https://apnews.com\" target=\"_blank\" class=\"resource-link\">Associated Press</a>\n                    <a href=\"https://bbc.com/news\" target=\"_blank\" class=\"resource-link\">BBC News</a>\n                    <a href=\"https://bernama.com\" target=\"_blank\" class=\"resource-link\">Bernama</a>\n                </div>\n            </div>\n        `;\n    }\n    \n    showError(message) {\n        // Simple error display\n        alert(message);\n    }\n    \n    showNotFound() {\n        const resultsSection = document.getElementById('results');\n        const resultsContent = document.getElementById('resultsContent');\n        const verificationBadge = document.getElementById('verificationBadge');\n        \n        resultsSection.style.display = 'block';\n        resultsSection.scrollIntoView({ behavior: 'smooth' });\n        \n        this.updateVerificationBadge('not-found');\n        resultsContent.innerHTML = this.generateNotFoundContent();\n    }\n    \n    delay(ms) {\n        return new Promise(resolve => setTimeout(resolve, ms));\n    }\n}\n\n// Utility functions\nfunction setExample(text) {\n    const newsInput = document.getElementById('newsInput');\n    newsInput.value = text;\n    newsInput.focus();\n    \n    // Add a subtle animation\n    newsInput.style.transform = 'scale(1.02)';\n    setTimeout(() => {\n        newsInput.style.transform = 'scale(1)';\n    }, 200);\n}\n\n// Add resource link styles\nconst resourceLinkStyles = `\n    <style>\n        .resource-link {\n            display: inline-block;\n            padding: 0.5rem 1rem;\n            background: var(--bg-secondary);\n            color: var(--primary-color);\n            text-decoration: none;\n            border-radius: 6px;\n            font-size: 0.9rem;\n            font-weight: 500;\n            transition: all 0.3s ease;\n            border: 1px solid var(--border-color);\n        }\n        \n        .resource-link:hover {\n            background: var(--primary-color);\n            color: white;\n            transform: translateY(-1px);\n        }\n    </style>\n`;\n\ndocument.head.insertAdjacentHTML('beforeend', resourceLinkStyles);\n\n// Initialize app when DOM is loaded\ndocument.addEventListener('DOMContentLoaded', () => {\n    window.trustifyApp = new EnhancedTrustifyApp();\n});