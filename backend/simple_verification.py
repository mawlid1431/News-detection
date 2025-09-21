#!/usr/bin/env python3
"""Simple working verification system"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SimpleVerificationEngine:
    """Simple verification that actually works"""
    
    def __init__(self):
        # Use the working API keys directly
        self.newsapi_key = "ebe74bd45e474f518aa0e4e826a9c086"
        self.currents_key = "e5kXI-_B355CtMY6LPxcyOy8E_sGHEuX0KiewSIxVK0m80eC"
        self.newsdata_key = "pub_2d42cd9cd034467782c3d48ea2015e67"
    
    def verify(self, query: str) -> Dict[str, Any]:
        """Simple verification: found = verified, not found = unverified"""
        start_time = datetime.utcnow()
        
        # Search all available APIs
        all_articles = []
        
        # Try NewsAPI
        if self.newsapi_key:
            articles = self._search_newsapi(query)
            all_articles.extend(articles)
        
        # Try Currents API
        if self.currents_key:
            articles = self._search_currents(query)
            all_articles.extend(articles)
        
        # Try NewsData
        if self.newsdata_key:
            articles = self._search_newsdata(query)
            all_articles.extend(articles)
        
        # Remove duplicates
        unique_articles = self._deduplicate(all_articles)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Apply core logic
        if unique_articles:
            return self._create_verified_response(query, unique_articles, processing_time)
        else:
            return self._create_unverified_response(query, processing_time)
    
    def _search_newsapi(self, query: str) -> List[Dict]:
        """Search NewsAPI"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': self.newsapi_key,
                'language': 'en',
                'pageSize': 10,
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
                
                logger.info(f"NewsAPI: Found {len(articles)} articles")
                return articles
            else:
                logger.warning(f"NewsAPI error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"NewsAPI exception: {e}")
            return []
    
    def _search_currents(self, query: str) -> List[Dict]:
        """Search Currents API"""
        try:
            url = "https://api.currentsapi.services/v1/search"
            params = {
                'keywords': query,
                'apiKey': self.currents_key,
                'language': 'en'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for item in data.get('news', []):
                    if item.get('title') and item.get('url'):
                        articles.append({
                            'title': item.get('title', ''),
                            'description': item.get('description', ''),
                            'url': item.get('url', ''),
                            'source': 'Currents',
                            'published_at': item.get('published', ''),
                            'api_source': 'Currents'
                        })
                
                logger.info(f"Currents: Found {len(articles)} articles")
                return articles
            else:
                logger.warning(f"Currents error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Currents exception: {e}")
            return []
    
    def _search_newsdata(self, query: str) -> List[Dict]:
        """Search NewsData API"""
        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                'apikey': self.newsdata_key,
                'q': query,
                'language': 'en',
                'size': 10
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
                
                logger.info(f"NewsData: Found {len(articles)} articles")
                return articles
            else:
                logger.warning(f"NewsData error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"NewsData exception: {e}")
            return []
    
    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles"""
        seen_titles = set()
        unique = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique.append(article)
        
        return unique[:10]
    
    def _create_verified_response(self, query: str, articles: List[Dict], processing_time: float) -> Dict[str, Any]:
        """Create response for verified information"""
        
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
        summary = f"Found {len(articles)} articles about '{query}' from trusted news sources."
        if articles:
            summary += f" Latest: {articles[0].get('title', '')}"
        
        return {
            'query': query,
            'status': 'verified',
            'credibility_score': min(9.0, 6.0 + len(articles) * 0.3),
            'confidence': 'high',
            'explanation': f'Information verified through {len(articles)} trusted news sources.',
            'summary': summary,
            'official_sources': official_sources,
            'sources_found': len(articles),
            'processing_time_ms': round(processing_time),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _create_unverified_response(self, query: str, processing_time: float) -> Dict[str, Any]:
        """Create response for unverified information"""
        
        return {
            'query': query,
            'status': 'unverified',
            'credibility_score': 2.0,
            'confidence': 'high',
            'explanation': 'This information was not found in trusted news sources.',
            'summary': f'No verified information found about "{query}" in trusted news databases.',
            'official_sources': [],
            'sources_found': 0,
            'processing_time_ms': round(processing_time),
            'timestamp': datetime.utcnow().isoformat(),
            'recommendation': 'Please verify with official sources.'
        }