from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Product, Orders, Customer

# Create the blueprint
admin_dashboard = Blueprint('admin_dashboard', __name__, url_prefix='/admin/dashboard')

@admin_dashboard.route('/')
def index():
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        # Get counts for dashboard stats
        product_count = Product.query.count()
        order_count = Orders.query.count()
        customer_count = Customer.query.count()
        
        # Get recent orders
        recent_orders = Orders.query.order_by(Orders.order_date.desc()).limit(5).all()
        
        # Get products with low stock
        low_stock_products = Product.query.filter(Product.stock < 5).all()
        
    except Exception as e:
        print(f"Database error in admin dashboard: {e}")
        product_count = 0
        order_count = 0
        customer_count = 0
        recent_orders = []
        low_stock_products = []
    
    return render_template('admin/dashboard.html', 
                          product_count=product_count,
                          order_count=order_count,
                          customer_count=customer_count,
                          recent_orders=recent_orders,
                          low_stock_products=low_stock_products) 