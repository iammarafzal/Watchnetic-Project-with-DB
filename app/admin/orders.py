from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import Orders, Order_Detail, Customer, Product, Payment, Shipping
from sqlalchemy import text

# Create the blueprint
admin_orders = Blueprint('admin_orders', __name__, url_prefix='/admin/orders')

@admin_orders.route('/')
def index():
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    
    try:
        query = Orders.query
        
        # Apply filters if provided
        if status_filter:
            query = query.filter(Orders.status == status_filter)
            
        if search_query:
            # Join with Customer to search by customer name
            query = query.join(Customer).filter(
                db.or_(
                    Orders.order_id.like(f"%{search_query}%"),
                    Customer.name.like(f"%{search_query}%")
                )
            )
        
        # Order by most recent
        query = query.order_by(Orders.order_date.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=10, error_out=False)
        orders = pagination.items
    except Exception as e:
        print(f"Database error in admin_orders index: {e}")
        orders = []
        pagination = None
    
    return render_template('admin/orders/index.html', orders=orders, pagination=pagination)

@admin_orders.route('/<int:order_id>')
def view_order(order_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        order = Orders.query.get(order_id)
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('admin_orders.index'))
            
        # Get order details and manually calculate subtotal
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
                'product_name': item.name,
                'image_url': item.image_url if item.image_url else None
            })
            
        payment = Payment.query.filter_by(order_id=order_id).first()
        
        # Use direct SQL for Shipping to avoid ORM model with tracking_number field
        shipping_query = db.session.execute(
            text("""
            SELECT shipping_id, order_id, shipping_address, shipping_method, 
                   shipping_date, status
            FROM `Shipping`
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
                'status': shipping_query.status
            }
            
        customer = Customer.query.get(order.customer_id)
    except Exception as e:
        db.session.rollback()
        print(f"Database error in admin_orders view_order: {e}")
        import traceback
        traceback.print_exc()
        flash('Error retrieving order details', 'error')
        return redirect(url_for('admin_orders.index'))
    
    return render_template('admin/orders/view.html', 
                           order=order, 
                           order_details=order_details, 
                           payment=payment, 
                           shipping=shipping, 
                           customer=customer)

@admin_orders.route('/<int:order_id>/update_status', methods=['POST'])
def update_status(order_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        order = Orders.query.get(order_id)
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('admin_orders.index'))
        
        new_status = request.form.get('status')
        if new_status:
            order.status = new_status
            db.session.commit()
            flash('Order status updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Database error in admin_orders update_status: {e}")
        flash('Error updating order status', 'error')
    
    return redirect(url_for('admin_orders.view_order', order_id=order_id))

@admin_orders.route('/<int:order_id>/delete')
def delete_order(order_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        order = Orders.query.get(order_id)
        if order:
            # Delete associated records
            Order_Detail.query.filter_by(order_id=order_id).delete()
            Payment.query.filter_by(order_id=order_id).delete()
            Shipping.query.filter_by(order_id=order_id).delete()
            
            # Delete the order
            db.session.delete(order)
            db.session.commit()
            flash('Order deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Database error in admin_orders delete_order: {e}")
        flash('Error deleting order', 'error')
    
    return redirect(url_for('admin_orders.index'))

@admin_orders.route('/test/<int:order_id>')
def test_order(order_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        order = Orders.query.get(order_id)
        if not order:
            return f"Order {order_id} not found"
            
        customer = Customer.query.get(order.customer_id)
        
        result = {
            'order_id': order.order_id,
            'customer_name': customer.name if customer else 'Unknown',
            'order_date': order.order_date.strftime('%Y-%m-%d %H:%M'),
            'status': order.status,
            'total_amount': float(order.total_amount)
        }
        
        return str(result)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return f"Error: {str(e)}<br><pre>{error_trace}</pre>" 