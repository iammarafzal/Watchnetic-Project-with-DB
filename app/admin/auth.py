from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.extensions import db
from app.models import Admin
from werkzeug.security import generate_password_hash

# Create the blueprint
admin_auth = Blueprint('admin_auth', __name__, url_prefix='/admin/auth')

@admin_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            session['admin_id'] = admin.admin_id
            session['admin_username'] = admin.username
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin_dashboard.index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin/login.html')

@admin_auth.route('/logout')
def logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('admin_auth.login'))

@admin_auth.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'admin_id' not in session:
        flash('Please login to access the admin area', 'warning')
        return redirect(url_for('admin_auth.login'))
    
    try:
        admin = Admin.query.get(session['admin_id'])
        if not admin:
            flash('Admin not found', 'error')
            return redirect(url_for('admin_auth.logout'))
        
        if request.method == 'POST':
            admin.username = request.form.get('username')
            admin.email = request.form.get('email')
            
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if current_password and new_password and confirm_password:
                if not admin.check_password(current_password):
                    flash('Current password is incorrect', 'error')
                    return render_template('admin/profile.html', admin=admin)
                
                if new_password != confirm_password:
                    flash('New passwords do not match', 'error')
                    return render_template('admin/profile.html', admin=admin)
                
                admin.set_password(new_password)
                flash('Password updated successfully', 'success')
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('admin_dashboard.index'))
    except Exception as e:
        db.session.rollback()
        print(f"Database error in admin_auth profile: {e}")
        flash('Error updating profile', 'error')
    
    return render_template('admin/profile.html', admin=admin) 