#!/usr/bin/env python3
"""Smart verification system that learns and improves"""

import os
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any
from fuzzywuzzy import fuzz
from .url_handler import URLHandler
from .ai_fact_checker import AIFactChecker
from .bedrock_integration import BedrockFactChecker

logger = logging.getLogger(__name__)

class SmartVerificationEngine:
    """Smart verification that learns from data"""
    
    def __init__(self):
        # Working API keys
        self.newsapi_key = "ebe74bd45e474f518aa0e4e826a9c086"
        self.newsdata_key = "pub_2d42cd9cd034467782c3d48ea2015e67"
        self.mediastack_key = "d3c3ff2ccab4e1ad84d5b2957cf557e0"
        
        # Knowledge base for learning
        self.knowledge_base = self._load_knowledge_base()
        self.verified_patterns = self._load_verified_patterns()
        self.fake_patterns = self._load_fake_patterns()
        
        # URL handler and AI fact checker
        self.url_handler = URLHandler()
        self.ai_fact_checker = AIFactChecker()
        self.bedrock_checker = BedrockFactChecker()
    
    def _load_knowledge_base(self) -> Dict:
        """Load existing knowledge base"""
        try:
            with open('data/knowledge_base.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'verified_topics': {},
                'fake_topics': {},
                'learning_data': []
            }
    
    def _load_verified_patterns(self) -> List[str]:
        """Load patterns that indicate verified news"""
        return [
            'according to', 'study shows', 'research indicates', 'data reveals',
            'scientists confirm', 'experts say', 'official statement', 'government announces',
            'peer-reviewed', 'published in', 'clinical trial', 'evidence suggests',
            'WHO reports', 'CDC confirms', 'university study', 'medical journal'
        ]
    
    def _load_fake_patterns(self) -> List[str]:
        """Load patterns that indicate fake news"""
        return [
            'shocking truth', 'they dont want you to know', 'secret revealed',
            'miracle cure', 'doctors hate this', 'unbelievable discovery',
            'conspiracy exposed', 'hidden agenda', 'big pharma', 'government coverup',
            'click here', 'you wont believe', 'amazing secret', 'forbidden knowledge',
            # Geographical false claims
            'malaysia.*capital.*thailand', 'somalia.*asia', 'somalia.*thailand',
            'malaysia.*africa', 'thailand.*capital.*malaysia'
        ]
    
    def verify(self, query: str) -> Dict[str, Any]:
        """Smart verification with learning"""
        start_time = datetime.utcnow()
        
        # Step 0: Check if query is a URL
        if self.url_handler.is_url(query):
            return self._verify_url(query, start_time)
        
        # Step 1: Bedrock AI Fact Checking (Highest priority)
        if self.bedrock_checker.available:
            bedrock_result = self.bedrock_checker.fact_check(query)
            if bedrock_result and bedrock_result['status'] == 'unverified' and bedrock_result['credibility_score'] < 3.0:
                return self._add_metadata({
                    'query': query,
                    'status': 'unverified',
                    'credibility_score': bedrock_result['credibility_score'],
                    'confidence': 'high',
                    'explanation': bedrock_result['explanation'],
                    'summary': f'Bedrock AI analysis: {bedrock_result["explanation"]}',
                    'official_sources': [],
                    'sources_found': 0,
                    'method': 'bedrock_ai'
                }, start_time)
        
        # Step 2: Fallback AI Fact Checking
        ai_result = self.ai_fact_checker.fact_check(query)
        if ai_result['status'] == 'false':
            return self._add_metadata({
                'query': query,
                'status': 'unverified',
                'credibility_score': 0.5,
                'confidence': 'high',
                'explanation': ai_result['explanation'],
                'summary': f'Fact-check failed: {ai_result["explanation"]}',
                'official_sources': [],
                'sources_found': 0,
                'method': 'ai_fact_check'
            }, start_time)
        
        # Step 3: Check knowledge base
        kb_result = self._check_knowledge_base(query)
        if kb_result:
            return self._add_metadata(kb_result, start_time)
        
        # Step 4: Pattern analysis
        pattern_score = self._analyze_patterns(query)
        
        # Step 5: API search
        articles = self._search_all_apis(query)
        
        # Step 6: Content analysis
        content_score = self._analyze_content(query, articles)
        
        # Step 7: Smart decision making
        result = self._make_smart_decision(query, articles, pattern_score, content_score)
        
        # Step 8: Learn from this verification
        self._learn_from_verification(query, result, articles)
        
        return self._add_metadata(result, start_time)
    
    def _check_knowledge_base(self, query: str) -> Dict[str, Any]:
        """Check if we already know about this topic"""
        query_lower = query.lower()
        
        # Check verified topics
        for topic, data in self.knowledge_base.get('verified_topics', {}).items():
            if fuzz.ratio(query_lower, topic.lower()) > 80:
                return {
                    'query': query,
                    'status': 'verified',
                    'credibility_score': data['score'],
                    'confidence': 'high',
                    'explanation': f'Previously verified: {data["explanation"]}',
                    'summary': data['summary'],
                    'official_sources': data.get('sources', []),
                    'sources_found': len(data.get('sources', [])),
                    'method': 'knowledge_base'
                }
        
        # Check fake topics
        for topic, data in self.knowledge_base.get('fake_topics', {}).items():
            if fuzz.ratio(query_lower, topic.lower()) > 80:
                return {
                    'query': query,
                    'status': 'unverified',
                    'credibility_score': data['score'],
                    'confidence': 'high',
                    'explanation': f'Previously identified as false: {data["explanation"]}',
                    'summary': data['summary'],
                    'official_sources': [],
                    'sources_found': 0,
                    'method': 'knowledge_base'
                }
        
        return None
    
    def _analyze_patterns(self, query: str) -> float:
        """Analyze text patterns to predict credibility"""
        query_lower = query.lower()
        
        verified_score = 0
        fake_score = 0
        
        # Check for verified patterns
        for pattern in self.verified_patterns:
            if pattern in query_lower:
                verified_score += 1
        
        # Check for fake patterns
        for pattern in self.fake_patterns:
            if pattern in query_lower:
                fake_score += 2  # Fake patterns are stronger indicators
        
        # Calculate pattern score (-1 to 1)
        if verified_score > fake_score:
            return min(1.0, verified_score / 5)
        elif fake_score > verified_score:
            return max(-1.0, -fake_score / 5)
        else:
            return 0.0
    
    def _search_all_apis(self, query: str) -> List[Dict]:
        """Search all available APIs"""
        all_articles = []
        
        # NewsAPI
        articles = self._search_newsapi(query)
        all_articles.extend(articles)
        
        # NewsData
        articles = self._search_newsdata(query)
        all_articles.extend(articles)
        
        # MediaStack
        articles = self._search_mediastack(query)
        all_articles.extend(articles)
        
        return self._deduplicate(all_articles)
    
    def _search_newsapi(self, query: str) -> List[Dict]:
        """Search NewsAPI"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': self.newsapi_key,
                'language': 'en',
                'pageSize': 15,
                'sortBy': 'relevancy'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for item in data.get('articles', []):
                    if item.get('title') and item.get('url'):
                        articles.append({
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'url': item.get('url', ''),
                            'source': item.get('source', {}).get('name', 'NewsAPI'),
                            'published_at': item.get('publishedAt', ''),
                            'api_source': 'NewsAPI'
                        })
                
                return articles
            
        except Exception as e:
            logger.error(f"NewsAPI error: {e}")
        
        return []
    
    def _search_newsdata(self, query: str) -> List[Dict]:
        """Search NewsData"""
        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                'apikey': self.newsdata_key,
                'q': query,
                'language': 'en',
                'size': 15
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for item in data.get('results', []):
                    if item.get('title') and item.get('link'):
                        articles.append({
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'url': item.get('link', ''),
                            'source': item.get('source_id', 'NewsData'),
                            'published_at': item.get('pubDate', ''),
                            'api_source': 'NewsData'
                        })
                
                return articles
            
        except Exception as e:
            logger.error(f"NewsData error: {e}")
        
        return []
    
    def _search_mediastack(self, query: str) -> List[Dict]:
        """Search MediaStack"""
        try:
            url = "http://api.mediastack.com/v1/news"
            params = {
                'access_key': self.mediastack_key,
                'keywords': query,
                'languages': 'en',
                'limit': 15
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for item in data.get('data', []):
                    if item.get('title') and item.get('url'):
                        articles.append({
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'url': item.get('url', ''),
                            'source': item.get('source', 'MediaStack'),
                            'published_at': item.get('published_at', ''),
                            'api_source': 'MediaStack'
                        })
                
                return articles
            
        except Exception as e:
            logger.error(f"MediaStack error: {e}")
        
        return []
    
    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen:
                seen.add(title)
                unique.append(article)
        
        return unique
    
    def _analyze_content(self, query: str, articles: List[Dict]) -> float:
        """Analyze content quality and relevance"""
        if not articles:
            return 0.0
        
        relevance_scores = []
        quality_scores = []
        
        for article in articles:
            # Relevance score
            title_sim = fuzz.ratio(query.lower(), article.get('title', '').lower()) / 100
            desc_sim = fuzz.partial_ratio(query.lower(), article.get('description', '').lower()) / 100
            relevance = (title_sim * 0.7 + desc_sim * 0.3)
            relevance_scores.append(relevance)
            
            # Quality score based on source
            source = article.get('source', '').lower()
            if any(trusted in source for trusted in ['bbc', 'reuters', 'ap', 'cnn', 'guardian']):
                quality_scores.append(0.9)
            elif any(trusted in source for trusted in ['times', 'post', 'news']):
                quality_scores.append(0.7)
            else:
                quality_scores.append(0.5)
        
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        return (avg_relevance * 0.6 + avg_quality * 0.4)
    
    def _make_smart_decision(self, query: str, articles: List[Dict], pattern_score: float, content_score: float) -> Dict[str, Any]:
        """Make intelligent verification decision"""
        
        # Base score from articles found
        base_score = 3.0 if not articles else min(8.0, 5.0 + len(articles) * 0.3)
        
        # Adjust with pattern analysis
        pattern_adjustment = pattern_score * 2.0
        
        # Adjust with content quality
        content_adjustment = content_score * 2.0
        
        # Final score
        final_score = max(1.0, min(10.0, base_score + pattern_adjustment + content_adjustment))
        
        # Determine status
        if final_score >= 7.0 and articles:
            status = 'verified'
            explanation = f'Verified through {len(articles)} sources with high confidence.'
        elif final_score >= 5.0 and articles:
            status = 'partially-verified'
            explanation = f'Partially verified through {len(articles)} sources.'
        else:
            status = 'unverified'
            explanation = 'Could not verify through trusted sources.'
        
        # Create official sources
        official_sources = []
        for article in articles[:5]:
            official_sources.append({
                'title': article.get('title', 'Read More'),
                'url': article.get('url', ''),
                'source': article.get('source', 'News Source'),
                'published_at': article.get('published_at', '')
            })
        
        # Generate summary
        if articles:
            summary = f"Found {len(articles)} articles about '{query}'. "
            if articles[0].get('title'):
                summary += f"Latest: {articles[0]['title'][:100]}..."
        else:
            summary = f"No verified information found about '{query}' in trusted sources."
        
        return {
            'query': query,
            'status': status,
            'credibility_score': round(final_score, 1),
            'confidence': 'high' if final_score > 7 or final_score < 3 else 'medium',
            'explanation': explanation,
            'summary': summary,
            'official_sources': official_sources,
            'sources_found': len(articles),
            'pattern_score': pattern_score,
            'content_score': content_score
        }
    
    def _learn_from_verification(self, query: str, result: Dict, articles: List[Dict]):
        """Learn from this verification for future use"""
        try:
            # Add to learning data
            learning_entry = {
                'query': query,
                'result': result,
                'timestamp': datetime.utcnow().isoformat(),
                'sources_count': len(articles)
            }
            
            self.knowledge_base['learning_data'].append(learning_entry)
            
            # Update topic knowledge
            if result['status'] == 'verified' and result['credibility_score'] >= 7:
                self.knowledge_base['verified_topics'][query.lower()] = {
                    'score': result['credibility_score'],
                    'explanation': result['explanation'],
                    'summary': result['summary'],
                    'sources': result['official_sources'],
                    'learned_at': datetime.utcnow().isoformat()
                }
            elif result['status'] == 'unverified' and result['credibility_score'] <= 3:
                self.knowledge_base['fake_topics'][query.lower()] = {
                    'score': result['credibility_score'],
                    'explanation': result['explanation'],
                    'summary': result['summary'],
                    'learned_at': datetime.utcnow().isoformat()
                }
            
            # Save knowledge base
            self._save_knowledge_base()
            
        except Exception as e:
            logger.error(f"Learning error: {e}")
    
    def _save_knowledge_base(self):
        """Save knowledge base to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/knowledge_base.json', 'w') as f:
                json.dump(self.knowledge_base, f, indent=2)
        except Exception as e:
            logger.error(f"Save error: {e}")
    
    def _add_metadata(self, result: Dict, start_time: datetime) -> Dict[str, Any]:
        """Add processing metadata"""
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.update({
            'processing_time_ms': round(processing_time),
            'timestamp': datetime.utcnow().isoformat()
        })
        return result
    
    def _verify_url(self, url: str, start_time: datetime) -> Dict[str, Any]:
        """Verify content from URL"""
        
        # Extract content from URL
        url_content = self.url_handler.extract_content(url)
        
        if not url_content:
            return self._add_metadata({
                'query': url,
                'status': 'unverified',
                'credibility_score': 2.0,
                'confidence': 'high',
                'explanation': 'Could not extract content from the provided URL.',
                'summary': 'Unable to access or parse the article content.',
                'official_sources': [],
                'sources_found': 0,
                'method': 'url_extraction_failed'
            }, start_time)
        
        # Verify the extracted content
        title = url_content['title']
        content = url_content['content']
        source = url_content['source']
        
        # Check if it's from a trusted source
        trusted_sources = ['bbc', 'reuters', 'ap', 'cnn', 'guardian', 'nytimes', 'washingtonpost']
        is_trusted = any(trusted in url_content['domain'].lower() for trusted in trusted_sources)
        
        # Search for similar content in APIs to verify
        search_query = title[:100]  # Use title as search query
        articles = self._search_all_apis(search_query)
        
        # Calculate credibility based on source and verification
        base_score = 8.0 if is_trusted else 6.0
        verification_bonus = min(2.0, len(articles) * 0.3)
        final_score = min(9.5, base_score + verification_bonus)
        
        # Determine status
        if final_score >= 7.0:
            status = 'verified'
            explanation = f'Article from {source} verified. Content found in trusted source.'
        else:
            status = 'partially-verified'
            explanation = f'Article from {source}. Limited verification from other sources.'
        
        return self._add_metadata({
            'query': url,
            'status': status,
            'credibility_score': round(final_score, 1),
            'confidence': 'high',
            'explanation': explanation,
            'summary': f'Article: "{title}" from {source}. {content[:200]}...',
            'official_sources': [{
                'title': title,
                'url': url,
                'source': source,
                'published_at': ''
            }],
            'sources_found': 1,
            'method': 'url_verification',
            'extracted_title': title,
            'source_domain': url_content['domain']
        }, start_time)