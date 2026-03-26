from flask import render_template, request, flash, redirect, url_for
from app.models import Product, Review
from . import main

@main.route('/')
def index():
    latest_products = Product.query.order_by(Product.product_id.desc()).limit(6).all()
    return render_template('index.html', latest_products=latest_products)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/blogs')
def blogs():
    return render_template('blogs.html')

@main.route('/blog/<slug>')
def blog_post(slug):
    template_path = f'blog_posts/{slug}.html'
    try:
        return render_template(template_path)
    except:
        return render_template('blog_post_404.html')

@main.route('/faqs')
def faqs():
    return render_template('faqs.html')

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('contact.html')

@main.route('/subscribe-newsletter', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email')
    if email:
        flash('Thank you for subscribing to our newsletter!', 'success')
    return redirect(request.referrer or url_for('main.index'))
