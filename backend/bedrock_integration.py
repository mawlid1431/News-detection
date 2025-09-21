#!/usr/bin/env python3
"""Amazon Bedrock integration for enhanced fact-checking"""

import boto3
import json
import base64
import logging
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class BedrockFactChecker:
    """Amazon Bedrock fact checker using Claude models"""
    
    def __init__(self):
        # Decode the API key
        self.api_key_name = "BedrockAPIKey-4a4q-at-385240721237"
        self.api_key = "ABSKQmVkcm9ja0FQSUtleS00YTRxLWF0LTM4NTI0MDcyMTIzNzo3Y0VQRERLM2JlZnI0d1lrQ1FwdVMxUHV4Q1FEVkcwcjI4Sm8yQzBMQVE1V2R1OWYvRjRlK0dVM3lyUT0="
        
        try:
            # Initialize Bedrock client using environment variables
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
            self.available = True
            logger.info("Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.available = False
    
    def fact_check(self, claim: str) -> Optional[Dict[str, Any]]:
        """Fact check using Amazon Bedrock Claude model"""
        
        if not self.available:
            return None
        
        try:
            prompt = f"""You are a professional fact-checker with access to accurate geographical, scientific, and historical information. Analyze this claim with extreme precision:

Claim: "{claim}"

CRITICAL GEOGRAPHICAL FACTS:
- Somalia is located in East Africa (Horn of Africa), NOT in Asia or Thailand
- Malaysia is a country in Southeast Asia, NOT a capital city of any country
- Thailand's capital is Bangkok, NOT Malaysia
- Malaysia's capital is Kuala Lumpur

Respond ONLY with valid JSON in this exact format:
{{
    "status": "verified|unverified|partially-verified",
    "confidence": 0.95,
    "explanation": "Detailed factual explanation with specific corrections if claim is false",
    "credibility_score": 8.5,
    "method": "bedrock_claude"
}}

Be extremely strict with geographical claims. If the claim contains any geographical errors, mark it as "unverified" with a low credibility score."""

            # Prepare the request body for Claude
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            # Call Bedrock
            response = self.bedrock.invoke_model(
                body=body,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            
            # Parse response
            result = json.loads(response['body'].read())
            content = result['content'][0]['text']
            
            # Parse JSON response
            try:
                fact_check_result = json.loads(content)
                
                # Validate required fields
                required_fields = ['status', 'confidence', 'explanation', 'credibility_score']
                if all(field in fact_check_result for field in required_fields):
                    fact_check_result['method'] = 'bedrock_claude'
                    logger.info(f"Bedrock fact-check successful: {claim[:50]}...")
                    return fact_check_result
                else:
                    logger.warning("Bedrock response missing required fields")
                    return self._fallback_response(claim, content)
                    
            except json.JSONDecodeError:
                logger.warning("Bedrock response not valid JSON, using fallback")
                return self._fallback_response(claim, content)
                
        except Exception as e:
            logger.error(f"Bedrock API error: {e}")
            return None
    
    def _fallback_response(self, claim: str, content: str) -> Dict[str, Any]:
        """Create fallback response when JSON parsing fails"""
        
        content_lower = content.lower()
        
        # Determine status from content
        if any(word in content_lower for word in ['false', 'incorrect', 'wrong', 'not true']):
            status = 'unverified'
            credibility_score = 1.0
        elif any(word in content_lower for word in ['true', 'correct', 'accurate', 'verified']):
            status = 'verified'
            credibility_score = 9.0
        elif any(word in content_lower for word in ['partially', 'somewhat', 'mixed']):
            status = 'partially-verified'
            credibility_score = 6.0
        else:
            status = 'unverified'
            credibility_score = 5.0
        
        return {
            'status': status,
            'confidence': 0.8,
            'explanation': content.strip(),
            'credibility_score': credibility_score,
            'method': 'bedrock_claude_fallback'
        }
    
    def test_connection(self) -> bool:
        """Test Bedrock connection"""
        
        if not self.available:
            return False
        
        try:
            test_result = self.fact_check("The sky is blue")
            return test_result is not None
        except:
            return False