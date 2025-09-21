from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)

class User(db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    verifications = db.relationship('Verification', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Verification(db.Model):
    """Verification history model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    query = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # verified, partially-verified, unverified
    credibility_score = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.String(10), nullable=False)  # high, medium, low
    explanation = db.Column(db.Text)
    sources_count = db.Column(db.Integer, default=0)
    processing_time_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'status': self.status,
            'credibility_score': self.credibility_score,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'sources_count': self.sources_count,
            'processing_time_ms': self.processing_time_ms,
            'created_at': self.created_at.isoformat()
        }

class NewsSource(db.Model):
    """News source tracking model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255))
    source_type = db.Column(db.String(20))  # rss, api
    credibility = db.Column(db.Float, default=7.0)
    country = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'source_type': self.source_type,
            'credibility': self.credibility,
            'country': self.country,
            'is_active': self.is_active,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'created_at': self.created_at.isoformat()
        }