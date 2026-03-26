from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from models import db, Orders, Customer, Product

admin_orders = Blueprint('admin_orders', __name__)

# Route to view all orders
@admin_orders.route('/orders')
def view_orders():
    orders = Orders.query.all()  # Fetch all orders from the database
    return render_template('admin/orders.html', orders=orders)

# Route to create a new order
@admin_orders.route('/orders/create', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        product_id = request.form['product_id']
        quantity = request.form['quantity']

        # Fetch the customer and product details
        customer = Customer.query.get(customer_id)
        product = Product.query.get(product_id)

        if not customer or not product:
            flash("Invalid customer or product", "danger")
            return redirect(url_for('admin_orders.create_order'))

        # Calculate total price
        total_price = product.price * int(quantity)

        # Create new order
        new_order = Orders(  # Use Orders instead of Order
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            total_price=total_price,
            status='Pending'
        )

        # Add the new order to the database
        db.session.add(new_order)
        db.session.commit()

        flash("Order created successfully!", "success")
        return redirect(url_for('admin_orders.view_orders'))

    # If GET request, show the order creation form
    customers = Customer.query.all()
    products = Product.query.all()
    return render_template('admin/create_order.html', customers=customers, products=products)

# Route to update order status
@admin_orders.route('/orders/update/<int:id>', methods=['GET', 'POST'])
def update_order(id):
    order = Orders.query.get(id)  # Use Orders instead of Order
    if not order:
        flash("Order not found!", "danger")
        return redirect(url_for('admin_orders.view_orders'))

    if request.method == 'POST':
        order.status = request.form['status']
        db.session.commit()
        flash("Order status updated!", "success")
        return redirect(url_for('admin_orders.view_orders'))

    return render_template('admin/update_order.html', order=order)

# Route to delete an order
@admin_orders.route('/orders/delete/<int:id>', methods=['POST'])
def delete_order(id):
    order = Orders.query.get(id)  # Use Orders instead of Order
    if not order:
        flash("Order not found!", "danger")
        return redirect(url_for('admin_orders.view_orders'))

    db.session.delete(order)
    db.session.commit()

    flash("Order deleted successfully!", "success")
    return redirect(url_for('admin_orders.view_orders'))
