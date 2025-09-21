# 🌐 **Accurify.AI - REST API Documentation**

### _Complete API Reference with Testing Examples_

---

## 📋 **API Overview**

Accurify.AI provides a comprehensive RESTful API for news verification services. The API is designed to be simple, reliable, and fast, enabling real-time fact-checking with detailed response information.

**Base URL**: `http://localhost:5000` (Development) | `https://your-domain.com` (Production)

---

## 🔧 **API Endpoints Summary**

| Endpoint             | Method | Purpose                | Authentication |
| -------------------- | ------ | ---------------------- | -------------- |
| `/`                  | GET    | Main web interface     | None           |
| `/chatbot`           | GET    | Chatbot interface      | None           |
| `/api/health`        | GET    | System health check    | None           |
| `/api/verify`        | POST   | News verification      | None           |
| `/api/sources`       | GET    | Available news sources | None           |
| `/api/models/status` | GET    | ML model status        | None           |

---

## 🏠 **Core Endpoints**

### **1. Health Check Endpoint**

**Endpoint**: `GET /api/health`  
**Purpose**: Check system status and service availability  
**Authentication**: None required

#### **Request Example**

```bash
curl -X GET http://localhost:5000/api/health
```

#### **Response Format**

```json
{
  "status": "healthy",
  "timestamp": "2025-09-20T10:30:00.123Z",
  "version": "1.0.0",
  "services": {
    "ml_models": {
      "status": "loaded",
      "available_models": ["svm", "logistic", "random_forest", "transformer"],
      "primary_model": "svm"
    },
    "news_sources": {
      "status": "operational",
      "active_sources": 85,
      "total_sources": 100,
      "last_health_check": "2025-09-20T10:29:45.123Z"
    },
    "database": {
      "status": "connected",
      "type": "SQLite",
      "connection_pool": "healthy"
    }
  },
  "performance": {
    "average_response_time_ms": 145,
    "total_requests_today": 1247,
    "success_rate": 99.2
  }
}
```

#### **Response Codes**

- `200 OK`: System is healthy
- `503 Service Unavailable`: System experiencing issues

---

### **2. News Verification Endpoint**

**Endpoint**: `POST /api/verify`  
**Purpose**: Verify news claims using AI and multiple sources  
**Authentication**: None required  
**Content-Type**: `application/json`

#### **Request Format**

```json
{
  "query": "string (required, 3-1000 characters)",
  "options": {
    "include_sources": true,
    "max_sources": 10,
    "confidence_threshold": 0.8,
    "language": "en"
  }
}
```

#### **Request Examples**

**Example 1: Basic Verification**

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "COVID-19 vaccine causes autism"
  }'
```

**Example 2: With Options**

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Scientists discover new treatment for diabetes",
    "options": {
      "include_sources": true,
      "max_sources": 15,
      "confidence_threshold": 0.7
    }
  }'
```

**Example 3: JavaScript/Frontend**

```javascript
const response = await fetch("/api/verify", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    query: "Climate change is a hoax created by scientists",
    options: {
      include_sources: true,
      max_sources: 8,
    },
  }),
});

const result = await response.json();
console.log(result);
```

#### **Response Format**

