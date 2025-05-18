import os
import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

def run_migrations():
    """
    Consolidated database migration script.
    Handles all necessary database structure updates in a single file.
    """
    try:
        # Connect to MySQL database
        password = os.environ.get('DB_PASSWORD', '')
        conn = pymysql.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=password,
            database=os.environ.get('DB_NAME', 'watchnetic_db')
        )
        cursor = conn.cursor()
        
        print("Running database migrations...")
        
        # 1. Product table updates
        print("Updating product table...")
        
        # Add category column
        cursor.execute('''
            ALTER TABLE product 
            ADD COLUMN IF NOT EXISTS category VARCHAR(50)
        ''')
        
        # Add created_at column
        cursor.execute('''
            ALTER TABLE product 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ''')
        
        # Add updated_at column
        cursor.execute('''
            ALTER TABLE product 
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ''')
        
        # 2. Admin table updates
        print("Updating admin table...")
        
        # Check if admin table exists
        cursor.execute("SHOW TABLES LIKE 'admin'")
        if cursor.fetchone():
            # Check if password column exists
            cursor.execute("SHOW COLUMNS FROM admin LIKE 'password'")
            if not cursor.fetchone():
                cursor.execute('''
                    ALTER TABLE admin 
                    ADD COLUMN password VARCHAR(255) NOT NULL
                ''')
                
                # Set default password for admin
                cursor.execute("SELECT admin_id, username FROM admin")
                admins = cursor.fetchall()
                for admin_id, username in admins:
                    default_password = f"{username}@123"
                    hashed_password = generate_password_hash(default_password)
                    cursor.execute(
                        "UPDATE admin SET password = %s WHERE admin_id = %s",
                        (hashed_password, admin_id)
                    )
                    print(f"Set default password for admin: {username}")
        
        # 3. Orders table updates
        print("Updating orders table...")
        
        # Add subtotal column
        cursor.execute('''
            ALTER TABLE orders 
            ADD COLUMN IF NOT EXISTS subtotal DECIMAL(10,2)
        ''')
        
        # Update existing orders
        cursor.execute('''
            UPDATE orders SET subtotal = total_amount
            WHERE subtotal IS NULL
        ''')
        
        # 4. Order detail table updates
        print("Updating order_detail table...")
        
        # Add subtotal column if not exists
        cursor.execute('''
            ALTER TABLE order_detail 
            ADD COLUMN IF NOT EXISTS subtotal DECIMAL(10,2)
        ''')
        
        # Update existing order details
        cursor.execute('''
            UPDATE order_detail SET subtotal = price * quantity
            WHERE subtotal IS NULL
        ''')
        
        # 5. Review table updates
        print("Updating review table...")
        
        # Add order_id column if not exists
        cursor.execute('''
            ALTER TABLE review 
            ADD COLUMN IF NOT EXISTS order_id INT
        ''')
        
        # Add foreign key constraint if not exists
        cursor.execute('''
            SELECT COUNT(*) 
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'review' 
            AND COLUMN_NAME = 'order_id' 
            AND REFERENCED_TABLE_NAME = 'orders'
        ''')
        
        if cursor.fetchone()[0] == 0:
            # Add the foreign key constraint
            cursor.execute('''
                ALTER TABLE review 
                ADD CONSTRAINT fk_review_order
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            ''')
            
        # 6. Shipping table updates
        print("Updating shipping table...")
        
        # Add tracking_number column
        cursor.execute('''
            ALTER TABLE shipping 
            ADD COLUMN IF NOT EXISTS tracking_number VARCHAR(100)
        ''')
        
        # Commit all changes
        conn.commit()
        print("All database migrations completed successfully!")
        
    except pymysql.Error as e:
        print(f"MySQL Error: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    run_migrations() 