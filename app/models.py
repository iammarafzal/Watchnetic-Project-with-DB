from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Admin model
class Admin(db.Model):
    __tablename__ = 'admin'

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


# Customer model
class Customer(db.Model):
    __tablename__ = 'customer'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(255), nullable=False)
    
    # Relationships
    orders = db.relationship('Orders', backref='customer', lazy=True)
    cart = db.relationship('Cart', backref='customer', lazy=True)
    reviews = db.relationship('Review', backref='customer', lazy=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)


# Product model
class Product(db.Model):
    __tablename__ = 'product'

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order_details = db.relationship('Order_Detail', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    cart_items = db.relationship('Cart', backref='product', lazy=True)


# Order model
class Orders(db.Model):
    __tablename__ = 'orders'

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2))
    
    # Relationships
    order_details = db.relationship('Order_Detail', backref='order', lazy=True)
    payments = db.relationship('Payment', backref='order', lazy=True)
    shipping = db.relationship('Shipping', backref='order', lazy=True)

    def __repr__(self):
        return f'<Order {self.order_id}>'


# Order Detail model
class Order_Detail(db.Model):
    __tablename__ = 'order_detail'

    order_detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)


# Payment model
class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)


# Review model
class Review(db.Model):
    __tablename__ = 'review'

    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Check constraint for rating 1 to 5
    comment = db.Column(db.Text)
    review_date = db.Column(db.DateTime, default=datetime.utcnow)


# Cart model
class Cart(db.Model):
    __tablename__ = 'cart'

    cart_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


# Shipping model
class Shipping(db.Model):
    __tablename__ = 'shipping'

    shipping_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    shipping_method = db.Column(db.String(100), nullable=False)
    shipping_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False)
    # Note: This column may not exist in all database instances
    # If getting OperationalError about tracking_number, you may need to add the column:
    # ALTER TABLE shipping ADD COLUMN tracking_number VARCHAR(100)
    tracking_number = db.Column(db.String(100), nullable=True)


# Initialize the database
def init_db(app):
    db.init_app(app)
