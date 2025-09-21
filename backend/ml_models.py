import os
import pickle
import logging
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

# ML imports with fallbacks
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC
    from sklearn.pipeline import Pipeline
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
except ImportError as e:
    logging.warning(f"ML dependencies not fully available: {e}")

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logging.warning("Transformers not available")

logger = logging.getLogger(__name__)

class MLModelManager:
    """Manages ML models for fake news detection"""
    
    def __init__(self):
        self.models = {}
        self.vectorizer = None
        self.is_loaded = False
        
        # Download NLTK data if needed
        self._setup_nltk()
        
    def _setup_nltk(self):
        """Setup NLTK dependencies"""
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
        except LookupError:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('wordnet', quiet=True)
            except Exception as e:
                logger.warning(f"NLTK setup failed: {e}")
    
    def load_models(self):
        """Load all ML models"""
        try:
            # Load traditional ML model
            self._load_traditional_model()
            
            # Load transformer model if available
            if TRANSFORMERS_AVAILABLE:
                self._load_transformer_model()
            
            self.is_loaded = True
            logger.info("ML models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")
            # Create fallback models
            self._create_fallback_models()
    
    def _load_traditional_model(self):
        """Load SVM + TF-IDF model"""
        try:
            model_path = os.path.join('models', 'svm_model.pkl')
            vectorizer_path = os.path.join('models', 'tfidf_vectorizer.pkl')
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                with open(model_path, 'rb') as f:
                    self.models['svm'] = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                logger.info("Loaded pre-trained SVM model")
            else:
                # Train a simple model
                self._train_simple_model()
                
        except Exception as e:
            logger.error(f"Traditional model loading failed: {e}")
            self._create_simple_classifier()
    
    def _load_transformer_model(self):
        """Load transformer model for classification"""
        try:
            model_name = os.getenv('HF_MODEL_NAME', 'distilbert-base-uncased')
            
            # Try to load a pre-trained fake news classifier
            self.models['transformer'] = pipeline(
                "text-classification",
                model="hamzab/roberta-fake-news-classification",
                return_all_scores=True
            )
            logger.info("Loaded transformer model")
            
        except Exception as e:
            logger.warning(f"Transformer model loading failed: {e}")
            # Fallback to general sentiment analysis
            try:
                self.models['transformer'] = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
                logger.info("Loaded fallback sentiment model")
            except Exception as e2:
                logger.error(f"Fallback transformer failed: {e2}")
    
    def _train_simple_model(self):
        """Train a simple SVM model with basic features"""
        try:
            # Create simple training data
            fake_samples = [
                "SHOCKING: Scientists don't want you to know this secret!",
                "BREAKING: Miracle cure discovered but hidden by big pharma",
                "You won't believe what happens next in this conspiracy",
                "Secret government documents reveal shocking truth",
                "This one weird trick will change everything"
            ]
            
            real_samples = [
                "According to a new study published in Nature journal",
                "Researchers at Harvard University have found evidence",
                "The World Health Organization announced today",
                "Data from the latest government report shows",
                "Scientists have confirmed through peer review"
            ]
            
            # Prepare training data
            X_train = fake_samples + real_samples
            y_train = [0] * len(fake_samples) + [1] * len(real_samples)  # 0=fake, 1=real
            
            # Create and train pipeline
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            self.models['svm'] = Pipeline([
                ('tfidf', self.vectorizer),
                ('svm', SVC(probability=True, kernel='linear'))
            ])
            
            self.models['svm'].fit(X_train, y_train)
            
            # Save the model
            os.makedirs('models', exist_ok=True)
            with open('models/svm_model.pkl', 'wb') as f:
                pickle.dump(self.models['svm'], f)
            
            logger.info("Trained and saved simple SVM model")
            
        except Exception as e:
            logger.error(f"Simple model training failed: {e}")
            self._create_simple_classifier()
    
    def _create_simple_classifier(self):
        """Create rule-based classifier as fallback"""
        fake_keywords = [
            'shocking', 'secret', 'hidden', 'conspiracy', 'miracle', 
            'unbelievable', 'hoax', 'fake', 'scam', 'lie'
        ]
        
        reliable_keywords = [
            'study', 'research', 'university', 'journal', 'peer-reviewed',
            'according to', 'data shows', 'evidence', 'confirmed'
        ]
        
        self.models['rule_based'] = {
            'fake_keywords': fake_keywords,
            'reliable_keywords': reliable_keywords
        }
        
        logger.info("Created rule-based classifier")
    
    def _create_fallback_models(self):
        """Create minimal fallback models"""
        self._create_simple_classifier()
        self.is_loaded = True
        logger.info("Created fallback models")
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """Classify text using available models"""
        if not self.is_loaded:
            self.load_models()
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'models_used': []
        }
        
        # Try SVM model
        if 'svm' in self.models:
            try:
                svm_result = self._classify_with_svm(text)
                results.update(svm_result)
                results['models_used'].append('svm')
            except Exception as e:
                logger.error(f"SVM classification failed: {e}")
        
        # Try transformer model
        if 'transformer' in self.models:
            try:
                transformer_result = self._classify_with_transformer(text)
                results.update(transformer_result)
                results['models_used'].append('transformer')
            except Exception as e:
                logger.error(f"Transformer classification failed: {e}")
        
        # Fallback to rule-based
        if not results['models_used']:
            rule_result = self._classify_with_rules(text)
            results.update(rule_result)
            results['models_used'].append('rule_based')
        
        return results
    
    def _classify_with_svm(self, text: str) -> Dict[str, Any]:
        """Classify using SVM model"""
        prediction = self.models['svm'].predict([text])[0]
        probabilities = self.models['svm'].predict_proba([text])[0]
        
        return {
            'prediction': 'reliable' if prediction == 1 else 'unreliable',
            'confidence': max(probabilities),
            'svm_scores': {
                'fake_prob': probabilities[0],
                'real_prob': probabilities[1]
            }
        }
    
    def _classify_with_transformer(self, text: str) -> Dict[str, Any]:
        """Classify using transformer model"""
        result = self.models['transformer'](text)
        
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], list):
                # Fake news classifier format
                scores = {item['label']: item['score'] for item in result[0]}
                fake_score = scores.get('FAKE', 0)
                real_score = scores.get('REAL', 0)
                
                prediction = 'reliable' if real_score > fake_score else 'unreliable'
                confidence = max(fake_score, real_score)
            else:
                # Sentiment analysis format
                label = result[0]['label']
                score = result[0]['score']
                
                # Map sentiment to reliability (positive = more reliable)
                prediction = 'reliable' if label == 'POSITIVE' else 'unreliable'
                confidence = score
        else:
            prediction = 'uncertain'
            confidence = 0.5
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'transformer_result': result
        }
    
    def _classify_with_rules(self, text: str) -> Dict[str, Any]:
        """Classify using rule-based approach"""
        text_lower = text.lower()
        
        fake_score = sum(1 for keyword in self.models['rule_based']['fake_keywords'] 
                        if keyword in text_lower)
        reliable_score = sum(1 for keyword in self.models['rule_based']['reliable_keywords'] 
                           if keyword in text_lower)
        
        if reliable_score > fake_score:
            prediction = 'reliable'
            confidence = min(0.8, 0.5 + reliable_score * 0.1)
        elif fake_score > reliable_score:
            prediction = 'unreliable'
            confidence = min(0.8, 0.5 + fake_score * 0.1)
        else:
            prediction = 'uncertain'
            confidence = 0.5
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'rule_scores': {
                'fake_indicators': fake_score,
                'reliable_indicators': reliable_score
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get model status"""
        return {
            'loaded': self.is_loaded,
            'available_models': list(self.models.keys()),
            'transformers_available': TRANSFORMERS_AVAILABLE
        }
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed model information"""
        status = self.get_status()
        
        model_info = {}
        for model_name in self.models.keys():
            if model_name == 'svm':
                model_info[model_name] = {
                    'type': 'Support Vector Machine',
                    'features': 'TF-IDF',
                    'status': 'loaded'
                }
            elif model_name == 'transformer':
                model_info[model_name] = {
                    'type': 'Transformer',
                    'architecture': 'BERT/RoBERTa',
                    'status': 'loaded'
                }
            elif model_name == 'rule_based':
                model_info[model_name] = {
                    'type': 'Rule-based',
                    'features': 'Keyword matching',
                    'status': 'loaded'
                }
        
        status['model_details'] = model_info
        return status