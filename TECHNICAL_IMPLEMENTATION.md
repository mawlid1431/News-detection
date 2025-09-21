# 🔧 **Accurify.AI - Technical Implementation Guide**

### _Comprehensive Technology Stack & Implementation Details_

---

## 📋 **Technology Stack Overview**

Accurify.AI is built using a modern, full-stack technology stack carefully chosen for performance, scalability, and maintainability. Each technology serves a specific purpose in delivering a robust news verification system.

---

## 🐍 **Backend Technologies**

### **1. Python Flask Web Framework**

**Technology**: Flask 2.3.3  
**Purpose**: Core web framework and API server  
**Why Chosen**:

- ✅ **Lightweight & Flexible**: Perfect for microservices architecture
- ✅ **Rich Ecosystem**: Extensive library support for ML and APIs
- ✅ **Rapid Development**: Quick prototyping and deployment
- ✅ **Scalability**: Easy to scale horizontally
- ✅ **ML Integration**: Seamless integration with Python ML libraries

**Implementation Details**:

```python
# Core Flask application structure
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__,
           template_folder='frontend/templates',
           static_folder='frontend/static')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accurify.db'

# Extensions
CORS(app)  # Enable cross-origin requests
```

**Key Features Implemented**:

- RESTful API endpoints
- Template rendering with Jinja2
- Static file serving
- Error handling and logging
- CORS support for frontend integration

---

### **2. SQLAlchemy ORM**

**Technology**: SQLAlchemy 1.4+  
**Purpose**: Database abstraction and ORM  
**Why Chosen**:

- ✅ **Database Agnostic**: Works with SQLite, PostgreSQL, MySQL
- ✅ **Security**: Protection against SQL injection
- ✅ **Performance**: Query optimization and caching
- ✅ **Migrations**: Database schema versioning
- ✅ **Relationships**: Easy handling of complex data relationships

**Implementation Details**:

```python
# Database models
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Verification(db.Model):
    """Verification history model"""
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    credibility_score = db.Column(db.Float, default=0.0)
    confidence = db.Column(db.String(20), default='low')
    explanation = db.Column(db.Text)
    sources_count = db.Column(db.Integer, default=0)
    processing_time_ms = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

**Features**:

- Model definition and relationships
- Query builder and optimization
- Connection pooling
- Transaction management

---

### **3. Machine Learning Stack**

#### **scikit-learn 1.3.0**

**Purpose**: Core machine learning algorithms  
**Why Chosen**:

- ✅ **Comprehensive**: Wide range of algorithms
- ✅ **Mature**: Battle-tested and well-documented
- ✅ **Performance**: Optimized implementations
- ✅ **Integration**: Works well with other Python libraries

**Implementation**:

```python
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class MLModelManager:
    def __init__(self):
        self.models = {
            'svm': SVC(probability=True, kernel='rbf'),
            'logistic': LogisticRegression(max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100)
        }
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 3),
            stop_words='english'
        )
```

#### **NLTK 3.8.1**

**Purpose**: Natural Language Processing  
**Why Chosen**:

- ✅ **Text Processing**: Comprehensive NLP tools
- ✅ **Preprocessing**: Tokenization, stemming, lemmatization
- ✅ **Resources**: Rich linguistic data and corpora
- ✅ **Research Quality**: Academic-grade NLP capabilities

**Implementation**:

```python
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import re

class TextPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def preprocess_text(self, text):
        # Convert to lowercase
        text = text.lower()

        # Remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text)

        # Tokenize
        tokens = word_tokenize(text)

        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token)
                 for token in tokens
                 if token not in self.stop_words]

        return ' '.join(tokens)
```

---

### **4. API Integration & HTTP Handling**

#### **Requests 2.31.0**

**Purpose**: HTTP client for external APIs  
**Why Chosen**:

- ✅ **Simple API**: Easy to use and understand
- ✅ **Robust**: Handles redirects, SSL, timeouts
- ✅ **Features**: Sessions, authentication, hooks
- ✅ **Reliable**: Industry standard for Python HTTP

**Implementation**:

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class NewsAPIClient:
    def __init__(self):
        self.session = requests.Session()

        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def search_news(self, query, source='gnews'):
        """Search news from external APIs"""
        try:
            response = self.session.get(
                url=f"https://gnews.io/api/v4/search",
                params={
                    'q': query,
                    'token': self.api_key,
                    'lang': 'en'
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
```

#### **BeautifulSoup4 4.12.2**

**Purpose**: HTML parsing and web scraping  
**Why Chosen**:

- ✅ **Robust Parsing**: Handles malformed HTML
- ✅ **Easy API**: Simple and intuitive
- ✅ **Performance**: Fast parsing with different parsers
- ✅ **Flexibility**: CSS selectors and XPath support

**Implementation**:

