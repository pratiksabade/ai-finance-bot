import os
from flask import Flask, render_template, send_from_directory, jsonify, session, redirect, url_for
from flask_cors import CORS
from config import Config
from models import db
from routes import (
    auth_bp,
    dashboard_bp,
    income_bp,
    expenses_bp,
    budgets_bp,
    goals_bp,
    ai_bp
)


def create_app(config_class=Config) -> Flask:
    """Application factory for Personal Finance Advisor Bot."""
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Register API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(ai_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    # Web Page Routes
    @app.route('/')
    def index():
        if 'user_id' in session:
            return redirect(url_for('dashboard_view'))
        return render_template('index.html')

    @app.route('/login')
    def login_view():
        if 'user_id' in session:
            return redirect(url_for('dashboard_view'))
        return render_template('login.html')

    @app.route('/register')
    def register_view():
        if 'user_id' in session:
            return redirect(url_for('dashboard_view'))
        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard_view():
        if 'user_id' not in session:
            return redirect(url_for('login_view'))
        return render_template('dashboard.html', user_name=session.get('user_name', 'User'))

    @app.route('/privacy-policy')
    @app.route('/privacy')
    def privacy_view():
        return render_template('privacy.html')

    @app.route('/terms')
    @app.route('/terms-and-conditions')
    def terms_view():
        return render_template('terms.html')

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.svg',
            mimetype='image/svg+xml'
        )

    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'service': 'Personal Finance Advisor Bot',
            'currency': 'INR',
            'version': '1.0.0'
        })

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    print(f"Starting Personal Finance Advisor Bot on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
