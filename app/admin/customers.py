from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import Customer, Orders

# Create the blueprint
admin_customers = Blueprint('admin_customers', __name__, url_prefix='/admin/customers')

@admin_customers.route('/')
def index():
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        customers = Customer.query.all()
    except Exception as e:
        print(f"Database error in admin_customers index: {e}")
        customers = []
    
    return render_template('admin/customers/index.html', customers=customers)

@admin_customers.route('/<int:customer_id>')
def view(customer_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            flash('Customer not found', 'error')
            return redirect(url_for('admin_customers.index'))
            
        orders = Orders.query.filter_by(customer_id=customer_id).order_by(Orders.order_date.desc()).all()
    except Exception as e:
        print(f"Database error in admin_customers view: {e}")
        flash('Error retrieving customer details', 'error')
        return redirect(url_for('admin_customers.index'))
    
    return render_template('admin/customers/view.html', customer=customer, orders=orders)

@admin_customers.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit(customer_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            flash('Customer not found', 'error')
            return redirect(url_for('admin_customers.index'))
        
        if request.method == 'POST':
            customer.name = request.form.get('name')
            customer.email = request.form.get('email')
            customer.phone = request.form.get('phone')
            customer.address = request.form.get('address')
            
            db.session.commit()
            flash('Customer updated successfully', 'success')
            return redirect(url_for('admin_customers.view', customer_id=customer_id))
    except Exception as e:
        db.session.rollback()
        print(f"Database error in admin_customers edit: {e}")
        flash('Error updating customer', 'error')
        return redirect(url_for('admin_customers.index'))
    
    return render_template('admin/customers/edit.html', customer=customer)

@admin_customers.route('/delete/<int:customer_id>')
def delete(customer_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        customer = Customer.query.get(customer_id)
        if customer:
            # Check if customer has orders
            orders_count = Orders.query.filter_by(customer_id=customer_id).count()
            if orders_count > 0:
                flash('Cannot delete customer with existing orders', 'error')
                return redirect(url_for('admin_customers.index'))
            
            db.session.delete(customer)
            db.session.commit()
            flash('Customer deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Database error in admin_customers delete: {e}")
        flash('Error deleting customer', 'error')
    
    return redirect(url_for('admin_customers.index')) 