import click
from app.extensions import db
from app.models import Product, Customer, Review, Admin
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def register_cli_commands(app):
    @app.cli.command('seed-watches')
    def seed_watches_command():
        """Populate database with 20 watches and reviews"""
        print("Rebuilding database...")
        db.drop_all()
        db.create_all()
        
        print("Creating Admin account (admin@watchnetic.com / admin@123)...")
        admin = Admin(username='admin', email='admin@watchnetic.com')
        admin.set_password('admin@123')
        db.session.add(admin)

        print("Creating Dummy Customer for reviews...")
        customer = Customer(
            name="Reviewer Pro", email="reviewer@example.com", 
            phone="555-0192", password=generate_password_hash("password123")
        )
        db.session.add(customer)
        db.session.commit()

        print("Generating 20 Premium Watches...")
        names = ["Royal Oak", "Speedmaster", "Submariner", "Classic Fusion", "Smart Pro 5", 
                 "Vintage 1965", "Nautilus", "Daytona", "Seamaster", "Carrera", 
                 "Tank Must", "Navitimer", "Reverso", "Fifty Fathoms", "Santos", 
                 "Luminor", "Monaco", "Master Control", "Altiplano", "Chronomat"]
        categories = ["Luxury", "Sports", "Casual", "Smart", "Vintage"]

        # High-res unsplash watch images for distinct angles
        main_imgs = [
            "https://images.unsplash.com/photo-1524592094714-0f0654e20314?auto=format&fit=crop&q=80&w=800",
            "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?auto=format&fit=crop&q=80&w=800",
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&q=80&w=800",
            "https://images.unsplash.com/photo-1614164185128-e4ec99c436d7?auto=format&fit=crop&q=80&w=800"
        ]
        
        comments = [
            "Absolutely stunning piece.", "Exceeded my expectations entirely.", 
            "The build quality is phenomenal.", "Very comfortable on the wrist.", 
            "Highly recommended for watch enthusiasts.", "A bit heavy but looks incredible.", 
            "Perfect daily driver watch.", "The finishing is just out of this world.", 
            "Gets so many compliments.", "Keeps perfect time, completely worth it."
        ]
        
        products = []
        for i, name in enumerate(names):
            # 15 in stock, 5 out of stock
            stock = random.randint(10, 50) if i < 15 else 0
            
            # Ensure each watch has distinct main and angle images
            img_pool = random.sample(main_imgs, 3)
            
            p = Product(
                name=f"{name} Edition",
                description=f"A masterpiece of horological engineering. The {name} represents the pinnacle of premium watchmaking, offering unparalleled precision, luxurious materials, and a design that commands respect in any setting.",
                price=round(random.uniform(800.0, 9999.0), 2),
                stock=stock,
                category=random.choice(categories),
                image_url=img_pool[0], # Front
                additional_images=[img_pool[1], img_pool[2]] # Side, Case-back
            )
            db.session.add(p)
            products.append(p)
            
        db.session.commit()
        
        print("Generating Realistic Reviews...")
        for i in range(15):
            p = products[i]
            for _ in range(5):
                r = Review(
                    customer_id=customer.customer_id,
                    product_id=p.product_id,
                    order_id=None,
                    rating=random.randint(4, 5),
                    comment=random.choice(comments),
                    review_date=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(r)
                
        db.session.commit()
        print("Successfully seeded 20 products, images, and realistic reviews!")
