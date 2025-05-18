# Watchnetic - E-commerce Watch Store

Watchnetic is a modern e-commerce platform specializing in watches. The application offers a complete shopping experience for customers and comprehensive management tools for administrators.

## Features

- **Customer Features**
  - Browse watch catalog with filtering and searching
  - User account management (registration, login, profile)
  - Shopping cart functionality
  - Order processing and payment
  - Product reviews and ratings
  - Responsive design for all devices

- **Admin Features**
  - Product management (add, edit, delete)
  - Order management and status updates
  - Customer management
  - Analytics dashboard
  - Secure admin authentication

## Technology Stack

- **Backend**: Python with Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Additional Libraries**: SQLAlchemy, Werkzeug

## Project Structure

The project follows a modular structure:

```
watchnetic/
├── admin/                     # Admin panel blueprints
│   ├── products.py
│   ├── orders.py
│   ├── customers.py
│   ├── dashboard.py
│   └── auth.py
├── static/                    # Static assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/                 # HTML templates
│   ├── admin/
│   ├── customer/
│   └── ...
├── app.py                     # Main application file
├── models.py                  # Database models
├── config.py                  # Configuration settings
├── commands.py                # Flask CLI commands
├── setup.py                   # Database & sample data setup
├── db_migrations.py           # Database migrations
└── requirements.txt           # Project dependencies
```

## Setup and Installation

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/watchnetic.git
   cd watchnetic
   ```

2. **Create and activate a virtual environment**
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On MacOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   DATABASE_URL=mysql://username:password@localhost/watchnetic_db
   ```

5. **Setup the database**
   ```
   # Create the database schema
   python setup.py
   
   # To also create sample data
   python setup.py --with-sample-data
   ```

6. **Run the application**
   ```
   flask run
   ```

7. **Access the application**
   - The store: http://localhost:5000/
   - Admin panel: http://localhost:5000/admin/auth/login
     - Default admin credentials: admin / admin@123

## Development

### Adding a new admin user

```
flask create-admin username admin@example.com password123
```

### Importing products from CSV

```
flask import-products path/to/products.csv
```

### Resetting a user password

```
flask reset-password username new_password
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- All watch images and descriptions are for demonstration purposes only.
- Special thanks to all contributors who made this project possible. 