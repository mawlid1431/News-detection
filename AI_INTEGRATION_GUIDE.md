# 🤖 AI Integration Guide - Amazon Bedrock, Claude, and More

This guide shows how to integrate Trustify AI with advanced AI services like Amazon Bedrock, Claude, OpenAI, and others for enhanced fact-checking capabilities.

## 🚀 Quick Integration

### **Amazon Bedrock Integration**

1. **Install AWS SDK**:
```bash
pip install boto3
```

2. **Add to requirements.txt**:
```
boto3>=1.34.0
```

3. **Update .env file**:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

4. **Create bedrock_integration.py**:
```python
import boto3
import json
from typing import Dict, Any

class BedrockFactChecker:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime')
        self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def fact_check(self, claim: str) -> Dict[str, Any]:
        prompt = f"""You are a professional fact-checker. Analyze this claim:

Claim: "{claim}"

Respond with JSON format:
{{
    "status": "verified|unverified|partially-verified",
    "confidence": 0.95,
    "explanation": "Detailed explanation",
    "credibility_score": 8.5
}}

Be extremely accurate with geographical facts. Somalia is in East Africa, not Asia."""

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        response = self.bedrock.invoke_model(
            body=body,
            modelId=self.model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        result = json.loads(response['body'].read())
        content = result['content'][0]['text']
        
        try:
            return json.loads(content)
        except:
            return {
                "status": "unverified",
                "confidence": 0.5,
                "explanation": content,
                "credibility_score": 5.0
            }
```

### **OpenAI GPT-4 Integration**

1. **Install OpenAI SDK**:
```bash
pip install openai>=1.0.0
```

2. **Add to .env**:
```env
OPENAI_API_KEY=your_openai_key
```

3. **Create openai_integration.py**:
```python
from openai import OpenAI
import json

class OpenAIFactChecker:
    def __init__(self):
        self.client = OpenAI()
    
    def fact_check(self, claim: str):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional fact-checker with access to accurate geographical and scientific information."},
                {"role": "user", "content": f"Fact-check this claim and respond in JSON: {claim}"}
            ],
            max_tokens=300,
            temperature=0.1
        )
        
        return json.loads(response.choices[0].message.content)
```

### **Google Gemini Integration**

1. **Install Google AI SDK**:
```bash
pip install google-generativeai
```

2. **Add to .env**:
```env
GEMINI_API_KEY=your_gemini_key
```

3. **Create gemini_integration.py**:
```python
import google.generativeai as genai
import json

class GeminiFactChecker:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def fact_check(self, claim: str):
        prompt = f"Fact-check this claim and respond in JSON format: {claim}"
        response = self.model.generate_content(prompt)
        return json.loads(response.text)
```

## 🔧 Integration Steps

### **Step 1: Update ai_fact_checker.py**

```python
# Add to imports
from .bedrock_integration import BedrockFactChecker
from .openai_integration import OpenAIFactChecker
from .gemini_integration import GeminiFactChecker

class AIFactChecker:
    def __init__(self):
        # Existing code...
        
        # Add new AI services
        self.bedrock_checker = BedrockFactChecker() if os.getenv('AWS_ACCESS_KEY_ID') else None
        self.openai_checker = OpenAIFactChecker() if os.getenv('OPENAI_API_KEY') else None
        self.gemini_checker = GeminiFactChecker() if os.getenv('GEMINI_API_KEY') else None
    
    def _check_with_ai_apis(self, claim: str):
        # Try Bedrock first (most reliable)
        if self.bedrock_checker:
            result = self.bedrock_checker.fact_check(claim)
            if result:
                return result
        
        # Try OpenAI GPT-4
        if self.openai_checker:
            result = self.openai_checker.fact_check(claim)
            if result:
                return result
        
        # Try Gemini as fallback
        if self.gemini_checker:
            result = self.gemini_checker.fact_check(claim)
            if result:
                return result
        
        # Existing fallback code...
```

### **Step 2: Update smart_verification.py**

```python
class SmartVerificationEngine:
    def __init__(self):
        # Existing code...
        
        # Enhanced AI fact checker with multiple services
        self.ai_fact_checker = AIFactChecker()
    
    def verify(self, query: str):
        # Existing code with AI fact checking as first step
        # This will now use Bedrock, OpenAI, or Gemini automatically
```

