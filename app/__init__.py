from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.routes import api

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Register blueprints
    app.register_blueprint(api)
    
    return app 