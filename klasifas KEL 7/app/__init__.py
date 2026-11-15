from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.config import Config
from datetime import timedelta

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu.'
    login_manager.login_message_category = 'warning'
    
    # Daftarkan Blueprint
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Filter Waktu WIB (UTC+7)
    @app.template_filter('wib')
    def wib_filter(dt):
        if dt is None:
            return ''
        return (dt + timedelta(hours=7)).strftime('%d/%m/%Y %H:%M')
    
    # Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.models import User
    return User.query.get(int(user_id))