```json
{
  "query": "COVID-19 vaccine causes autism",
  "status": "unverified",
  "credibility_score": 1.2,
  "confidence": "low",
  "prediction": "unreliable",
  "explanation": "No credible scientific evidence supports this claim. Multiple peer-reviewed studies have consistently found no link between vaccines and autism. This claim has been thoroughly debunked by the medical community.",
  "sources": [
    {
      "title": "CDC: Vaccines Do Not Cause Autism",
      "url": "https://www.cdc.gov/vaccinesafety/concerns/autism.html",
      "source": "Centers for Disease Control",
      "credibility": 9.5,
      "relevance": 0.95,
      "date": "2024-08-15"
    },
    {
      "title": "WHO Statement on Vaccine Safety",
      "url": "https://www.who.int/news-room/feature-stories/detail/vaccine-safety",
      "source": "World Health Organization",
      "credibility": 9.8,
      "relevance": 0.91,
      "date": "2024-07-22"
    }
  ],
  "ml_analysis": {
    "models_used": ["svm", "transformer", "logistic"],
    "svm_prediction": {
      "classification": "unreliable",
      "confidence": 0.87,
      "fake_probability": 0.87,
      "real_probability": 0.13
    },
    "transformer_prediction": {
      "classification": "unreliable",
      "confidence": 0.92,
      "model": "roberta-fake-news-classification"
    },
    "ensemble_result": {
      "final_prediction": "unreliable",
      "confidence": 0.89,
      "agreement_score": 0.94
    }
  },
  "verification_details": {
    "sources_checked": 8,
    "sources_supporting": 0,
    "sources_contradicting": 8,
    "consensus_level": "strong_contradiction",
    "fact_check_links": [
      "https://www.snopes.com/fact-check/vaccines-autism/",
      "https://www.factcheck.org/2019/03/the-facts-on-autism-and-vaccines/"
    ]
  },
  "ai_summary": "This claim has been extensively studied and consistently debunked by the scientific community. Multiple large-scale studies involving millions of children have found no causal relationship between vaccines and autism spectrum disorders.",
  "official_links": [
    {
      "title": "CDC Vaccine Safety Information",
      "url": "https://www.cdc.gov/vaccinesafety/",
      "type": "official_health_authority"
    },
    {
      "title": "WHO Immunization Guidelines",
      "url": "https://www.who.int/immunization/",
      "type": "international_health_organization"
    }
  ],
  "read_more_available": true,
  "suggestion": "For accurate health information, consult peer-reviewed medical journals and official health authorities like CDC, WHO, or your healthcare provider.",
  "processing_time_ms": 1247,
  "timestamp": "2025-09-20T10:35:12.456Z",
  "request_id": "req_abc123def456"
}
```

#### **Response Field Descriptions**

| Field                  | Type   | Description                                                                 |
| ---------------------- | ------ | --------------------------------------------------------------------------- |
| `query`                | string | Original query text                                                         |
| `status`               | string | Overall verification status: "verified", "partially_verified", "unverified" |
| `credibility_score`    | number | Credibility score from 0-10 (higher = more credible)                        |
| `confidence`           | string | Confidence level: "high", "medium", "low"                                   |
| `prediction`           | string | ML prediction: "reliable", "unreliable", "uncertain"                        |
| `explanation`          | string | Human-readable explanation of the result                                    |
| `sources`              | array  | Array of news sources found                                                 |
| `ml_analysis`          | object | Detailed ML model analysis                                                  |
| `verification_details` | object | Source verification statistics                                              |
| `ai_summary`           | string | AI-generated summary of findings                                            |
| `official_links`       | array  | Links to official/authoritative sources                                     |
| `processing_time_ms`   | number | Total processing time in milliseconds                                       |

#### **Response Codes**

- `200 OK`: Verification completed successfully
- `400 Bad Request`: Invalid request format or missing query
- `422 Unprocessable Entity`: Query validation failed
- `500 Internal Server Error`: Verification service error

#### **Error Response Format**

```json
{
  "error": "Query is required",
  "message": "The 'query' field must be provided and contain 3-1000 characters",
  "code": "INVALID_REQUEST",
  "timestamp": "2025-09-20T10:35:12.456Z",
  "request_id": "req_error_123"
}
```

---

### **3. News Sources Endpoint**

**Endpoint**: `GET /api/sources`  
**Purpose**: Get information about available news sources  
**Authentication**: None required

#### **Request Example**

```bash
curl -X GET http://localhost:5000/api/sources
```

#### **Response Format**