```python
from bs4 import BeautifulSoup
import requests

class WebScraper:
    def extract_article_content(self, url):
        """Extract main content from news article"""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Try multiple content selectors
            selectors = [
                'article',
                '.article-content',
                '.content',
                'main',
                '[role="main"]'
            ]

            for selector in selectors:
                content = soup.select_one(selector)
                if content:
                    return content.get_text(strip=True)

            # Fallback to paragraphs
            paragraphs = soup.find_all('p')
            return ' '.join([p.get_text(strip=True) for p in paragraphs])

        except Exception as e:
            logger.error(f"Scraping failed for {url}: {e}")
            return None
```

---

### **5. Configuration & Environment Management**

#### **python-dotenv 1.0.0**

**Purpose**: Environment variable management  
**Why Chosen**:

- ✅ **Security**: Keep secrets out of code
- ✅ **Flexibility**: Environment-specific configurations
- ✅ **12-Factor App**: Follows best practices
- ✅ **Simple**: Easy .env file format

**Implementation**:

```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///trustify.db')

    # API Keys
    GNEWS_API_KEY = os.getenv('GNEWS_API_KEY')
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
    CURRENTS_API_KEY = os.getenv('CURRENTS_API_KEY')

    # ML Configuration
    MODEL_CONFIDENCE_THRESHOLD = float(os.getenv('MODEL_CONFIDENCE_THRESHOLD', '0.8'))
    MAX_NEWS_SOURCES = int(os.getenv('MAX_NEWS_SOURCES', '10'))
```

---

## 🎨 **Frontend Technologies**

### **1. HTML5**

**Purpose**: Semantic markup and structure  
**Why Chosen**:

- ✅ **Semantic Elements**: Better accessibility and SEO
- ✅ **Modern APIs**: Web Speech, Fetch, WebSocket support
- ✅ **Standards Compliant**: Cross-browser compatibility
- ✅ **Progressive Enhancement**: Works without JavaScript

**Implementation Features**:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="AI-powered news verification system" />
    <title>Accurify.AI - Verify News with AI</title>
  </head>
  <body>
    <main role="main" class="chat-container">
      <section class="chat-header" aria-label="Application header">
        <h1>Accurify.AI</h1>
      </section>

      <section class="chat-messages" aria-live="polite" role="log">
        <!-- Dynamic content -->
      </section>

      <section class="chat-input" role="form">
        <input
          type="text"
          id="chatInput"
          placeholder="Enter news to verify..."
          aria-label="News verification input" />
        <button id="sendBtn" aria-label="Send message">Send</button>
        <button id="voiceBtn" aria-label="Voice input">🎤</button>
      </section>
    </main>
  </body>
</html>
```

### **2. CSS3**

**Purpose**: Modern styling and responsive design  
**Why Chosen**:

- ✅ **Modern Features**: Grid, Flexbox, animations
- ✅ **Responsive**: Mobile-first design approach
- ✅ **Performance**: Hardware acceleration
- ✅ **Maintainable**: CSS custom properties and organization

**Implementation Highlights**:

```css
/* CSS Custom Properties for theming */
:root {
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --text-color: #1f2937;
  --bg-color: #ffffff;
  --border-radius: 12px;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Modern CSS Grid Layout */
.chat-container {
  display: grid;
  grid-template-rows: auto 1fr auto;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  background: var(--bg-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
}

/* Responsive Design */
@media (max-width: 768px) {
  .chat-container {
    height: 100vh;
    border-radius: 0;
    max-width: 100%;
  }
}

/* Smooth Animations */
.message {
  opacity: 0;
  transform: translateY(20px);
  animation: slideIn 0.3s ease-out forwards;
}

@keyframes slideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### **3. JavaScript ES6+**

**Purpose**: Interactive functionality and API communication  
**Why Chosen**:

- ✅ **Modern Syntax**: Arrow functions, async/await, modules
- ✅ **Browser APIs**: Fetch, Web Speech, WebRTC
- ✅ **Performance**: Optimized execution
- ✅ **Maintainable**: Class-based architecture

**Implementation Architecture**:

```javascript
// Main Application Class
class AccurifyApp {
  constructor() {
    this.apiBaseUrl = "/api";
    this.isListening = false;
    this.recognition = null;
    this.synthesis = window.speechSynthesis;

    this.init();
  }

  init() {
    this.setupEventListeners();
    this.initializeVoiceRecognition();
    this.loadExamples();
  }

  // Modern async/await API calls
  async verifyNews(query) {
    try {
      this.showTyping();

      const response = await fetch(`${this.apiBaseUrl}/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      this.displayResult(result);
    } catch (error) {
      console.error("Verification failed:", error);
      this.displayError("Verification service unavailable");
    } finally {
      this.hideTyping();
    }
  }

  // Web Speech API Integration
  initializeVoiceRecognition() {
    if ("webkitSpeechRecognition" in window) {
      this.recognition = new webkitSpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = false;
      this.recognition.lang = "en-US";

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("chatInput").value = transcript;
        this.sendMessage();
      };

      this.recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        this.isListening = false;
        this.updateVoiceButton();
      };
    }
  }

  // Speech Synthesis
  speak(text) {
    if (this.synthesis) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 0.8;
      this.synthesis.speak(utterance);
    }
  }
}

