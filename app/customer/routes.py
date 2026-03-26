from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import Customer, Orders, Review, Payment, Order_Detail, Product, Shipping
from sqlalchemy import text
from . import customer

@customer.route('/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please provide both email and password', 'danger')
            return render_template('customer/login.html')
        
        cust = Customer.query.filter_by(email=email).first()
        
        if cust and check_password_hash(cust.password, password):
            session['customer_id'] = cust.customer_id
            session['customer_name'] = cust.name
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            if next_page: return redirect(next_page)
            return redirect(url_for('customer.customer_profile'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('customer/login.html')

@customer.route('/profile')
def customer_profile():
    if 'customer_id' not in session:
        flash('Please login to view your profile', 'warning')
        return redirect(url_for('customer.customer_login'))
    
    customer_id = session['customer_id']
    cust = Customer.query.get(customer_id)
    orders = Orders.query.filter_by(customer_id=customer_id).order_by(Orders.order_date.desc()).all()
    reviews = Review.query.filter_by(customer_id=customer_id).order_by(Review.review_date.desc()).all()
    
    order_review_counts = {}
    for order in orders:
        count = Review.query.filter_by(customer_id=customer_id, order_id=order.order_id).count()
        if count > 0:
            order_review_counts[order.order_id] = count
    
    return render_template('customer/profile.html', customer=cust, orders=orders, 
                          reviews=reviews, order_review_counts=order_review_counts)

@customer.route('/logout')
def customer_logout():
    if 'customer_id' in session: session.pop('customer_id', None)
    if 'customer_name' in session: session.pop('customer_name', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('main.index'))

@customer.route('/register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        existing_customer = Customer.query.filter_by(email=email).first()
        if existing_customer:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('customer.customer_login'))
        
        hashed_password = generate_password_hash(password)
        new_customer = Customer(name=name, email=email, password=hashed_password, phone=phone)
        
        try:
            db.session.add(new_customer)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('customer.customer_login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('customer/register.html')

@customer.route('/order_detail/<int:order_id>')
def order_detail(order_id):
    if 'customer_id' not in session:
        flash('Please login to view order details', 'warning')
        return redirect(url_for('customer.customer_login'))
    
    customer_id = session['customer_id']
    order = Orders.query.get(order_id)
    
    if not order or order.customer_id != customer_id:
        flash('Order not found or you do not have permission to view it', 'danger')
        return redirect(url_for('customer.customer_profile'))
    
    order_details_query = db.session.execute(
        text('''
        SELECT od.order_detail_id, od.order_id, od.product_id, od.quantity, od.price,
               (od.quantity * od.price) as subtotal, p.name, p.image_url
        FROM `Order_Detail` od
        JOIN `Product` p ON od.product_id = p.product_id
        WHERE od.order_id = :order_id
        '''),
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
    
    cust = Customer.query.get(customer_id)
    
    shipping_query = db.session.execute(
        text('''
        SELECT shipping_id, order_id, shipping_address, shipping_method, shipping_date, status
        FROM shipping
        WHERE order_id = :order_id
        LIMIT 1
        '''),
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
            'tracking_number': None
        }
    
    payment = Payment.query.filter_by(order_id=order_id).first()
    
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
                          order=order, order_details=order_details,
                          customer=cust, shipping=shipping, payment=payment, reviews=reviews)

@customer.route('/write-review/<int:order_id>/<int:product_id>', methods=['GET', 'POST'])
def write_review(order_id, product_id):
    if 'customer_id' not in session:
        flash('Please login to write reviews', 'warning')
        return redirect(url_for('customer.customer_login'))
    
    flash('Review feature coming soon!', 'info')
    return redirect(url_for('customer.order_detail', order_id=order_id))
