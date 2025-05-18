import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from models import db, Product, Customer, Orders, Admin, Order_Detail, Review, Payment, Shipping, init_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import text

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Configure app
config_name = os.environ.get('FLASK_ENV', 'development')
if config_name == 'production':
    app.config['DEBUG'] = False
else:
    app.config['DEBUG'] = True

# Set secret key    
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development')

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql://root@localhost/watchnetic_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

# Register blueprints for admin
from admin.products import admin_products
from admin.orders import admin_orders
from admin.customers import admin_customers
from admin.dashboard import admin_dashboard
from admin.auth import admin_auth

app.register_blueprint(admin_products)
app.register_blueprint(admin_orders)
app.register_blueprint(admin_customers)
app.register_blueprint(admin_dashboard)
app.register_blueprint(admin_auth)

# Basic routes
@app.route('/')
def index():
    latest_products = Product.query.order_by(Product.product_id.desc()).limit(6).all()
    return render_template('index.html', latest_products=latest_products)

@app.route('/watches')
def watches():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    products_pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('watches.html', products=products_pagination.items, pagination=products_pagination)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(Product.product_id != product_id).limit(3).all()
    
    # Get reviews for this product
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.review_date.desc()).all()
    
    # Calculate average rating
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    return render_template('product_detail.html', product=product, related_products=related_products, 
                          reviews=reviews, avg_rating=avg_rating)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blogs')
def blogs():
    # Here you would typically fetch blog posts from a database
    # For now, we'll just render the template
    return render_template('blogs.html')

