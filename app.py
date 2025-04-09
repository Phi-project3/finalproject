import os
import urllib
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, text
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

# Initialize database and login manager
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///your_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Create User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Initialize DB
with app.app_context():
    db.create_all()  # Make sure tables are created

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = "login"  # Redirect to login if not logged in

# Database connection string (SQL Server or SQLite fallback)
raw_connection_string = os.environ.get('DATABASE_URL')
if raw_connection_string is None:
    raw_connection_string = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=tcp:sustainabite-server.database.windows.net,1433;"
        "Database=sustainabite-database;"
        "Uid=sustainabite-server-admin;"
        "Pwd={Qvs6YFz6AN$ekYvN};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

params = urllib.parse.quote_plus(raw_connection_string)
engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/landing')
@login_required
def landing():
    return render_template('landing.html')

@app.route('/test')
def test():
    return render_template('jonnas_test.html')

@app.route('/scan')
def scan():
    return render_template('barcode_scan.html')

@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term')

    query = text("""SELECT * FROM [dbo].[sustainabite] WHERE "Product name" LIKE :term""")

    with engine.connect() as connection:
        result = connection.execute(query, {"term": f"%{search_term}%"})
        records = [dict(row._mapping) for row in result.fetchall()]
        
    return render_template('search.html', records=records, search_term=search_term)

@app.route('/product/<code>')
def product_details(code):

    query = text("""
                 SELECT *
                 FROM [dbo].[sustainabite]
                 WHERE Barcode = :code
                 """)
    
    with engine.connect() as connection:
        result = connection.execute(query, {"code": code})

        product = result.fetchone()
        
        if product:
            product = dict(product._mapping)
        else:
            product = None

    return render_template('product_details.html', product=product)


@app.route('/about')
def about():
    return render_template('about.html')

# Product query routes
@app.route('/query-chocolate')
def query_chocolate():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * 
            FROM [dbo].[sustainabite]
            WHERE "Product group" = 'Chocolate products'
        """))
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

@app.route('/query-alcohol')
def query_alcohol():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * 
            FROM [dbo].[sustainabite]
            WHERE "Product group" = 'Alcoholic beverages'
        """))
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

@app.route('/query-canned-food')
def query_canned_food():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * 
            FROM [dbo].[sustainabite]
            WHERE "Product group" = 'Canned foods'
        """))
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

@app.route('/query-cheese')
def query_cheese():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * 
            FROM [dbo].[sustainabite]
            WHERE "Product group" = 'Cheese'
        """))
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

@app.route('/query-fruit')
def query_fruit():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * 
            FROM [dbo].[sustainabite]
            WHERE "Product group" = 'Fruits'
        """))
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

@app.route('/query-ice-cream')
def query_ice_cream():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * 
            FROM [dbo].[sustainabite]
            WHERE "Product group" = 'Ice cream'
        """))
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

@app.route('/query-meat')
def query_meat():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * 
            FROM [dbo].[sustainabite]
            WHERE "Product group" = 'Meat'
        """))
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

@app.route('/query-milk')
def query_milk():
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT * 
            FROM [dbo].[sustainabite]
            WHERE "Product group" = 'Milk and yogurt'
        """))
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

# Cart routes
@app.route('/add_to_cart/<product_code>', methods=['POST'])
def add_to_cart(product_code):
    cart = session.get('cart', {})

    if product_code in cart:
        cart[product_code] += 1
    else:
        cart[product_code] = 1

    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    return render_template('cart.html', cart=cart)

# Login and registration routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            return "Username already taken. Please choose a different one."
        
        # Create a new user
        new_user = User(username=username)
        new_user.set_password(password)
        
        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))  # Redirect to login after successful registration
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))  # Redirect to home page after successful login
        else:
            return "Invalid credentials. Please try again."
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