```json
{
  "total_sources": 100,
  "active_sources": 87,
  "sources_by_category": {
    "international": 45,
    "malaysian": 15,
    "scientific": 20,
    "fact_checkers": 12,
    "government": 8
  },
  "sources": [
    {
      "name": "Reuters",
      "country": "International",
      "category": "news_agency",
      "credibility_rating": 9.5,
      "language": "en",
      "api_status": "active",
      "last_checked": "2025-09-20T10:30:00Z",
      "response_time_ms": 245,
      "success_rate": 99.2
    },
    {
      "name": "BBC News",
      "country": "United Kingdom",
      "category": "broadcaster",
      "credibility_rating": 9.2,
      "language": "en",
      "api_status": "active",
      "last_checked": "2025-09-20T10:29:45Z",
      "response_time_ms": 312,
      "success_rate": 98.7
    },
    {
      "name": "Bernama",
      "country": "Malaysia",
      "category": "national_agency",
      "credibility_rating": 9.0,
      "language": "en",
      "api_status": "active",
      "last_checked": "2025-09-20T10:31:15Z",
      "response_time_ms": 189,
      "success_rate": 97.8
    }
  ],
  "health_summary": {
    "operational_sources": 87,
    "degraded_sources": 8,
    "failed_sources": 5,
    "average_response_time": 275,
    "overall_success_rate": 96.8
  },
  "last_updated": "2025-09-20T10:30:00Z"
}
```

---

### **4. ML Models Status Endpoint**

**Endpoint**: `GET /api/models/status`  
**Purpose**: Get detailed information about ML models  
**Authentication**: None required

#### **Request Example**

```bash
curl -X GET http://localhost:5000/api/models/status
```

#### **Response Format**

```json
{
  "models_loaded": true,
  "total_models": 5,
  "active_models": 4,
  "models": {
    "svm": {
      "name": "Support Vector Machine",
      "type": "traditional_ml",
      "status": "loaded",
      "accuracy": 92.3,
      "precision": 91.8,
      "recall": 92.7,
      "f1_score": 92.2,
      "training_date": "2025-09-15",
      "version": "1.2.0",
      "features": "TF-IDF (10,000 features)",
      "inference_time_ms": 45,
      "memory_usage_mb": 24.5
    },
    "logistic_regression": {
      "name": "Logistic Regression",
      "type": "traditional_ml",
      "status": "loaded",
      "accuracy": 89.1,
      "precision": 88.9,
      "recall": 89.3,
      "f1_score": 89.1,
      "training_date": "2025-09-15",
      "version": "1.2.0",
      "features": "TF-IDF (5,000 features)",
      "inference_time_ms": 12,
      "memory_usage_mb": 8.2
    },
    "random_forest": {
      "name": "Random Forest",
      "type": "ensemble_ml",
      "status": "loaded",
      "accuracy": 87.4,
      "precision": 87.1,
      "recall": 87.8,
      "f1_score": 87.4,
      "training_date": "2025-09-15",
      "version": "1.2.0",
      "features": "TF-IDF (8,000 features)",
      "trees": 100,
      "inference_time_ms": 67,
      "memory_usage_mb": 45.1
    },
    "transformer": {
      "name": "RoBERTa Fake News Classifier",
      "type": "transformer",
      "status": "loaded",
      "accuracy": 94.2,
      "precision": 94.0,
      "recall": 94.5,
      "f1_score": 94.2,
      "model_name": "hamzab/roberta-fake-news-classification",
      "version": "1.0.0",
      "parameters": "125M",
      "inference_time_ms": 180,
      "memory_usage_mb": 512.3
    },
    "rule_based": {
      "name": "Rule-Based Classifier",
      "type": "rule_based",
      "status": "loaded",
      "accuracy": 78.5,
      "precision": 76.2,
      "recall": 81.3,
      "f1_score": 78.7,
      "version": "1.0.0",
      "rules_count": 45,
      "inference_time_ms": 5,
      "memory_usage_mb": 0.1
    }
  },
  "ensemble_performance": {
    "accuracy": 93.1,
    "precision": 92.7,
    "recall": 93.4,
    "f1_score": 93.0,
    "confidence_threshold": 0.8,
    "average_inference_time_ms": 150
  },
  "system_info": {
    "total_memory_usage_mb": 590.2,
    "cpu_usage_percent": 15.3,
    "gpu_available": false,
    "python_version": "3.9.12",
    "sklearn_version": "1.3.0",
    "transformers_version": "4.33.2"
  },
  "last_updated": "2025-09-20T10:30:00Z"
}
```

