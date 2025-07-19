from .admin_routes import admin_bp
from .user_routes import user_bp
from .auth import auth_bp

all_blueprints = [admin_bp, user_bp, auth_bp]
