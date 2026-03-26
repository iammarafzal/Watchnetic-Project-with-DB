from flask import Flask
from .extensions import db
import os

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)

    if config_name == 'production':
        app.config['DEBUG'] = False
    else:
        app.config['DEBUG'] = True

    # Set secret key    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///watchnetic.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints for admin
    from .admin.products import admin_products
    from .admin.orders import admin_orders
    from .admin.customers import admin_customers
    from .admin.dashboard import admin_dashboard
    from .admin.auth import admin_auth

    app.register_blueprint(admin_products)
    app.register_blueprint(admin_orders)
    app.register_blueprint(admin_customers)
    app.register_blueprint(admin_dashboard)
    app.register_blueprint(admin_auth)

    # Register main app blueprints
    from .main.routes import main as main_bp
    from .shop.routes import shop as shop_bp
    from .customer.routes import customer as customer_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(customer_bp)

    return app
