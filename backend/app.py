import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import Config
from backend.database import init_db
from backend.routes import api
from backend.middleware import logger
from backend.database import db

app = Flask(__name__, instance_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance'))
app.config.from_object(Config)

# ============================================================
# CORS - Enable once, no duplicates
# ============================================================
CORS(app, origins='*', supports_credentials=True, allow_headers=['Content-Type', 'Authorization', 'Accept'], methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Database
db_path = os.path.join(app.instance_path, 'climate.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
os.makedirs(app.instance_path, exist_ok=True)
print(f"📁 Instance folder: {app.instance_path}")

init_db(app)

with app.app_context():
    db.create_all()
    print("✅ Database tables created/verified!")

app.register_blueprint(api)

# ============================================================
# CORS Headers for all responses
# ============================================================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/')
def home():
    return jsonify({
        'name': '🌤️ Climate AI Backend',
        'version': '1.0',
        'status': 'running',
        'database': 'SQLite',
        'endpoints': {
            'health': '/api/health',
            'cities': '/api/cities',
            'predict': '/api/predict',
            'whatif': '/api/whatif',
            'explain_human': '/api/explain_human',
            'climate': '/api/climate',
            'history': '/api/history',
            'alerts': '/api/alerts'
        }
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌤️ CLIMATE AI BACKEND SERVER")
    print("="*60)
    app.run(host='0.0.0.0', port=5001, debug=True)
