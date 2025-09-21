#!/usr/bin/env python3
"""URL content extraction and verification"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional

class URLHandler:
    """Handle URL content extraction and verification"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def is_url(self, text: str) -> bool:
        """Check if text is a URL"""
        url_pattern = r'https?://[^\s]+'
        return bool(re.match(url_pattern, text.strip()))
    
    def extract_content(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                element.decompose()
            
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_main_content(soup)
            
            # Extract source domain
            domain = re.findall(r'https?://([^/]+)', url)[0] if url else 'unknown'
            
            return {
                'title': title,
                'content': content,
                'url': url,
                'domain': domain,
                'source': self._get_source_name(domain)
            }
            
        except Exception as e:
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title"""
        # Try different title selectors
        selectors = [
            'h1',
            '.headline',
            '.title',
            '[data-testid="headline"]',
            '.article-title',
            '.post-title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback to page title
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text(strip=True)
        
        return 'Article'
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main article content"""
        # Try different content selectors
        selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '[data-testid="article-content"]',
            '.content',
            'main'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Get text from paragraphs
                paragraphs = element.find_all('p')
                if paragraphs:
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs[:5]])
                    if len(content) > 100:
                        return content
        
        # Fallback to all paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            content = ' '.join([p.get_text(strip=True) for p in paragraphs[:5]])
            return content
        
        return soup.get_text(strip=True)[:500]
    
    def _get_source_name(self, domain: str) -> str:
        """Get readable source name from domain"""
        source_map = {
            'bbc.com': 'BBC News',
            'cnn.com': 'CNN',
            'reuters.com': 'Reuters',
            'apnews.com': 'Associated Press',
            'theguardian.com': 'The Guardian',
            'nytimes.com': 'New York Times',
            'washingtonpost.com': 'Washington Post',
            'wsj.com': 'Wall Street Journal'
        }
        
        for key, value in source_map.items():
            if key in domain:
                return value
        
        return domain.replace('www.', '').title()