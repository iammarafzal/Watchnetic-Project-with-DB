import click
from flask.cli import with_appcontext
from models import db, Admin, Product, Customer
from werkzeug.security import generate_password_hash
import os
import csv
from datetime import datetime

@click.command('create-admin')
@click.argument('username')
@click.argument('email')
@click.argument('password')
@with_appcontext
def create_admin(username, email, password):
    """Create an admin user."""
    admin = Admin.query.filter_by(username=username).first()
    if admin:
        click.echo(f'Admin user {username} already exists')
        return
    
    admin = Admin(username=username, email=email)
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    
    click.echo(f'Admin user {username} created successfully')

@click.command('import-products')
@click.argument('csv_file')
@with_appcontext
def import_products(csv_file):
    """Import products from a CSV file."""
    if not os.path.exists(csv_file):
        click.echo(f'Error: File {csv_file} does not exist')
        return
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                # Check if product already exists
                product = Product.query.filter_by(name=row['name']).first()
                if product:
                    click.echo(f'Product {row["name"]} already exists, skipping')
                    continue
                
                # Create new product
                product = Product(
                    name=row['name'],
                    description=row.get('description', ''),
                    price=float(row.get('price', 0)),
                    stock=int(row.get('stock', 0)),
                    image_url=row.get('image_url', ''),
                    category=row.get('category', '')
                )
                db.session.add(product)
                count += 1
            
            db.session.commit()
            click.echo(f'Successfully imported {count} products')
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error importing products: {str(e)}')

@click.command('reset-password')
@click.argument('username')
@click.argument('new_password')
@with_appcontext
def reset_password(username, new_password):
    """Reset an admin or customer password."""
    # Try to find admin first
    admin = Admin.query.filter_by(username=username).first()
    if admin:
        admin.set_password(new_password)
        db.session.commit()
        click.echo(f'Admin password for {username} reset successfully')
        return
    
    # If not an admin, check for customer by email
    customer = Customer.query.filter_by(email=username).first()
    if customer:
        customer.set_password(new_password)
        db.session.commit()
        click.echo(f'Customer password for {username} reset successfully')
        return
    
    click.echo(f'No user found with username/email {username}')

def init_app(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(import_products)
    app.cli.add_command(reset_password) 