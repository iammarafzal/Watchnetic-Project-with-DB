# Watchnetic - E-commerce Watch Store

Watchnetic is a modern, responsive, and beautifully refactored e-commerce platform specializing in premium digital timepieces. The application offers a stunningly designed shopping experience for customers and robust management tools for administrators.

## Features

- **Frontend & UI (Tailwind CSS)**
  - Entirely built using modern **Tailwind CSS** utility classes for a pixel-perfect, glassmorphic, and high-fidelity interface.
  - Interactive components powered by lightweight **Alpine.js** without any bulky frontend frameworks.
  - Fully responsive grid layouts adapting seamlessly from mobile to ultra-wide desktop displays.

- **Customer Features**
  - Browse watch catalog with intuitive category filtering.
  - User account management (secure registration, login, profile).
  - Dynamic shopping cart functionality and elegant checkout flows.
  - Product stock indicators and detailed image showcases.

- **Admin Features**
  - Modular product management framework via secure routing.
  - Customer order tracking and lifecycle updates.
  - Secure and dedicated admin authentication pipelines.

## Technology Stack

- **Backend**: Python 3.x, Flask (Application Factory Pattern)
- **Database**: SQLite (Zero configuration needed, perfectly portable)
- **ORM**: SQLAlchemy
- **Frontend**: Tailwind CSS (Play CDN), Alpine.js, HTML5
- **Icons**: FontAwesome 6

## Project Structure

The project strictly follows the **Flask Application Factory** pattern utilizing modular Blueprints, ensuring scalability and a clean architecture.

```text
watchnetic/
├── app/
│   ├── __init__.py            # Flask App Factory and configuration setup
│   ├── extensions.py          # Centralized SQLAlchemy extension
│   ├── models.py              # Definitive local Database models (SQLite ready)
│   ├── admin/                 # Administrator panel blueprints
│   ├── customer/              # Customer blueprints (auth, registration)
│   ├── main/                  # Core view routes (home, about, search)
│   ├── shop/                  # E-commerce pipelines (cart, checkout, orders)
│   ├── templates/             # Pure Tailwind HTML templates 
│   └── static/                # Static assets (images)
├── instance/                  # Auto-generated SQLite database location
├── run.py                     # Entry point to launch the local server
├── config.py                  # Core application configuration settings
├── commands.py                # Flask CLI commands for terminal management
├── setup.py                   # Automated Database schema and sample data initialization
└── requirements.txt           # Python package dependencies
```

## Setup and Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/iammarafzal/watchnetic.git
   cd watchnetic
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On MacOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=run.py
   FLASK_DEBUG=1
   SECRET_KEY=your_secure_random_key_here
   ```

5. **Initialize the local database**
   Watchnetic uses SQLite, meaning no external database installations are required. Run the setup script to instantly generate schemas and seed the store:
   ```bash
   # Create the database schema and inject complete sample data
   python setup.py --with-sample-data
   ```

6. **Run the application**
   Launch the development server:
   ```bash
   python run.py
   ```

7. **Access the application**
   - The storefront: http://localhost:5000/
   - The platform is instantly usable upon boot.

## Development Commands

Watchnetic includes helpful CLI hooks defined in `commands.py`:

### Adding a new admin user
```bash
flask create-admin username admin@example.com password123
```

### Importing products from CSV
```bash
flask import-products path/to/products.csv
```

### Resetting a user password
```bash
flask reset-password username new_password
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.
