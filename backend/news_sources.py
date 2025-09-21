import os
import requests
import feedparser
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)

class NewsSourceManager:
    """Enhanced news source manager with working APIs and RSS feeds"""
    
    def __init__(self):
        # Only include working API keys
        self.api_keys = {
            'newsapi': os.getenv('NEWSAPI_KEY'),
            'newsdata': os.getenv('NEWSDATA_IO_KEY'),
            'mediastack': os.getenv('MEDIASTACK_KEY'),
            'thenewsapi': os.getenv('THENEWSAPI_KEY'),
            'worldnews': os.getenv('WOLRDNEWS_API_KEY'),
            # Backup APIs (may have quota issues but keep for retry)
            'gnews': os.getenv('GNEWS_API_KEY'),
            'currents': os.getenv('CURRENTS_API_KEY'),
            'guardian': os.getenv('GUARDIAN_API_KEY')
        }
        
        # HTTP headers to avoid blocking
        self.headers = {
            'User-Agent': 'Trustify-AI-Bot/1.0 (News Verification Service)',
            'Accept': 'application/rss+xml, application/xml, text/xml'
        }
        
        self.sources = self._initialize_working_sources()
        
    def _initialize_working_sources(self) -> List[Dict]:
        """Initialize only working news sources"""
        return [
            # Working International RSS Sources
            {'name': 'BBC News', 'type': 'rss', 'url': 'https://feeds.bbci.co.uk/news/rss.xml', 'credibility': 9.2, 'status': 'working'},
            {'name': 'CNN', 'type': 'rss', 'url': 'http://rss.cnn.com/rss/edition.rss', 'credibility': 8.5, 'status': 'working'},
            {'name': 'Al Jazeera', 'type': 'rss', 'url': 'https://www.aljazeera.com/xml/rss/all.xml', 'credibility': 8.7, 'status': 'working'},
            {'name': 'NPR', 'type': 'rss', 'url': 'https://feeds.npr.org/1001/rss.xml', 'credibility': 8.8, 'status': 'working'},
            {'name': 'Deutsche Welle', 'type': 'rss', 'url': 'https://rss.dw.com/xml/rss-en-all', 'credibility': 8.8, 'status': 'working'},
            {'name': 'France 24', 'type': 'rss', 'url': 'https://www.france24.com/en/rss', 'credibility': 8.6, 'status': 'working'},
            {'name': 'CBS News', 'type': 'rss', 'url': 'https://www.cbsnews.com/latest/rss/main', 'credibility': 8.6, 'status': 'working'},
            {'name': 'The Guardian', 'type': 'rss', 'url': 'https://www.theguardian.com/world/rss', 'credibility': 8.9, 'status': 'working'},
            {'name': 'NHK World', 'type': 'rss', 'url': 'https://www3.nhk.or.jp/rss/news/cat0.xml', 'credibility': 8.6, 'status': 'working'},
            {'name': 'Sky News', 'type': 'rss', 'url': 'http://feeds.skynews.com/feeds/rss/home.xml', 'credibility': 8.4, 'status': 'working'},
            {'name': 'ABC News', 'type': 'rss', 'url': 'https://abcnews.go.com/abcnews/topstories', 'credibility': 8.5, 'status': 'working'},
            
            # Backup Sources (may have issues but try anyway)
            {'name': 'Reuters', 'type': 'rss', 'url': 'https://feeds.reuters.com/reuters/topNews', 'credibility': 9.5, 'status': 'backup'},
            {'name': 'Associated Press', 'type': 'rss', 'url': 'https://apnews.com/apf-topnews', 'credibility': 9.4, 'status': 'backup'},
            
            # Malaysian Sources (some may have issues)
            {'name': 'The Star', 'type': 'rss', 'url': 'https://www.thestar.com.my/rss/news/', 'credibility': 8.8, 'status': 'backup'},
            {'name': 'Free Malaysia Today', 'type': 'rss', 'url': 'https://www.freemalaysiatoday.com/feed/', 'credibility': 8.2, 'status': 'backup'},
            
            # Working API Sources
            {'name': 'NewsAPI.org', 'type': 'api', 'credibility': 8.2, 'status': 'working'},
            {'name': 'NewsData.io', 'type': 'api', 'credibility': 8.0, 'status': 'working'},
            {'name': 'MediaStack', 'type': 'api', 'credibility': 7.8, 'status': 'working'},
            {'name': 'The News API', 'type': 'api', 'credibility': 8.1, 'status': 'working'},
            {'name': 'World News API', 'type': 'api', 'credibility': 7.9, 'status': 'working'},
            
            # Backup API Sources (quota issues)
            {'name': 'GNews', 'type': 'api', 'credibility': 8.0, 'status': 'quota_limited'},
            {'name': 'Currents API', 'type': 'api', 'credibility': 7.8, 'status': 'quota_limited'},
            {'name': 'Guardian API', 'type': 'api', 'credibility': 8.9, 'status': 'auth_issue'},
        ]
    
    def search_news(self, query: str, max_results: int = 20) -> List[Dict]:
        """Enhanced search with robust error handling and working sources priority"""
        all_articles = []
        
        # Use ThreadPoolExecutor for parallel requests with timeout
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            # Priority 1: Working API sources
            if self.api_keys['newsapi']:
                futures.append(executor.submit(self._search_newsapi_enhanced, query))
            if self.api_keys['newsdata']:
                futures.append(executor.submit(self._search_newsdata_enhanced, query))
            if self.api_keys['mediastack']:
                futures.append(executor.submit(self._search_mediastack_enhanced, query))
            if self.api_keys['thenewsapi']:
                futures.append(executor.submit(self._search_thenewsapi_enhanced, query))
            if self.api_keys['worldnews']:
                futures.append(executor.submit(self._search_worldnews_enhanced, query))
            
            # Priority 2: Working RSS sources
            working_rss = [s for s in self.sources if s['type'] == 'rss' and s.get('status') == 'working']
            for source in working_rss[:8]:  # Limit to 8 RSS sources for speed
                futures.append(executor.submit(self._search_rss_enhanced, source, query))
            
            # Priority 3: Backup APIs (try but with shorter timeout)
            if self.api_keys['gnews']:
                futures.append(executor.submit(self._search_gnews_backup, query))
            
            # Collect results with timeout protection
            for future in as_completed(futures, timeout=30):
                try:
                    articles = future.result(timeout=8)
                    if articles:
                        all_articles.extend(articles)
                except Exception as e:
                    logger.warning(f"Source search failed: {str(e)}")
        
        # Remove duplicates and sort by credibility + relevance
        unique_articles = self._deduplicate_and_rank_articles(all_articles, query)
        return unique_articles[:max_results]
    
    def _search_newsapi_enhanced(self, query: str) -> List[Dict]:
        """Enhanced NewsAPI search with better error handling"""
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': self.api_keys['newsapi'],
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': 10
            }
            
            response = requests.get(url, params=params, timeout=12, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                # Skip removed articles
                if article.get('title') == '[Removed]' or not article.get('title'):
                    continue
                    
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'NewsAPI'),
                    'published_at': article.get('publishedAt', ''),
                    'credibility': 8.2,
                    'api_source': 'newsapi'
                })
            
            logger.info(f"NewsAPI: Retrieved {len(articles)} articles")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"NewsAPI request error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"NewsAPI error: {str(e)}")
            return []
    
    def _search_newsdata_enhanced(self, query: str) -> List[Dict]:
        """Enhanced NewsData.io search"""
        try:
            url = "https://newsdata.io/api/1/news"
            params = {
                'apikey': self.api_keys['newsdata'],
                'q': query,
                'language': 'en'
            }
            
            response = requests.get(url, params=params, timeout=12, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('results', []):
                if article.get('title'):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('link', ''),
                        'source': article.get('source_id', 'NewsData.io'),
                        'published_at': article.get('pubDate', ''),
                        'credibility': 8.0,
                        'api_source': 'newsdata'
                    })
            
            logger.info(f"NewsData.io: Retrieved {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"NewsData.io error: {str(e)}")
            return []
    
    def _search_mediastack_enhanced(self, query: str) -> List[Dict]:
        """Enhanced MediaStack search"""
        try:
            url = "http://api.mediastack.com/v1/news"
            params = {
                'access_key': self.api_keys['mediastack'],
                'keywords': query,
                'languages': 'en'
            }
            
            response = requests.get(url, params=params, timeout=12, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('data', []):
                if article.get('title'):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', 'MediaStack'),
                        'published_at': article.get('published_at', ''),
                        'credibility': 7.8,
                        'api_source': 'mediastack'
                    })
            
            logger.info(f"MediaStack: Retrieved {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"MediaStack error: {str(e)}")
            return []
    
    def _search_thenewsapi_enhanced(self, query: str) -> List[Dict]:
        """Enhanced The News API search"""
        try:
            url = "https://api.thenewsapi.com/v1/news/all"
            params = {
                'api_token': self.api_keys['thenewsapi'],
                'search': query,
                'language': 'en',
                'limit': 8
            }
            
            response = requests.get(url, params=params, timeout=12, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('data', []):
                if article.get('title'):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', 'TheNewsAPI'),
                        'published_at': article.get('published_at', ''),
                        'credibility': 8.1,
                        'api_source': 'thenewsapi'
                    })
            
            logger.info(f"The News API: Retrieved {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"The News API error: {str(e)}")
            return []
    
    def _search_worldnews_enhanced(self, query: str) -> List[Dict]:
        """Enhanced World News API search"""
        try:
            url = "https://api.worldnewsapi.com/search-news"
            params = {
                'api-key': self.api_keys['worldnews'],
                'text': query,
                'number': 8
            }
            
            response = requests.get(url, params=params, timeout=12, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for article in data.get('news', []):
                if article.get('title'):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('summary', ''),
                        'url': article.get('url', ''),
                        'source': article.get('author', 'WorldNewsAPI'),
                        'published_at': article.get('publish_date', ''),
                        'credibility': 7.9,
                        'api_source': 'worldnews'
                    })
            
            logger.info(f"World News API: Retrieved {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"World News API error: {str(e)}")
            return []
    
    def _search_rss_enhanced(self, source: Dict, query: str) -> List[Dict]:
        """Enhanced RSS search with better error handling"""
        try:
            feed = feedparser.parse(source['url'])
            articles = []
            
            if hasattr(feed, 'entries') and len(feed.entries) > 0:
                for entry in feed.entries[:15]:
                    title = entry.get('title', '')
                    description = entry.get('description', '') or entry.get('summary', '')
                    
                    # Enhanced relevance check
                    if self._is_relevant(title, description, query):
                        articles.append({
                            'title': title,
                            'description': description,
                            'url': entry.get('link', ''),
                            'source': source['name'],
                            'published_at': entry.get('published', ''),
                            'credibility': source['credibility'],
                            'api_source': 'rss'
                        })
            
            if articles:
                logger.info(f"{source['name']} RSS: Retrieved {len(articles)} relevant articles")
            return articles
            
        except Exception as e:
            logger.warning(f"RSS search error for {source['name']}: {str(e)}")
            return []
    
    def _search_gnews_backup(self, query: str) -> List[Dict]:
        """Backup GNews search with quota handling"""
        try:
            url = "https://gnews.io/api/v4/search"
            params = {
                'q': query,
                'token': self.api_keys['gnews'],
                'lang': 'en',
                'max': 5
            }
            
            response = requests.get(url, params=params, timeout=8)
            
            if response.status_code == 403:
                logger.warning("GNews: Daily quota exceeded")
                return []
            
            response.raise_for_status()
            data = response.json()
            articles = []
            
            for article in data.get('articles', []):
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'source': article.get('source', {}).get('name', 'GNews'),
                    'published_at': article.get('publishedAt', ''),
                    'credibility': 8.0,
                    'api_source': 'gnews'
                })
            
            logger.info(f"GNews (backup): Retrieved {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.warning(f"GNews backup error: {str(e)}")
            return []
    
    def _is_relevant(self, title: str, description: str, query: str) -> bool:
        """Enhanced relevance checking"""
        if not title and not description:
            return False
        
        # Convert to lowercase for comparison
        title_lower = title.lower()
        desc_lower = description.lower()
        query_lower = query.lower()
        
        # Check for exact query match
        if query_lower in title_lower or query_lower in desc_lower:
            return True
        
        # Check for individual query words
        query_words = query_lower.split()
        if len(query_words) > 1:
            # At least 60% of query words should be present
            matches = sum(1 for word in query_words 
                         if word in title_lower or word in desc_lower)
            return matches >= len(query_words) * 0.6
        
        return False
    
    def _deduplicate_and_rank_articles(self, articles: List[Dict], query: str) -> List[Dict]:
        """Enhanced deduplication and ranking by credibility and relevance"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title = article.get('title', '').lower().strip()
            if title and title not in seen_titles and len(title) > 10:
                # Add relevance score
                article['relevance_score'] = self._calculate_relevance_score(article, query)
                # Add combined score (credibility + relevance)
                article['combined_score'] = (
                    article.get('credibility', 5.0) * 0.7 + 
                    article['relevance_score'] * 3.0
                )
                
                seen_titles.add(title)
                unique_articles.append(article)
        
        # Sort by combined score (credibility + relevance)
        unique_articles.sort(key=lambda x: x.get('combined_score', 0), reverse=True)
        return unique_articles
    
    def _calculate_relevance_score(self, article: Dict, query: str) -> float:
        """Calculate relevance score for an article"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        query_lower = query.lower()
        
        score = 0.0
        
        # Exact query match in title (highest weight)
        if query_lower in title:
            score += 3.0
        
        # Exact query match in description
        if query_lower in description:
            score += 2.0
        
        # Individual word matches
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 2:  # Skip very short words
                if word in title:
                    score += 1.5
                if word in description:
                    score += 1.0
        
        # Normalize score (0-10 scale)
        max_possible_score = 3.0 + 2.0 + len(query_words) * 2.5
        normalized_score = min(10.0, (score / max_possible_score) * 10.0) if max_possible_score > 0 else 0.0
        
        return normalized_score
    
    def get_sources_info(self) -> Dict[str, Any]:
        """Get enhanced information about available sources"""
        working_sources = [s for s in self.sources if s.get('status') == 'working']
        backup_sources = [s for s in self.sources if s.get('status') in ['backup', 'quota_limited', 'auth_issue']]
        
        working_apis = sum(1 for key, value in self.api_keys.items() if value and key in ['newsapi', 'newsdata', 'mediastack', 'thenewsapi', 'worldnews'])
        
        return {
            'total_sources': len(self.sources),
            'working_sources': len(working_sources),
            'backup_sources': len(backup_sources),
            'working_apis': working_apis,
            'sources_by_type': {
                'working_rss': len([s for s in working_sources if s['type'] == 'rss']),
                'working_api': len([s for s in working_sources if s['type'] == 'api']),
                'backup_rss': len([s for s in backup_sources if s['type'] == 'rss']),
                'backup_api': len([s for s in backup_sources if s['type'] == 'api'])
            },
            'average_credibility': sum(s['credibility'] for s in working_sources) / len(working_sources) if working_sources else 0,
            'top_working_sources': sorted(working_sources, key=lambda x: x['credibility'], reverse=True)[:10]
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Enhanced health status with detailed metrics"""
        working_apis = sum(1 for key, value in self.api_keys.items() 
                          if value and key in ['newsapi', 'newsdata', 'mediastack', 'thenewsapi', 'worldnews'])
        working_rss = len([s for s in self.sources if s.get('status') == 'working' and s['type'] == 'rss'])
        
        total_working = working_apis + working_rss
        
        # Determine overall health
        if total_working >= 10:
            health_status = 'excellent'
        elif total_working >= 7:
            health_status = 'healthy'
        elif total_working >= 4:
            health_status = 'degraded'
        else:
            health_status = 'critical'
        
        return {
            'status': health_status,
            'working_apis': working_apis,
            'working_rss_feeds': working_rss,
            'total_working_sources': total_working,
            'quota_limited_apis': sum(1 for s in self.sources if s.get('status') == 'quota_limited'),
            'backup_sources_available': len([s for s in self.sources if s.get('status') == 'backup']),
            'last_check': datetime.now().isoformat(),
            'recommendations': self._get_health_recommendations(total_working)
        }
    
    def _get_health_recommendations(self, working_count: int) -> List[str]:
        """Get health recommendations based on working sources count"""
        recommendations = []
        
        if working_count >= 10:
            recommendations.append("✅ System is in excellent health with redundant sources")
        elif working_count >= 7:
            recommendations.append("✅ System is healthy with sufficient source diversity")
        elif working_count >= 4:
            recommendations.append("⚠️ System is functional but could benefit from more sources")
            recommendations.append("💡 Consider checking API quotas or adding backup RSS feeds")
        else:
            recommendations.append("🚨 System needs immediate attention - insufficient working sources")
            recommendations.append("🔧 Check API keys and network connectivity")
            recommendations.append("📞 Consider upgrading API plans or adding more RSS sources")
        
        # API-specific recommendations
        if not self.api_keys.get('newsapi'):
            recommendations.append("🔑 Add NewsAPI key for more comprehensive coverage")
        if not self.api_keys.get('newsdata'):
            recommendations.append("🔑 Add NewsData.io key for additional source diversity")
        
        return recommendations
    
    def test_source_connectivity(self) -> Dict[str, Any]:
        """Test connectivity to all sources"""
        results = {}
        
        # Test working API sources
        api_tests = [
            ('newsapi', self._test_newsapi_connectivity),
            ('newsdata', self._test_newsdata_connectivity),
            ('mediastack', self._test_mediastack_connectivity),
            ('thenewsapi', self._test_thenewsapi_connectivity),
            ('worldnews', self._test_worldnews_connectivity)
        ]
        
        for api_name, test_func in api_tests:
            if self.api_keys.get(api_name):
                results[api_name] = test_func()
            else:
                results[api_name] = {'status': 'no_key', 'message': 'API key not configured'}
        
        # Test sample RSS sources
        working_rss = [s for s in self.sources if s.get('status') == 'working' and s['type'] == 'rss'][:5]
        for source in working_rss:
            results[f"rss_{source['name']}"] = self._test_rss_connectivity(source)
        
        return results
    
    def _test_newsapi_connectivity(self) -> Dict[str, Any]:
        """Test NewsAPI connectivity"""
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {'apiKey': self.api_keys['newsapi'], 'country': 'us', 'pageSize': 1}
            response = requests.get(url, params=params, timeout=10, headers=self.headers)
            
            if response.status_code == 200:
                return {'status': 'connected', 'response_time': response.elapsed.total_seconds()}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _test_newsdata_connectivity(self) -> Dict[str, Any]:
        """Test NewsData.io connectivity"""
        try:
            url = "https://newsdata.io/api/1/news"
            params = {'apikey': self.api_keys['newsdata'], 'country': 'us', 'size': 1}
            response = requests.get(url, params=params, timeout=10, headers=self.headers)
            
            if response.status_code == 200:
                return {'status': 'connected', 'response_time': response.elapsed.total_seconds()}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _test_mediastack_connectivity(self) -> Dict[str, Any]:
        """Test MediaStack connectivity"""
        try:
            url = "http://api.mediastack.com/v1/news"
            params = {'access_key': self.api_keys['mediastack'], 'countries': 'us', 'limit': 1}
            response = requests.get(url, params=params, timeout=10, headers=self.headers)
            
            if response.status_code == 200:
                return {'status': 'connected', 'response_time': response.elapsed.total_seconds()}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _test_thenewsapi_connectivity(self) -> Dict[str, Any]:
        """Test The News API connectivity"""
        try:
            url = "https://api.thenewsapi.com/v1/news/all"
            params = {'api_token': self.api_keys['thenewsapi'], 'limit': 1}
            response = requests.get(url, params=params, timeout=10, headers=self.headers)
            
            if response.status_code == 200:
                return {'status': 'connected', 'response_time': response.elapsed.total_seconds()}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _test_worldnews_connectivity(self) -> Dict[str, Any]:
        """Test World News API connectivity"""
        try:
            url = "https://api.worldnewsapi.com/search-news"
            params = {'api-key': self.api_keys['worldnews'], 'text': 'news', 'number': 1}
            response = requests.get(url, params=params, timeout=10, headers=self.headers)
            
            if response.status_code == 200:
                return {'status': 'connected', 'response_time': response.elapsed.total_seconds()}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _test_rss_connectivity(self, source: Dict) -> Dict[str, Any]:
        """Test RSS feed connectivity"""
        try:
            start_time = time.time()
            feed = feedparser.parse(source['url'])
            response_time = time.time() - start_time
            
            if hasattr(feed, 'entries') and len(feed.entries) > 0:
                return {
                    'status': 'connected', 
                    'response_time': response_time,
                    'articles_count': len(feed.entries)
                }
            else:
                return {'status': 'error', 'message': 'No articles found or feed unavailable'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}