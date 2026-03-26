from flask import render_template, request, session, flash, redirect, url_for
from app.models import db, Product, Review, Customer, Orders, Order_Detail, Shipping, Payment
from datetime import datetime
from . import shop

@shop.route('/watches')
def watches():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', 'featured')
    per_page = 8
    
    query = Product.query
    
    if sort == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort == 'newest':
        query = query.order_by(Product.product_id.desc())
    else:
        query = query.order_by(Product.product_id.asc())

    products_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('watches.html', products=products_pagination.items, pagination=products_pagination, current_sort=sort)

@shop.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    related_products = Product.query.filter(Product.product_id != product_id).limit(3).all()
    
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.review_date.desc()).all()
    
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    return render_template('product_detail.html', product=product, related_products=related_products, 
                          reviews=reviews, avg_rating=avg_rating)

@shop.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('search.html')
    
    products = Product.query.filter(
        (Product.name.like(f'%{query}%')) | 
        (Product.description.like(f'%{query}%'))
    ).all()
    
    return render_template('search.html', products=products, query=query)

@shop.route('/cart')
def view_cart():
    cart_items = []
    total = 0
    
    if 'cart' in session and session['cart']['items']:
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

@shop.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'customer_id' not in session:
        flash('Please login to checkout', 'warning')
        return redirect(url_for('customer.customer_login'))
    
    if 'cart' not in session or not session['cart']['items']:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop.watches'))
    
    customer_id = session['customer_id']
    customer = Customer.query.get(customer_id)
    
    cart_items = []
    total = 0
    
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
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state', '')
        country = request.form.get('country')
        postal_code = request.form.get('postal_code')
        phone = request.form.get('phone')
        
        order = Orders(
            customer_id=customer_id,
            order_date=datetime.now(),
            total_amount=total,
            status='Pending'
        )
        
        db.session.add(order)
        db.session.flush() 
        
        for item in cart_items:
            order_detail = Order_Detail(
                order_id=order.order_id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                unit_price=item['price']
            )
            db.session.add(order_detail)
        
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
            session['cart'] = {'items': {}, 'count': 0, 'total': 0}
            flash('Order placed successfully!', 'success')
            return redirect(url_for('shop.order_confirmation'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('checkout.html', customer=customer, cart_items=cart_items, total=total)

@shop.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        return redirect(url_for('shop.order_confirmation'))
    return render_template('payment.html')

@shop.route('/order-confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')

@shop.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = int(request.form.get('quantity', 1))
    
    if 'cart' not in session:
        session['cart'] = {'items': {}, 'count': 0, 'total': 0}
    
    cart = session['cart']
    product_id_str = str(product_id)
    
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
    
    cart['count'] = sum(item['quantity'] for item in cart['items'].values())
    cart['total'] = sum(item['price'] * item['quantity'] for item in cart['items'].values())
    
    session['cart'] = cart
    flash('Product added to cart successfully!', 'success')
    return redirect(url_for('shop.watches'))

@shop.route('/update-cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    if 'cart' not in session:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop.view_cart'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        return redirect(url_for('shop.remove_from_cart', product_id=product_id))
    
    cart = session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart['items']:
        cart['items'][product_id_str]['quantity'] = quantity
        cart['count'] = sum(item['quantity'] for item in cart['items'].values())
        cart['total'] = sum(item['price'] * item['quantity'] for item in cart['items'].values())
        session['cart'] = cart
        flash('Cart updated successfully!', 'success')
    
    return redirect(url_for('shop.view_cart'))

@shop.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' not in session:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('shop.view_cart'))
    
    cart = session['cart']
    product_id_str = str(product_id)
    
    if product_id_str in cart['items']:
        del cart['items'][product_id_str]
        cart['count'] = sum(item['quantity'] for item in cart['items'].values())
        cart['total'] = sum(item['price'] * item['quantity'] for item in cart['items'].values())
        session['cart'] = cart
        flash('Item removed from cart successfully!', 'success')
    
    return redirect(url_for('shop.view_cart'))

@shop.route('/clear-cart')
def clear_cart():
    if 'cart' in session:
        session['cart'] = {'items': {}, 'count': 0, 'total': 0}
        flash('Cart cleared successfully!', 'success')
    return redirect(url_for('shop.view_cart'))