// Initialize application
document.addEventListener("DOMContentLoaded", () => {
  new AccurifyApp();
});
```

---

## 🔍 **Core Business Logic Implementation**

### **1. Verification Engine**

```python
class VerificationEngine:
    """Core news verification logic"""

    def __init__(self):
        self.ml_manager = MLModelManager()
        self.news_manager = NewsSourceManager()
        self.confidence_threshold = 0.8

    def verify(self, query):
        """Main verification workflow"""
        start_time = time.time()

        # Step 1: ML Classification
        ml_result = self.ml_manager.classify_text(query)

        # Step 2: News Source Search
        articles = self.news_manager.search_news(query)

        # Step 3: Similarity Analysis
        similarity_scores = self._calculate_similarity(query, articles)

        # Step 4: Credibility Assessment
        credibility_score = self._calculate_credibility(
            ml_result, similarity_scores, articles
        )

        # Step 5: Generate Result
        result = self._generate_result(
            query, ml_result, articles, credibility_score,
            time.time() - start_time
        )

        return result

    def _calculate_credibility(self, ml_result, similarity_scores, articles):
        """Calculate final credibility score"""
        # ML model weight (40%)
        ml_score = ml_result.get('confidence', 0.0) * 0.4

        # Source reliability weight (35%)
        source_score = np.mean([
            article.get('source_credibility', 5.0)
            for article in articles
        ]) / 10.0 * 0.35

        # Similarity weight (25%)
        similarity_score = np.mean(similarity_scores) * 0.25

        return min(10.0, (ml_score + source_score + similarity_score) * 10)
```

### **2. News Sources Manager**

```python
class NewsSourceManager:
    """Manage multiple news source APIs"""

    def __init__(self):
        self.sources = {
            'gnews': GNewsAPI(),
            'newsapi': NewsAPIOrg(),
            'currents': CurrentsAPI(),
            'guardian': GuardianAPI()
        }
        self.malaysian_sources = {
            'bernama': BernamaAPI(),
            'thestar': TheStarAPI(),
            'nst': NewStraitsTimes()
        }

    def search_news(self, query, max_sources=10):
        """Search across multiple news sources"""
        all_articles = []

        # Search international sources
        for source_name, source_api in self.sources.items():
            try:
                articles = source_api.search(query, limit=3)
                if articles:
                    all_articles.extend(articles)
            except Exception as e:
                logger.warning(f"Source {source_name} failed: {e}")

        # Search Malaysian sources
        for source_name, source_api in self.malaysian_sources.items():
            try:
                articles = source_api.search(query, limit=2)
                if articles:
                    all_articles.extend(articles)
            except Exception as e:
                logger.warning(f"Malaysian source {source_name} failed: {e}")

        # Deduplicate and rank
        unique_articles = self._deduplicate_articles(all_articles)
        ranked_articles = self._rank_articles(unique_articles, query)

        return ranked_articles[:max_sources]
```

---

## 🚀 **Deployment Technologies**

### **1. Docker Containerization**

**Purpose**: Application packaging and deployment  
**Why Chosen**:

- ✅ **Consistency**: Same environment everywhere
- ✅ **Isolation**: Dependency management
- ✅ **Scalability**: Easy scaling and orchestration
- ✅ **CI/CD**: Streamlined deployment pipeline

**Implementation**:

```dockerfile
# Multi-stage Docker build
FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run application
CMD ["python", "run.py"]
```

### **2. AWS Cloud Infrastructure**

**Technologies**: EC2, RDS, S3, CloudFront, Lambda  
**Why Chosen**:

- ✅ **Scalability**: Auto-scaling capabilities
- ✅ **Reliability**: 99.99% uptime SLA
- ✅ **Security**: Enterprise-grade security
- ✅ **Cost-Effective**: Pay-as-you-use pricing
- ✅ **Managed Services**: Reduced operational overhead

**Infrastructure as Code**:

```yaml
# CloudFormation template excerpt
Resources:
  TrustifyAppServer:
    Type: AWS::EC2::Instance
    Properties:
      InstanceType: t3.medium
      ImageId: ami-0abcdef1234567890
      SecurityGroups:
        - !Ref TrustifySecurityGroup
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          yum update -y
          yum install -y docker
          service docker start
          docker run -d -p 80:5000 trustify-ai:latest

  TrustifyDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceClass: db.t3.micro
      Engine: postgres
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      MultiAZ: true
```

---

## 🔧 **Development Tools & Workflow**

### **1. Version Control**

- **Git**: Source code management
- **GitHub**: Remote repository and collaboration
- **Branching Strategy**: GitFlow for feature development

### **2. Code Quality**

```python
# Requirements for code quality
pylint>=2.15.0          # Code linting
black>=22.0.0           # Code formatting
pytest>=7.0.0           # Unit testing
coverage>=6.0.0         # Test coverage
mypy>=0.991             # Type checking
```

### **3. CI/CD Pipeline**

```yaml
# GitHub Actions workflow
name: CI/CD Pipeline
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=./ --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 📊 **Performance Optimization**