---

## 🧪 **Testing Examples**

### **Test Case 1: Known Fake News**

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SHOCKING: Scientists discover that drinking bleach cures COVID-19!"
  }'

# Expected Response: status="unverified", credibility_score < 3.0
```

### **Test Case 2: Verified Information**

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "WHO recommends vaccination as the most effective way to prevent COVID-19"
  }'

# Expected Response: status="verified", credibility_score > 8.0
```

### **Test Case 3: Ambiguous Content**

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "New study suggests possible link between diet and cancer risk"
  }'

# Expected Response: status="partially_verified", credibility_score 5.0-7.0
```

### **Test Case 4: Current Event**

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Malaysia GDP growth rate forecast for 2025"
  }'

# Expected Response: Multiple sources, recent articles
```

### **Test Case 5: Scientific Claim**

```bash
curl -X POST http://localhost:5000/api/verify \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Climate change is caused by human activities according to 97% of scientists"
  }'

# Expected Response: High credibility, scientific sources
```

---

## 🔍 **Advanced Usage Examples**

### **1. Batch Processing (Multiple Queries)**

```python
import requests
import asyncio
import aiohttp

async def verify_multiple_claims(claims):
    """Verify multiple claims concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for claim in claims:
            task = session.post(
                'http://localhost:5000/api/verify',
                json={'query': claim},
                headers={'Content-Type': 'application/json'}
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        results = []
        for response in responses:
            result = await response.json()
            results.append(result)

        return results

# Usage
claims = [
    "Vaccines cause autism",
    "Climate change is a hoax",
    "5G towers spread coronavirus",
    "Face masks don't prevent disease transmission"
]

results = asyncio.run(verify_multiple_claims(claims))
for result in results:
    print(f"Query: {result['query']}")
    print(f"Status: {result['status']}")
    print(f"Credibility: {result['credibility_score']}/10")
    print("---")
```

### **2. Real-time Monitoring**

```python
import requests
import time

def monitor_api_health():
    """Monitor API health and performance"""
    while True:
        try:
            start_time = time.time()
            response = requests.get('http://localhost:5000/api/health')
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Healthy - Response time: {response_time:.0f}ms")
                print(f"   Success rate: {data['performance']['success_rate']}%")
                print(f"   Active sources: {data['services']['news_sources']['active_sources']}")
            else:
                print(f"❌ API Unhealthy - Status: {response.status_code}")

        except Exception as e:
            print(f"🔥 API Error: {e}")

        time.sleep(30)  # Check every 30 seconds

# Run monitoring
monitor_api_health()
```

### **3. Custom News Verification App**

```javascript
class NewsVerifier {
  constructor(apiBaseUrl = "http://localhost:5000") {
    this.apiBaseUrl = apiBaseUrl;
  }

  async verifyNews(query, options = {}) {
    try {
      const response = await fetch(`${this.apiBaseUrl}/api/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: query,
          options: options,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return this.formatResult(result);
    } catch (error) {
      console.error("Verification failed:", error);
      return { error: error.message };
    }
  }

  formatResult(result) {
    return {
      isReliable: result.credibility_score >= 7.0,
      confidence: result.confidence,
      summary: result.ai_summary,
      sources: result.sources.length,
      processingTime: result.processing_time_ms,
    };
  }

  async getSourceHealth() {
    const response = await fetch(`${this.apiBaseUrl}/api/sources`);
    const data = await response.json();
    return {
      totalSources: data.total_sources,
      activeSources: data.active_sources,
      healthPercentage: (data.active_sources / data.total_sources) * 100,
    };
  }
}

