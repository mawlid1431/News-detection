import os
import logging
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class AISummarizer:
    """AI-powered news summarization with fallback methods"""
    
    def __init__(self):
        self.max_summary_length = int(os.getenv('MAX_SUMMARY_LENGTH', 200))
        self.min_summary_length = int(os.getenv('MIN_SUMMARY_LENGTH', 50))
    
    def summarize_articles(self, articles: List[Dict], query: str) -> Dict[str, Any]:
        """Summarize multiple articles about a topic"""
        if not articles:
            return {
                'summary': f"Sorry, not found. Please verify the source where you found this information about '{query}'.",
                'confidence': 0.0,
                'sources_count': 0,
                'official_links': []
            }
        
        try:
            # Extract and clean article content
            combined_content = self._extract_content(articles)
            
            # Generate summary
            summary = self._generate_summary(combined_content, query)
            
            # Get official links
            official_links = self._get_official_links(articles)
            
            return {
                'summary': summary,
                'confidence': 0.85,
                'sources_count': len(articles),
                'official_links': official_links,
                'method': 'extractive'
            }
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return {
                'summary': f"Found {len(articles)} related articles about '{query}'. Click the links below to read more from official sources.",
                'confidence': 0.6,
                'sources_count': len(articles),
                'official_links': self._get_official_links(articles),
                'method': 'fallback'
            }
    
    def _extract_content(self, articles: List[Dict]) -> str:
        """Extract and combine content from articles"""
        combined_text = []
        
        for article in articles[:3]:  # Limit to top 3 articles
            # Use description/summary if available
            content = article.get('description', '') or article.get('summary', '')
            
            # If no description, try to extract from URL
            if not content and article.get('url'):
                content = self._extract_from_url(article['url'])
            
            if content:
                # Clean and add content
                cleaned = self._clean_text(content)
                if len(cleaned) > 50:  # Only add substantial content
                    combined_text.append(cleaned)
        
        return ' '.join(combined_text)
    
    def _extract_from_url(self, url: str) -> str:
        """Extract content from article URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
                element.decompose()
            
            # Try to find main content
            content_selectors = [
                'article', '.article-content', '.post-content', 
                '.entry-content', 'main', '.content'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    break
            
            if not content:
                # Fallback to paragraphs
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs[:5]])
            
            return content[:1000]  # Limit content length
            
        except Exception as e:
            logger.warning(f"Failed to extract from URL {url}: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove extra punctuation
        text = re.sub(r'[^\w\s.,!?;:]', '', text)
        
        return text.strip()
    
    def _generate_summary(self, content: str, query: str) -> str:
        """Generate extractive summary"""
        if not content:
            return f"Sorry, not found. Please verify the source where you found this information about '{query}'."
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return f"Limited information found about '{query}'. Please check the official sources below for more details."
        
        # Score sentences based on query relevance
        scored_sentences = []
        query_words = set(query.lower().split())
        
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            # Calculate overlap with query
            overlap = len(query_words.intersection(sentence_words))
            # Prefer sentences with more query words and reasonable length
            score = overlap * (1 + len(sentence) / 100)
            scored_sentences.append((sentence, score))
        
        # Sort by score and select top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Build summary
        summary_sentences = []
        total_length = 0
        
        for sentence, score in scored_sentences:
            if total_length + len(sentence) <= self.max_summary_length:
                summary_sentences.append(sentence)
                total_length += len(sentence)
            
            if len(summary_sentences) >= 3 or total_length >= self.min_summary_length:
                break
        
        if summary_sentences:
            summary = '. '.join(summary_sentences)
            if not summary.endswith('.'):
                summary += '.'
            return summary
        else:
            return f"Found information about '{query}'. Check the official sources below for detailed coverage."
    
    def _get_official_links(self, articles: List[Dict]) -> List[Dict]:
        """Extract official links with metadata"""
        official_links = []
        
        for article in articles[:5]:  # Limit to top 5
            if article.get('url'):
                link_info = {
                    'url': article['url'],
                    'title': article.get('title', 'Read More'),
                    'source': article.get('source', 'News Source'),
                    'published_at': article.get('published_at', ''),
                    'credibility': article.get('credibility', 7.0)
                }
                official_links.append(link_info)
        
        return official_links
    
    def generate_not_found_message(self, query: str) -> Dict[str, Any]:
        """Generate message when no articles are found"""
        return {
            'summary': f"Sorry, not found. Please verify the source where you found this information about '{query}'. We couldn't locate this news in our trusted sources database.",
            'confidence': 0.0,
            'sources_count': 0,
            'official_links': [],
            'method': 'not_found',
            'suggestion': "Try rephrasing your query or check if this information comes from a reliable news source."
        }