### **1. Caching Strategy**

```python
from functools import lru_cache
import redis

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

    @lru_cache(maxsize=1000)
    def get_model_prediction(self, text_hash):
        """Cache ML predictions"""
        return self._calculate_prediction(text_hash)

    def cache_news_articles(self, query, articles, ttl=3600):
        """Cache news search results"""
        cache_key = f"news:{hashlib.md5(query.encode()).hexdigest()}"
        self.redis_client.setex(
            cache_key,
            ttl,
            json.dumps(articles)
        )
```

### **2. Database Optimization**

```python
# Database indexing
class Verification(db.Model):
    __tablename__ = 'verifications'

    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.Text, nullable=False, index=True)  # Index for search
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)  # Index for date queries

    # Composite index for common queries
    __table_args__ = (
        db.Index('idx_query_timestamp', 'query', 'timestamp'),
    )
```

---

## 🔒 **Security Implementation**

### **1. Input Validation**

```python
from marshmallow import Schema, fields, validate

class VerificationRequestSchema(Schema):
    query = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=1000),
        allow_none=False
    )

def validate_request(request_data):
    schema = VerificationRequestSchema()
    try:
        result = schema.load(request_data)
        return result, None
    except ValidationError as err:
        return None, err.messages
```

### **2. Rate Limiting**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/verify', methods=['POST'])
@limiter.limit("10 per minute")
def verify_news():
    # Verification logic
    pass
```

---

## 📈 **Monitoring & Logging**

### **1. Structured Logging**

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id

        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

for handler in logging.getLogger().handlers:
    handler.setFormatter(JSONFormatter())
```

### **2. Performance Monitoring**

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            logger.info(
                f"Function {func.__name__} executed successfully",
                extra={
                    'execution_time': execution_time,
                    'function': func.__name__,
                    'status': 'success'
                }
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed",
                extra={
                    'execution_time': execution_time,
                    'function': func.__name__,
                    'status': 'error',
                    'error': str(e)
                }
            )
            raise
    return wrapper
```

---

## 🎯 **Technology Decision Matrix**

| Technology       | Alternatives Considered | Why Chosen                   | Trade-offs               |
| ---------------- | ----------------------- | ---------------------------- | ------------------------ |
| **Flask**        | Django, FastAPI         | Lightweight, ML integration  | Less built-in features   |
| **SQLAlchemy**   | Django ORM, Raw SQL     | Database agnostic, secure    | Learning curve           |
| **scikit-learn** | TensorFlow, PyTorch     | Mature, comprehensive        | Limited deep learning    |
| **PostgreSQL**   | MySQL, MongoDB          | ACID compliance, performance | More complex than SQLite |
| **JavaScript**   | TypeScript, React       | Native browser support       | Less type safety         |
| **Docker**       | VM, Native deployment   | Consistency, portability     | Additional complexity    |
| **AWS**          | Google Cloud, Azure     | Market leader, services      | Vendor lock-in           |

---

## 🔄 **Development Workflow**

### **1. Local Development Setup**

```bash
# 1. Clone repository
git clone https://github.com/your-repo/trustify-ai.git
cd trustify-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 6. Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# 7. Train models (if needed)
python train_model.py

# 8. Run application
python run.py
```

### **2. Testing Strategy**

```python
# Unit tests
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_health_endpoint(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    assert 'status' in response.json

def test_verify_endpoint(client):
    response = client.post('/api/verify',
                          json={'query': 'Test news claim'})
    assert response.status_code == 200
    assert 'credibility_score' in response.json
```

---

This technical implementation guide demonstrates the thoughtful selection and integration of modern technologies to create a robust, scalable, and maintainable news verification system. Each technology choice is justified by specific requirements and demonstrates best practices in full-stack development.

**Key Technical Strengths:**

- ✅ **Modern Stack**: Latest stable versions of all technologies
- ✅ **Best Practices**: Following industry standards and patterns
- ✅ **Scalability**: Architecture designed for growth
- ✅ **Security**: Multiple layers of protection
- ✅ **Maintainability**: Clean code and documentation
- ✅ **Performance**: Optimized for speed and efficiency
