from flask import Flask, render_template
from config import Config
from flask_cors import CORS
from extensions import db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    
    with app.app_context():
        # Import models here to ensure they are registered with SQLAlchemy
        from models.user_model import User
        from models.food_model import Food
        from models.bill_model import Bill
        from models.settings_model import Setting
        
        db.create_all()
        
        # Seed default admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin')
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            
            # Seed default food and settings for the admin user
            #from database.db import seed_data
            #seed_data(admin_user.id)

            # Seed menu only if Food table is empty
            if Food.query.count() == 0:
               from database.db import seed_data
               seed_data(admin_user.id)

    # Register Blueprints
    from routes.bill_routes import bill_bp
    from routes.report_routes import report_bp
    from routes.settings_routes import settings_bp
    from routes.auth_routes import auth_bp
    
    app.register_blueprint(bill_bp, url_prefix='/api/bills')
    app.register_blueprint(report_bp, url_prefix='/api/reports')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    @app.before_request
    def require_login():
        from flask import request, redirect, url_for, session, jsonify
        # Allowed routes that don't need login
        allowed_routes = ['login', 'static', 'landing']
        if request.endpoint in allowed_routes or request.path.startswith('/static/') or request.path.startswith('/api/auth/'):
            return
        
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            return redirect(url_for('login'))

    @app.route('/')
    def landing():
        return render_template('landing.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/billing')
    def billing():
        return render_template('billing.html')

    @app.route('/history')
    def history():
        return render_template('history.html')

    @app.route('/reports')
    def reports():
        return render_template('reports.html')

    @app.route('/settings')
    def settings():
        return render_template('settings.html')

    @app.route('/login')
    def login():
        return render_template('login.html')

    return app



if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