// Usage example
const verifier = new NewsVerifier();

// Verify a claim
verifier
  .verifyNews("COVID-19 vaccines are safe and effective")
  .then((result) => {
    console.log("Verification result:", result);
  });

// Check source health
verifier.getSourceHealth().then((health) => {
  console.log(`Source health: ${health.healthPercentage.toFixed(1)}%`);
});
```

---

## 🚀 **Performance & Rate Limits**

### **Performance Metrics**

- **Average Response Time**: 150ms for verification
- **Throughput**: 100+ requests per minute
- **Availability**: 99.9% uptime target
- **Concurrent Users**: Up to 50 simultaneous requests

### **Rate Limiting**

Currently, no rate limiting is implemented, but for production deployment:

- **Per IP**: 60 requests per minute
- **Per API Key**: 1000 requests per hour (if authentication added)
- **Burst Limit**: 10 requests per second

### **Optimization Tips**

1. **Cache Results**: Results are cached for 1 hour for identical queries
2. **Batch Requests**: Use concurrent requests for multiple verifications
3. **Keep-Alive**: Use persistent connections for multiple requests
4. **Compression**: API supports gzip compression

---

## 🔒 **Security & Best Practices**

### **Input Validation**

- Query length: 3-1000 characters
- Special character filtering
- SQL injection prevention
- XSS protection

### **Error Handling**

```json
{
  "error": "Validation failed",
  "message": "Query must be between 3 and 1000 characters",
  "code": "VALIDATION_ERROR",
  "field": "query",
  "timestamp": "2025-09-20T10:35:12.456Z"
}
```

### **Best Practices for Integration**

1. **Always check response status codes**
2. **Implement retry logic with exponential backoff**
3. **Handle network timeouts gracefully**
4. **Cache results to reduce API calls**
5. **Monitor API health regularly**

---

## 📚 **SDK Examples**

### **Python SDK**

```python
import requests
from typing import Dict, Any, Optional

class AccurifyClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def verify(self, query: str, **options) -> Dict[str, Any]:
        """Verify a news claim"""
        response = self.session.post(
            f"{self.base_url}/api/verify",
            json={"query": query, "options": options},
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def health(self) -> Dict[str, Any]:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/api/health")
        response.raise_for_status()
        return response.json()

    def sources(self) -> Dict[str, Any]:
        """Get news sources information"""
        response = self.session.get(f"{self.base_url}/api/sources")
        response.raise_for_status()
        return response.json()

# Usage
client = AccurifyClient()
result = client.verify("Climate change is real")
print(f"Credibility: {result['credibility_score']}/10")
```

### **Node.js SDK**

```javascript
const axios = require("axios");

class AccurifyClient {
  constructor(baseUrl = "http://localhost:5000") {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });
  }

  async verify(query, options = {}) {
    try {
      const response = await this.client.post("/api/verify", {
        query: query,
        options: options,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Verification failed: ${error.message}`);
    }
  }

  async health() {
    const response = await this.client.get("/api/health");
    return response.data;
  }

  async sources() {
    const response = await this.client.get("/api/sources");
    return response.data;
  }
}

// Usage
const client = new AccurifyClient();

client
  .verify("Vaccines are safe")
  .then((result) => {
    console.log(`Credibility: ${result.credibility_score}/10`);
  })
  .catch((error) => {
    console.error("Error:", error.message);
  });
```

---

This comprehensive API documentation provides everything needed to integrate with and test the Accurify.AI verification system. The API is designed to be developer-friendly while providing detailed information for accurate news verification.

**API Strengths:**

- ✅ **RESTful Design**: Standard HTTP methods and status codes
- ✅ **Comprehensive Responses**: Detailed verification information
- ✅ **Real-time Processing**: Fast response times
- ✅ **Multiple Data Sources**: 100+ news sources integration
- ✅ **Error Handling**: Clear error messages and codes
- ✅ **Documentation**: Complete examples and SDKs
