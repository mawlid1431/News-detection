from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Import our modules
from backend.smart_verification import SmartVerificationEngine
from backend.database import init_db, db, Verification

# Initialize Flask app
app = Flask(__name__, 
           template_folder='frontend/templates',
           static_folder='frontend/static')

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trustify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app)
init_db(app)

# Initialize core verification engine
verification_engine = SmartVerificationEngine()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Serve the chatbot UI"""
    return render_template('chatbot_ui.html')

@app.route('/old')
def old_index():
    """Serve the old main page"""
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    """Serve the chatbot page"""
    return render_template('chatbot.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {
            'verification_engine': 'active',
            'database': 'connected'
        }
    })

@app.route('/api/verify', methods=['POST'])
def verify_news():
    """Core verification endpoint - simple and direct"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        logger.info(f"Verifying query: {query}")
        
        # Core verification logic
        result = verification_engine.verify(query)
        
        # Save to database
        try:
            verification = Verification(
                query=query,
                status=result.get('status', 'unknown'),
                credibility_score=result.get('credibility_score', 0.0),
                confidence=result.get('confidence', 'low'),
                explanation=result.get('explanation', ''),
                sources_count=result.get('sources_found', 0),
                processing_time_ms=result.get('processing_time_ms', 0)
            )
            db.session.add(verification)
            db.session.commit()
        except Exception as db_error:
            logger.warning(f"Database save failed: {db_error}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return jsonify({
            'error': 'Verification service temporarily unavailable',
            'query': query,
            'status': 'error',
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/sources')
def get_sources():
    """Get available trusted sources"""
    return jsonify({
        'total_sources': 3,
        'active_sources': ['NewsAPI', 'Currents', 'NewsData'],
        'status': 'operational'
    })



@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )