from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO


# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()




def create_app():
    # Initialize Flask application
    app = Flask(__name__)
    
    # Configure the SQLAlchemy database URI
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Replace 'your_database.db' as needed
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy and SocketIO with the app
    db.init_app(app)
    socketio.init_app(app)
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()  # Use only when necessary, e.g., in development
    
    # Register blueprints (if any)
    # from .your_blueprint import your_blueprint
    # app.register_blueprint(your_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    # Run app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000)