@app.route('/blog/<slug>')
def blog_post(slug):
    # Here you would usually fetch the blog post from a database
    # Just render a hard-coded template for now
    template_path = f'blog_posts/{slug}.html'
    try:
        return render_template(template_path)
    except:
        return render_template('blog_post_404.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # In a real application, you would save this to a database
        # and/or send an email notification
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html')
    
    # Search for products containing the query in name or description
    products = Product.query.filter(
        (Product.name.like(f'%{query}%')) | 
        (Product.description.like(f'%{query}%'))
    ).all()
    
    return render_template('search.html', products=products, query=query)

@app.route('/subscribe-newsletter', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email')
    if email:
        # In a real application, you would save this to a database
        # For now, just acknowledge with a flash message
        flash('Thank you for subscribing to our newsletter!', 'success')
    return redirect(request.referrer or url_for('index'))

@app.route('/customer/login', methods=['GET', 'POST'])

def customer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validate input
        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return render_template('customer/login.html')
        
        # Check if customer exists
        customer = Customer.query.filter_by(email=email).first()
        
        # Verify password if customer exists
        if customer and check_password_hash(customer.password, password):
            # Set up session
            session['customer_id'] = customer.customer_id
            session['customer_name'] = customer.name
            
            flash('Login successful!', 'success')
            
            # Redirect to intended page or default to profile
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('customer_profile'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('customer/login.html')

@app.route('/customer/profile')
def customer_profile():
    if 'customer_id' not in session:
        flash('Please login to view your profile', 'warning')
        return redirect(url_for('customer_login'))
    
    customer_id = session['customer_id']
    customer = Customer.query.get(customer_id)
    orders = Orders.query.filter_by(customer_id=customer_id).order_by(Orders.order_date.desc()).all()
    
    # Fetch customer reviews
    reviews = Review.query.filter_by(customer_id=customer_id).order_by(Review.review_date.desc()).all()
    
    # Get count of reviews per order for displaying badges
    order_review_counts = {}
    for order in orders:
        count = Review.query.filter_by(customer_id=customer_id, order_id=order.order_id).count()
        if count > 0:
            order_review_counts[order.order_id] = count
    
    return render_template('customer/profile.html', customer=customer, orders=orders, 
                          reviews=reviews, order_review_counts=order_review_counts)

@app.route('/customer/logout')
def customer_logout():
    # Remove customer data from session
    if 'customer_id' in session:
        session.pop('customer_id', None)
    if 'customer_name' in session:
        session.pop('customer_name', None)
    
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        # Check if email already exists
        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('customer_login'))
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Create new customer
        new_customer = Customer(
            name=name,
            email=email,
            password=hashed_password,
            phone=phone
        )
        
        try:
            db.session.add(new_customer)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('customer_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('customer/register.html')

@app.route('/cart')
def view_cart():
    cart_items = []
    total = 0
    
    if 'cart' in session and session['cart']['items']:
        # Get product details for each item in the cart
        for item_id, item_data in session['cart']['items'].items():
            product_id = item_data['id']
            product = Product.query.get(product_id)
            
            if product:
                item = {
                    'product_id': product_id,
                    'name': product.name,
                    'price': float(product.price),
                    'image_url': product.image_url,
                    'quantity': item_data['quantity'],
                    'item_total': float(product.price) * item_data['quantity']
                }
                cart_items.append(item)
                total += item['item_total']
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'customer_id' not in session:
        flash('Please login to checkout', 'warning')
        return redirect(url_for('customer_login'))
    
    if 'cart' not in session or not session['cart']['items']:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('watches'))
    
    customer_id = session['customer_id']
    customer = Customer.query.get(customer_id)
    
    cart_items = []
    total = 0
    
    # Get product details for each item in the cart
    for item_id, item_data in session['cart']['items'].items():
        product_id = item_data['id']
        product = Product.query.get(product_id)
        
        if product:
            item = {
                'product_id': product_id,
                'name': product.name,
                'price': float(product.price),
                'quantity': item_data['quantity'],
                'item_total': float(product.price) * item_data['quantity']
            }
            cart_items.append(item)
            total += item['item_total']
    
    if request.method == 'POST':
        # Process the checkout form
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state', '')
        country = request.form.get('country')
        postal_code = request.form.get('postal_code')
        phone = request.form.get('phone')
        
        # Create a new order
        order = Orders(
            customer_id=customer_id,
            order_date=datetime.now(),
            total_amount=total,
            status='Pending'
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        # Create order details
        for item in cart_items:
            order_detail = Order_Detail(
                order_id=order.order_id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['price']
            )
            db.session.add(order_detail)
        
        # Create shipping record
        shipping = Shipping(
            order_id=order.order_id,
            address=address,
            city=city,
            state=state,
            country=country,
            postal_code=postal_code,
            phone=phone,
            status='Processing'
        )
        db.session.add(shipping)
        
        try:
            db.session.commit()
            # Clear the cart
            session['cart'] = {'items': {}, 'count': 0, 'total': 0}
            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_confirmation'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('checkout.html', customer=customer, cart_items=cart_items, total=total)

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Process payment 
        return redirect(url_for('order_confirmation'))
    return render_template('payment.html')

@app.route('/order-confirmation')
def order_confirmation():
    # This is a simple confirmation page shown after an order is placed
    return render_template('order_confirmation.html')

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    # Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {'items': {}, 'count': 0, 'total': 0}
    
    # Add item to cart or update quantity if already in cart
    cart = session['cart']
    product_id_str = str(product_id)  # Convert to string for session storage
    
    if product_id_str in cart['items']:
        cart['items'][product_id_str]['quantity'] += quantity
    else:
        cart['items'][product_id_str] = {
            'id': product_id,
            'name': product.name,
            'price': float(product.price),
            'image_url': product.image_url,
            'quantity': quantity,
            'product_id': product.product_id
        }
    
    # Update cart count and total
    cart['count'] = sum(item['quantity'] for item in cart['items'].values())
    cart['total'] = sum(item['price'] * item['quantity'] for item in cart['items'].values())
    
    # Save updated cart back to session
    session['cart'] = cart
    
    flash('Product added to cart successfully!', 'success')
    return redirect(url_for('watches'))

@app.route('/update-cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    if 'cart' not in session:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('view_cart'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        return redirect(url_for('remove_from_cart', product_id=product_id))
    
    # Update cart item quantity
    cart = session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart['items']:
        cart['items'][product_id_str]['quantity'] = quantity
        
        # Update cart count and total
        cart['count'] = sum(item['quantity'] for item in cart['items'].values())
        cart['total'] = sum(item['price'] * item['quantity'] for item in cart['items'].values())
        
        # Save updated cart back to session
        session['cart'] = cart
        
        flash('Cart updated successfully!', 'success')
    
    return redirect(url_for('view_cart'))

@app.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' not in session:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('view_cart'))
    
    # Remove item from cart
    cart = session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart['items']:
        del cart['items'][product_id_str]
        
        # Update cart count and total
        cart['count'] = sum(item['quantity'] for item in cart['items'].values())
        cart['total'] = sum(item['price'] * item['quantity'] for item in cart['items'].values())
        
        # Save updated cart back to session
        session['cart'] = cart
        
        flash('Item removed from cart successfully!', 'success')
    
    return redirect(url_for('view_cart'))

@app.route('/clear-cart')
def clear_cart():
    if 'cart' in session:
        session['cart'] = {'items': {}, 'count': 0, 'total': 0}
        flash('Cart cleared successfully!', 'success')
    
    return redirect(url_for('view_cart'))

@app.route('/order_detail/<int:order_id>')
def order_detail(order_id):
    if 'customer_id' not in session:
        flash('Please login to view order details', 'warning')
        return redirect(url_for('customer_login'))
    
    customer_id = session['customer_id']
    order = Orders.query.get(order_id)
    
    # Check if order exists and belongs to the customer
    if not order or order.customer_id != customer_id:
        flash('Order not found or you do not have permission to view it', 'danger')
        return redirect(url_for('customer_profile'))
    
    # Get order details with product information
    order_details_query = db.session.execute(
        text("""
        SELECT od.order_detail_id, od.order_id, od.product_id, od.quantity, od.price,
               (od.quantity * od.price) as subtotal, p.name, p.image_url
        FROM `Order_Detail` od
        JOIN `Product` p ON od.product_id = p.product_id
        WHERE od.order_id = :order_id
        """),
        {"order_id": order_id}
    )
    
    order_details = []
    for item in order_details_query:
        order_details.append({
            'order_detail_id': item.order_detail_id,
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': float(item.price),
            'subtotal': float(item.subtotal),
            'name': item.name,
            'image_url': item.image_url
        })
    
    # Get customer information
    customer = Customer.query.get(customer_id)
    
    # Get shipping information - using raw SQL to avoid the tracking_number column issue
    shipping_query = db.session.execute(
        text("""
        SELECT shipping_id, order_id, shipping_address, shipping_method, shipping_date, status
        FROM shipping
        WHERE order_id = :order_id
        LIMIT 1
        """),
        {"order_id": order_id}
    ).fetchone()
    
    shipping = None
    if shipping_query:
        shipping = {
            'shipping_id': shipping_query.shipping_id,
            'order_id': shipping_query.order_id,
            'shipping_address': shipping_query.shipping_address,
            'shipping_method': shipping_query.shipping_method,
            'shipping_date': shipping_query.shipping_date,
            'status': shipping_query.status,
            'tracking_number': None  # Set to None since the column doesn't exist
        }
    
    # Get payment information
    payment = Payment.query.filter_by(order_id=order_id).first()
    
    # Check if the customer has already reviewed products in this order
    reviews = {}
    for item in order_details:
        review = Review.query.filter_by(
            customer_id=customer_id, 
            product_id=item['product_id'],
            order_id=order_id
        ).first()
        
        if review:
            reviews[item['product_id']] = review
    
    return render_template('customer/order_detail.html', 
                          order=order, 
                          order_details=order_details,
                          customer=customer,
                          shipping=shipping,
                          payment=payment,
                          reviews=reviews)

@app.route('/write-review/<int:order_id>/<int:product_id>', methods=['GET', 'POST'])
def write_review(order_id, product_id):
    """
    Placeholder route for the review functionality.
    This will be implemented in the future.
    """
    if 'customer_id' not in session:
        flash('Please login to write reviews', 'warning')
        return redirect(url_for('customer_login'))
    
    # For now, just redirect back to the order detail page
    flash('Review feature coming soon!', 'info')
    return redirect(url_for('order_detail', order_id=order_id))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    logger.info("Starting Watchnetic application...")
    app.run(host='0.0.0.0', port=5000)
