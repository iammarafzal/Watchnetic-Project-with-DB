from app import create_app
from flask import current_app
from app.extensions import db
from app.models import Admin, Product, Customer, Orders, Order_Detail, Review, Payment, Shipping
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
from db_migrations import run_migrations
import requests
from PIL import Image, ImageDraw
from io import BytesIO

# Load environment variables
load_dotenv()

# Create Flask app
app = create_app()

# Configure database
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///watchnetic.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
# db.init_app(app)

def setup_database():
    """Initialize database and create tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        print("Database setup complete!")

def create_admin_user():
    """Create admin user if it doesn't exist"""
    with app.app_context():
        print("Checking if admin user exists...")
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            print("Creating admin user...")
            admin = Admin(
                username='admin',
                email='admin@watchnetic.com'
            )
            admin.set_password('admin@123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists.")

def create_payment_icons():
    """Create payment method icons for the footer"""
    print("Creating payment icons...")
    
    # Create directory if it doesn't exist
    static_image_path = "static/images"
    if not os.path.exists(static_image_path):
        os.makedirs(static_image_path)
    
    # Final image dimensions
    width = 240
    height = 24
    spacing = 10  # Space between icons
    
    # Create a transparent base image
    payment_methods = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(payment_methods)
    
    # Function to download and resize an icon
    def add_payment_icon(url, position):
        try:
            response = requests.get(url)
            icon = Image.open(BytesIO(response.content))
            
            # Resize proportionally to height 24px
            aspect_ratio = icon.width / icon.height
            new_width = int(height * aspect_ratio)
            icon = icon.resize((new_width, height), Image.LANCZOS)
            
            # Add to main image
            payment_methods.paste(icon, (position, 0), icon if icon.mode == 'RGBA' else None)
            
            return position + new_width + spacing
        except Exception as e:
            print(f"Error adding icon: {e}")
            return position
    
    # Add payment icons - using example URLs of common payment methods
    icons = [
        "https://cdn-icons-png.flaticon.com/512/5968/5968299.png",  # Visa
        "https://cdn-icons-png.flaticon.com/512/5968/5968144.png",  # Mastercard
        "https://cdn-icons-png.flaticon.com/512/5968/5968251.png",  # PayPal
        "https://cdn-icons-png.flaticon.com/512/5968/5968155.png",  # JazzCash
    ]
    
    position = 0
    for icon_url in icons:
        position = add_payment_icon(icon_url, position)
    
    # Save the final image
    payment_methods.save(f"{static_image_path}/payment-methods.png")
    
    print(f"Payment methods image created at {static_image_path}/payment-methods.png")

def create_sample_data():
    """Create sample data for the application"""
    with app.app_context():
        # Check if we already have products
        if Product.query.count() > 0:
            print("Sample data already exists, skipping creation.")
            return
        
        print("Creating sample data...")
        
        # Create sample products
        watch_categories = ["Luxury", "Sports", "Casual", "Smart", "Vintage"]
        sample_watches = [
            {
                "name": "Royal Oak Chronograph",
                "description": "Luxury timepiece with elegant design and precision movement.",
                "price": 1299.99,
                "stock": 10,
                "image_url": "/static/images/products/watch1.jpg",
                "category": "Luxury"
            },
            {
                "name": "Speedmaster Professional",
                "description": "The first watch worn on the moon, with chronograph functionality.",
                "price": 899.99,
                "stock": 15,
                "image_url": "/static/images/products/watch2.jpg",
                "category": "Sports"
            },
            {
                "name": "Submariner Diver",
                "description": "Water-resistant diver's watch with rotating bezel.",
                "price": 1099.99,
                "stock": 8,
                "image_url": "/static/images/products/watch3.jpg",
                "category": "Sports"
            },
            {
                "name": "Classic Fusion",
                "description": "Elegant fusion of traditional watchmaking and modern design.",
                "price": 799.99,
                "stock": 12,
                "image_url": "/static/images/products/watch4.jpg",
                "category": "Casual"
            },
            {
                "name": "Smart Pro 5",
                "description": "Advanced smartwatch with fitness tracking and notification features.",
                "price": 349.99,
                "stock": 20,
                "image_url": "/static/images/products/watch5.jpg",
                "category": "Smart"
            },
            {
                "name": "Vintage 1965",
                "description": "Classic timepiece inspired by 1960s design.",
                "price": 599.99,
                "stock": 5,
                "image_url": "/static/images/products/watch6.jpg",
                "category": "Vintage"
            }
        ]
        
        for watch_data in sample_watches:
            product = Product(**watch_data)
            db.session.add(product)
        
        # Create sample customers
        sample_customers = [
            {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "password": generate_password_hash("password123")
            },
            {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "987-654-3210",
                "password": generate_password_hash("password123")
            }
        ]
        
        for customer_data in sample_customers:
            customer = Customer(**customer_data)
            db.session.add(customer)
        
        # Commit to get IDs
        db.session.commit()
        
        # Create sample orders
        customers = Customer.query.all()
        products = Product.query.all()
        
        for customer in customers:
            # Create 1-3 orders for each customer
            for _ in range(random.randint(1, 3)):
                # Order date within the last 30 days
                order_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
                
                # Select random status
                status = random.choice(["Pending", "Processing", "Shipped", "Delivered"])
                
                # Create order
                order = Orders(
                    customer_id=customer.customer_id,
                    order_date=order_date,
                    status=status,
                    total_amount=0  # Will calculate later
                )
                db.session.add(order)
                db.session.flush()  # To get the order ID
                
                # Add 1-3 products to the order
                total_amount = 0
                for _ in range(random.randint(1, 3)):
                    product = random.choice(products)
                    quantity = random.randint(1, 3)
                    price = float(product.price)
                    subtotal = price * quantity
                    
                    order_detail = Order_Detail(
                        order_id=order.order_id,
                        product_id=product.product_id,
                        quantity=quantity,
                        price=price,
                        subtotal=subtotal
                    )
                    db.session.add(order_detail)
                    
                    total_amount += subtotal
                
                # Update order total
                order.total_amount = total_amount
                order.subtotal = total_amount
                
                # Create payment
                payment = Payment(
                    order_id=order.order_id,
                    customer_id=customer.customer_id,
                    amount=total_amount,
                    payment_method=random.choice(["Credit Card", "PayPal", "Bank Transfer"]),
                    payment_date=order_date,
                    status="Completed"
                )
                db.session.add(payment)
                
                # Create shipping
                shipping = Shipping(
                    order_id=order.order_id,
                    shipping_address=f"{random.randint(100, 999)} Sample St, City, Country",
                    shipping_method=random.choice(["Standard", "Express", "Overnight"]),
                    shipping_date=order_date + timedelta(days=1) if status != "Pending" else None,
                    status=status,
                    tracking_number=f"TRK{random.randint(10000, 99999)}" if status in ["Shipped", "Delivered"] else None
                )
                db.session.add(shipping)
                
                # Add reviews for delivered orders
                if status == "Delivered":
                    for order_detail in Order_Detail.query.filter_by(order_id=order.order_id).all():
                        # 70% chance of leaving a review
                        if random.random() < 0.7:
                            review = Review(
                                customer_id=customer.customer_id,
                                product_id=order_detail.product_id,
                                order_id=order.order_id,
                                rating=random.randint(3, 5),  # Mostly positive reviews
                                comment=f"Great product! Very satisfied with my purchase.",
                                review_date=order_date + timedelta(days=random.randint(5, 15))
                            )
                            db.session.add(review)
        
        # Commit all changes
        db.session.commit()
        print("Sample data created successfully!")

if __name__ == '__main__':
    # Setup database
    setup_database()
    
    # Create admin user
    create_admin_user()
    
    # Create payment icons
    try:
        create_payment_icons()
    except Exception as e:
        print(f"Error creating payment icons: {e}")
    
    # Create sample data (optional)
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--with-sample-data':
        create_sample_data()
    
    print("Setup complete!") 