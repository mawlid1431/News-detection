#!/usr/bin/env python3
"""
Core Verification Logic - Simple and Direct
Connects to trusted APIs, fetches results, and provides clear responses
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class CoreVerificationEngine:
    """Core verification logic - simple and direct"""
    
    def __init__(self):
        self.trusted_apis = self._initialize_trusted_apis()
        
    def _initialize_trusted_apis(self) -> List[Dict]:
        """Initialize trusted news APIs and RSS feeds"""
        apis = [
            {
                'name': 'NewsAPI',
                'url': 'https://newsapi.org/v2/everything',
                'key': os.getenv('NEWSAPI_KEY'),
                'params_template': {'q': '{query}', 'apiKey': '{key}', 'language': 'en', 'pageSize': 10}
            },
            {
                'name': 'Currents',
                'url': 'https://api.currentsapi.services/v1/search',
                'key': os.getenv('CURRENTS_API_KEY'),
                'params_template': {'keywords': '{query}', 'apiKey': '{key}', 'language': 'en'}
            },
            {
                'name': 'NewsData',
                'url': 'https://newsdata.io/api/1/news',
                'key': os.getenv('NEWSDATA_IO_KEY'),
                'params_template': {'apikey': '{key}', 'q': '{query}', 'language': 'en', 'size': 10}
            }
        ]
        
        # Add RSS feeds as backup
        rss_feeds = [
            {'name': 'BBC', 'url': 'http://feeds.bbci.co.uk/news/rss.xml'},
            {'name': 'Reuters', 'url': 'http://feeds.reuters.com/reuters/topNews'},
            {'name': 'CNN', 'url': 'http://rss.cnn.com/rss/edition.rss'}
        ]
        
        return apis
    
    def verify(self, query: str) -> Dict[str, Any]:
        """
        Core verification logic:
        1. Check trusted APIs
        2. If found: summarize and provide sources
        3. If not found: respond that it's not true
        """
        start_time = datetime.utcnow()
        
        # Step 1: Search trusted sources
        found_articles = self._search_trusted_sources(query)
        
        # Step 2: Apply core logic
        if found_articles:
            # Information found - summarize and provide sources
            result = self._process_found_information(query, found_articles)
        else:
            # Information not found - respond that it's not true
            result = self._process_not_found(query)
        
        # Add processing metadata
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.update({
            'processing_time_ms': round(processing_time),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        return result
    
    def _search_trusted_sources(self, query: str) -> List[Dict]:
        """Search all trusted APIs in parallel"""
        all_articles = []
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            
            for api in self.trusted_apis:
                if api['key']:  # Only use APIs with valid keys
                    future = executor.submit(self._query_api, api, query)
                    futures.append(future)
            
            for future in as_completed(futures):
                try:
                    articles = future.result(timeout=10)
                    all_articles.extend(articles)
                except Exception as e:
                    logger.warning(f"API query failed: {e}")
        
        return self._deduplicate_articles(all_articles)
    
    def _query_api(self, api: Dict, query: str) -> List[Dict]:
        """Query a single API"""
        try:
            params = {}
            for key, template in api['params_template'].items():
                params[key] = template.format(query=query, key=api['key'])
            
            response = requests.get(api['url'], params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = self._extract_articles(data, api['name'])
                logger.info(f"{api['name']}: Found {len(articles)} articles")
                return articles
            else:
                logger.warning(f"{api['name']}: HTTP {response.status_code} - {response.text[:200]}")
                return []
            
        except Exception as e:
            logger.error(f"{api['name']} API error: {e}")
            return []
    
    def _extract_articles(self, data: Dict, api_name: str) -> List[Dict]:
        """Extract articles from API response"""
        articles = []
        
        if api_name == 'GNews':
            for item in data.get('articles', []):
                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', {}).get('name', api_name),
                    'published_at': item.get('publishedAt', ''),
                    'api_source': api_name
                })
        
        elif api_name == 'NewsAPI':
            for item in data.get('articles', []):
                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'source': item.get('source', {}).get('name', api_name),
                    'published_at': item.get('publishedAt', ''),
                    'api_source': api_name
                })
        
        elif api_name == 'Currents':
            for item in data.get('news', []):
                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'source': api_name,
                    'published_at': item.get('published', ''),
                    'api_source': api_name
                })
        
        elif api_name == 'NewsData':
            for item in data.get('results', []):
                articles.append({
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'url': item.get('link', ''),
                    'source': item.get('source_id', api_name),
                    'published_at': item.get('pubDate', ''),
                    'api_source': api_name
                })
        
        return articles
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_articles.append(article)
        
        return unique_articles[:10]  # Limit to top 10
    
    def _process_found_information(self, query: str, articles: List[Dict]) -> Dict[str, Any]:
        """Process when information is found in trusted sources"""
        
        # Generate summary from found articles
        summary = self._generate_summary(articles, query)
        
        # Format official sources
        official_sources = []
        for article in articles[:5]:  # Top 5 sources
            if article.get('url'):  # Only include articles with URLs
                official_sources.append({
                    'title': article.get('title', 'Read More'),
                    'url': article.get('url', ''),
                    'source': article.get('source', 'News Source'),
                    'published_at': article.get('published_at', '')
                })
        
        # Calculate score based on number of sources
        score = min(9.0, 6.0 + (len(articles) * 0.5))
        
        return {
            'query': query,
            'status': 'verified',
            'credibility_score': score,
            'confidence': 'high',
            'explanation': f'Information found in {len(articles)} trusted news sources.',
            'summary': summary,
            'official_sources': official_sources,
            'sources_found': len(articles),
            'verification_method': 'trusted_api_search'
        }
    
    def _process_not_found(self, query: str) -> Dict[str, Any]:
        """Process when information is not found in trusted sources"""
        
        return {
            'query': query,
            'status': 'unverified',
            'credibility_score': 2.0,  # Low score for not found
            'confidence': 'high',
            'explanation': 'This information was not found in our trusted news sources and cannot be verified.',
            'summary': f'No verified information found about "{query}" in trusted news databases. This claim cannot be confirmed through reliable sources.',
            'official_sources': [],
            'sources_found': 0,
            'verification_method': 'trusted_api_search',
            'recommendation': 'Please verify the source of this information and check with official authorities.'
        }
    
    def _generate_summary(self, articles: List[Dict], query: str) -> str:
        """Generate summary from found articles"""
        if not articles:
            return f'No information found about "{query}".'
        
        # Extract key information
        titles = [article.get('title', '') for article in articles[:3]]
        descriptions = [article.get('description', '') for article in articles[:3]]
        
        # Create summary
        summary_parts = []
        summary_parts.append(f'Found {len(articles)} articles about "{query}" from trusted sources.')
        
        if titles:
            summary_parts.append('Key headlines include:')
            for i, title in enumerate(titles[:2], 1):
                if title:
                    summary_parts.append(f'{i}. {title}')
        
        return ' '.join(summary_parts)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of trusted APIs"""
        working_apis = sum(1 for api in self.trusted_apis if api['key'])
        total_apis = len(self.trusted_apis)
        
        return {
            'total_apis': total_apis,
            'working_apis': working_apis,
            'status': 'healthy' if working_apis > 0 else 'limited',
            'api_details': [
                {
                    'name': api['name'],
                    'status': 'configured' if api['key'] else 'missing_key'
                }
                for api in self.trusted_apis
            ]
        }