## 🌟 Advanced Features

### **Multi-Model Consensus**

```python
def consensus_fact_check(self, claim: str):
    """Get consensus from multiple AI models"""
    results = []
    
    if self.bedrock_checker:
        results.append(self.bedrock_checker.fact_check(claim))
    
    if self.openai_checker:
        results.append(self.openai_checker.fact_check(claim))
    
    if self.gemini_checker:
        results.append(self.gemini_checker.fact_check(claim))
    
    # Calculate consensus
    avg_score = sum(r['credibility_score'] for r in results) / len(results)
    consensus_status = max(set(r['status'] for r in results), key=[r['status'] for r in results].count)
    
    return {
        'status': consensus_status,
        'credibility_score': avg_score,
        'confidence': 'high' if len(results) >= 2 else 'medium',
        'explanation': f'Consensus from {len(results)} AI models',
        'individual_results': results
    }
```

### **Cost Optimization**

```python
def smart_ai_selection(self, claim: str):
    """Select AI service based on claim complexity and cost"""
    
    # Simple geographical claims -> Use local database
    if any(geo in claim.lower() for geo in ['somalia', 'malaysia', 'thailand', 'africa', 'asia']):
        return self._check_geographical_facts(claim)
    
    # Complex claims -> Use Bedrock (most accurate)
    if len(claim.split()) > 10:
        return self.bedrock_checker.fact_check(claim)
    
    # Simple claims -> Use OpenAI (faster/cheaper)
    return self.openai_checker.fact_check(claim)
```

## 📊 Performance Comparison

| AI Service | Speed | Accuracy | Cost | Best For |
|------------|-------|----------|------|----------|
| **Amazon Bedrock** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Complex fact-checking |
| **OpenAI GPT-4** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | General purpose |
| **Google Gemini** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | High-volume processing |
| **Local Database** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Known facts |

## 🔒 Security Best Practices

1. **Environment Variables**: Store all API keys in `.env` file
2. **Rate Limiting**: Implement request throttling
3. **Error Handling**: Graceful fallbacks between services
4. **Data Privacy**: Don't log sensitive claims
5. **Cost Monitoring**: Track API usage and costs

## 🚀 Deployment

### **AWS Lambda Integration**

```python
import boto3
import json

def lambda_handler(event, context):
    """AWS Lambda function for serverless fact-checking"""
    
    claim = event.get('claim', '')
    
    # Initialize fact checker
    checker = BedrockFactChecker()
    result = checker.fact_check(claim)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
```

### **Docker with AI Services**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . .

# Set environment variables
ENV AWS_DEFAULT_REGION=us-east-1
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["python", "app.py"]
```

## 📈 Monitoring & Analytics

```python
import logging
from datetime import datetime

class AIFactCheckingAnalytics:
    def __init__(self):
        self.metrics = {
            'total_checks': 0,
            'bedrock_usage': 0,
            'openai_usage': 0,
            'gemini_usage': 0,
            'accuracy_scores': []
        }
    
    def log_fact_check(self, service: str, claim: str, result: dict):
        self.metrics['total_checks'] += 1
        self.metrics[f'{service}_usage'] += 1
        self.metrics['accuracy_scores'].append(result['credibility_score'])
        
        logging.info(f"Fact-check: {service} | Claim: {claim[:50]}... | Score: {result['credibility_score']}")
```

## 🎯 Testing

```python
def test_ai_integrations():
    """Test all AI integrations"""
    
    test_claims = [
        "Malaysia is the capital city of Thailand",  # Should be FALSE
        "Somalia is in Africa",                      # Should be TRUE
        "The Earth is flat"                         # Should be FALSE
    ]
    
    checker = AIFactChecker()
    
    for claim in test_claims:
        result = checker.fact_check(claim)
        print(f"Claim: {claim}")
        print(f"Result: {result}")
        print("-" * 50)
```

---

**🎉 Ready to Deploy!**

Your Trustify AI system now supports multiple AI services for enhanced accuracy and reliability. The system automatically falls back between services and provides consensus-based fact-checking.

**Next Steps:**
1. Add your API keys to `.env`
2. Test with the provided examples
3. Deploy to your preferred platform
4. Monitor usage and costs
5. Scale as needed

*Built for accuracy, designed for scale* 🚀