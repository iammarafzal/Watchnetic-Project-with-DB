from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import Product
import os
import uuid
from datetime import datetime

# Create the blueprint
admin_products = Blueprint('admin_products', __name__, url_prefix='/admin/products')

@admin_products.route('/')
def index():
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        products = Product.query.all()
    except Exception as e:
        print(f"Database error in admin_products index: {e}")
        products = []
    
    return render_template('admin/products/index.html', products=products)

@admin_products.route('/add', methods=['GET', 'POST'])
def add():
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            price = float(request.form.get('price'))
            stock = int(request.form.get('stock'))
            
            product = Product(
                name=name,
                description=description,
                price=price,
                stock=stock
            )
            
            # Handle image upload
            image = request.files.get('image')
            if image and image.filename:
                # Generate a unique filename to prevent overwriting
                # Get the file extension
                file_extension = os.path.splitext(image.filename)[1]
                
                # Create a unique filename using timestamp and UUID
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
                
                # Set the image path
                product.image_url = f"images/watches/{unique_filename}"
                
                # Ensure directory exists
                os.makedirs('static/images/watches', exist_ok=True)
                
                # Save the image
                image_path = os.path.join('static/images/watches', unique_filename)
                image.save(image_path)
            
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully', 'success')
            return redirect(url_for('admin_products.index'))
        
        except Exception as e:
            db.session.rollback()
            print(f"Database error in admin_products add: {e}")
            flash('Error adding product', 'error')
    
    return render_template('admin/products/add.html')

@admin_products.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        product = Product.query.get(product_id)
        if not product:
            flash('Product not found', 'error')
            return redirect(url_for('admin_products.index'))
        
        if request.method == 'POST':
            product.name = request.form.get('name')
            product.description = request.form.get('description')
            product.price = float(request.form.get('price'))
            product.stock = int(request.form.get('stock'))
            
            # Handle image upload
            image = request.files.get('image')
            if image and image.filename:
                # Generate a unique filename to prevent overwriting
                # Get the file extension
                file_extension = os.path.splitext(image.filename)[1]
                
                # Create a unique filename using timestamp and UUID
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
                
                # Set the image path
                product.image_url = f"images/watches/{unique_filename}"
                
                # Ensure directory exists
                os.makedirs('static/images/watches', exist_ok=True)
                
                # Save the image
                image_path = os.path.join('static/images/watches', unique_filename)
                image.save(image_path)
            
            db.session.commit()
            flash('Product updated successfully', 'success')
            return redirect(url_for('admin_products.index'))
    
    except Exception as e:
        db.session.rollback()
        print(f"Database error in admin_products edit: {e}")
        flash('Error updating product', 'error')
        return redirect(url_for('admin_products.index'))
    
    return render_template('admin/products/edit.html', product=product)

@admin_products.route('/delete/<int:product_id>')
def delete(product_id):
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        product = Product.query.get(product_id)
        if product:
            db.session.delete(product)
            db.session.commit()
            flash('Product deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Database error in admin_products delete: {e}")
        flash('Error deleting product', 'error')
    
    return redirect(url_for('admin_products.index')) 