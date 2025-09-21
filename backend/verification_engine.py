import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from fuzzywuzzy import fuzz
from .news_sources import NewsSourceManager
from .ml_models import MLModelManager
from .ai_fact_checker import AIFactChecker

logger = logging.getLogger(__name__)

class VerificationEngine:
    """Core verification engine implementing three-tier classification"""
    
    def __init__(self):
        self.news_manager = NewsSourceManager()
        self.ml_manager = MLModelManager()
        self.ai_fact_checker = AIFactChecker()
        
        # Scoring thresholds
        self.EXACT_MATCH_SCORE = int(os.getenv('EXACT_MATCH_SCORE', 9))
        self.PARTIAL_MATCH_SCORE = int(os.getenv('PARTIAL_MATCH_SCORE', 5))
        self.NO_MATCH_SCORE = int(os.getenv('NO_MATCH_SCORE', 0))
        self.MULTIPLE_SOURCE_BONUS = int(os.getenv('MULTIPLE_SOURCE_BONUS', 1))
        
    def verify(self, query: str) -> Dict[str, Any]:
        """Main verification pipeline"""
        start_time = datetime.utcnow()
        
        try:
            # Step 1: AI Fact Checking (Primary)
            ai_fact_result = self.ai_fact_checker.fact_check(query)
            
            # If AI fact checker determines it's false, return immediately
            if ai_fact_result['status'] == 'false':
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                return {
                    'query': query,
                    'status': 'unverified',
                    'credibility_score': ai_fact_result['credibility_score'],
                    'confidence': 'high',
                    'explanation': ai_fact_result['explanation'],
                    'sources': [],
                    'ai_fact_check': ai_fact_result,
                    'processing_time_ms': round(processing_time),
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Step 2: ML Classification
            ml_result = self.ml_manager.classify_text(query)
            
            # Step 3: News source verification
            news_results = self.news_manager.search_news(query)
            
            # Step 3: Similarity analysis
            similarity_results = self._analyze_similarity(query, news_results)
            
            # Step 4: Calculate credibility score
            credibility_score = self._calculate_credibility(
                ml_result, similarity_results, news_results
            )
            
            # Step 5: Determine final status
            status = self._determine_status(credibility_score, similarity_results)
            
            # Step 6: Generate explanation
            explanation = self._generate_explanation(
                status, credibility_score, similarity_results, ml_result
            )
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return {
                'query': query,
                'status': status,
                'credibility_score': round(credibility_score, 1),
                'confidence': self._get_confidence_level(credibility_score),
                'explanation': explanation,
                'sources': [self._format_source(result) for result in news_results[:5]],
                'ml_analysis': ml_result,
                'ai_fact_check': ai_fact_result,
                'processing_time_ms': round(processing_time),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return {
                'query': query,
                'status': 'error',
                'error': 'Verification service temporarily unavailable',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _analyze_similarity(self, query: str, news_results: List[Dict]) -> List[Dict]:
        """Analyze similarity between query and news articles"""
        similarity_results = []
        
        for article in news_results:
            title_similarity = fuzz.ratio(query.lower(), article['title'].lower()) / 100
            content_similarity = fuzz.partial_ratio(
                query.lower(), article.get('description', '').lower()
            ) / 100
            
            overall_similarity = (title_similarity * 0.7 + content_similarity * 0.3)
            
            similarity_results.append({
                'article': article,
                'title_similarity': title_similarity,
                'content_similarity': content_similarity,
                'overall_similarity': overall_similarity,
                'match_type': self._get_match_type(overall_similarity)
            })
        
        return sorted(similarity_results, key=lambda x: x['overall_similarity'], reverse=True)
    
    def _get_match_type(self, similarity: float) -> str:
        """Determine match type based on similarity score"""
        if similarity >= 0.8:
            return 'exact'
        elif similarity >= 0.6:
            return 'partial'
        else:
            return 'related'
    
    def _calculate_credibility(self, ml_result: Dict, similarity_results: List[Dict], 
                             news_results: List[Dict]) -> float:
        """Calculate overall credibility score"""
        base_score = 5.0
        
        # ML model contribution
        if ml_result and ml_result.get('prediction'):
            if ml_result['prediction'] == 'reliable':
                base_score += ml_result.get('confidence', 0) * 2
            elif ml_result['prediction'] == 'unreliable':
                base_score -= ml_result.get('confidence', 0) * 3
        
        # Similarity contribution
        if similarity_results:
            high_similarity_count = sum(1 for r in similarity_results 
                                      if r['overall_similarity'] > 0.7)
            base_score += high_similarity_count * 0.8
            
            # Source credibility bonus
            avg_credibility = sum(r['article'].get('credibility', 7) 
                                for r in similarity_results) / len(similarity_results)
            base_score += (avg_credibility - 7) * 0.5
        
        # Multiple source bonus
        if len(news_results) >= 3:
            base_score += self.MULTIPLE_SOURCE_BONUS
        
        return max(0, min(10, base_score))
    
    def _determine_status(self, credibility_score: float, similarity_results: List[Dict]) -> str:
        """Determine verification status"""
        if credibility_score >= 8:
            return 'verified'
        elif credibility_score >= 6:
            return 'partially-verified'
        else:
            return 'unverified'
    
    def _generate_explanation(self, status: str, score: float, 
                            similarity_results: List[Dict], ml_result: Dict) -> str:
        """Generate human-readable explanation"""
        explanations = {
            'verified': f"High confidence verification ({score}/10). Found {len(similarity_results)} matching articles from trusted sources.",
            'partially-verified': f"Moderate confidence ({score}/10). Found some supporting evidence but with variations or limited sources.",
            'unverified': f"Low confidence ({score}/10). Limited or no supporting evidence found from trusted sources."
        }
        
        explanation = explanations.get(status, "Unable to determine verification status.")
        
        if ml_result and ml_result.get('prediction'):
            confidence_pct = round(ml_result.get('confidence', 0) * 100)
            explanation += f" ML analysis: {ml_result['prediction']} ({confidence_pct}% confidence)."
        
        return explanation
    
    def _get_confidence_level(self, score: float) -> str:
        """Get confidence level from score"""
        if score >= 8:
            return 'high'
        elif score >= 6:
            return 'medium'
        else:
            return 'low'
    
    def _format_source(self, article: Dict) -> Dict:
        """Format article for API response"""
        return {
            'name': article.get('source', 'Unknown'),
            'title': article.get('title', ''),
            'url': article.get('url', ''),
            'published_at': article.get('published_at', ''),
            'credibility': article.get('credibility', 7.0)
        }