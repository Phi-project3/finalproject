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

# Create User model for login
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

    query = text("""
                 SELECT *
                 FROM [dbo].[sustainabite]
                 WHERE "Product name" LIKE :term
                 """)

    with engine.connect() as connection:
        result = connection.execute(query, {"term": f"%{search_term}%"})

        records = [dict(row._mapping) for row in result.fetchall()]
        
    return render_template('search.html', records=records, search_term=search_term)

@app.route('/about')
def about():
    return render_template('about.html')


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

@app.route('/teamphi')
def page3():
    return render_template('winteriscoming.html')

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

# Basket routes
@app.route('/api/basket', methods=['GET'])
def get_basket():
    user_id = session.get('user_id', 'anonymous-user')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get basket ID
    cursor.execute("SELECT BasketID FROM ShoppingBasket WHERE UserID = ?", user_id)
    basket_row = cursor.fetchone()
    
    if not basket_row:
        return jsonify({"items": []})
    
    basket_id = basket_row[0]
    
    # Get basket items with product details
    cursor.execute("""
        SELECT bi.ItemID, bi.Barcode, bi.Quantity, p.[Product name], 
               p.[Environmental score], p.[Carbon footprint 1kg]
        FROM BasketItems bi
        JOIN sustainabite p ON bi.Barcode = p.Barcode
        WHERE bi.BasketID = ?
    """, basket_id)
    
    items = []
    for row in cursor.fetchall():
        items.append({
            "itemId": row[0],
            "barcode": row[1],
            "quantity": row[2],
            "productName": row[3],
            "environmentalScore": row[4],
            "carbonFootprint": row[5]
        })
    
    return jsonify({"items": items})

@app.route('/api/basket/add', methods=['POST'])
def add_to_basket():
    data = request.get_json()
    barcode = data.get('barcode')
    quantity = data.get('quantity', 1)
    user_id = session.get('user_id', 'anonymous-user')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get or create basket
    cursor.execute("SELECT BasketID FROM ShoppingBasket WHERE UserID = ?", user_id)
    basket_row = cursor.fetchone()
    
    if not basket_row:
        cursor.execute("""
            INSERT INTO ShoppingBasket (UserID, CreatedDate, LastModified)
            OUTPUT INSERTED.BasketID
            VALUES (?, GETDATE(), GETDATE())
        """, user_id)
        basket_id = cursor.fetchone()[0]
    else:
        basket_id = basket_row[0]
    
    # Check if item exists in basket
    cursor.execute("""
        SELECT ItemID, Quantity FROM BasketItems 
        WHERE BasketID = ? AND Barcode = ?
    """, basket_id, barcode)
    
    item_row = cursor.fetchone()
    
    if item_row:
        # Update quantity
        new_quantity = item_row[1] + quantity
        cursor.execute("""
            UPDATE BasketItems SET Quantity = ?
            WHERE ItemID = ?
        """, new_quantity, item_row[0])
    else:
        # Add new item
        cursor.execute("""
            INSERT INTO BasketItems (BasketID, Barcode, Quantity, DateAdded)
            VALUES (?, ?, ?, GETDATE())
        """, basket_id, barcode, quantity)
    
    # Update basket timestamp
    cursor.execute("""
        UPDATE ShoppingBasket SET LastModified = GETDATE()
        WHERE BasketID = ?
    """, basket_id)
    
    conn.commit()
    
    return jsonify({"success": True})

@app.route('/api/basket/remove', methods=['POST'])
def remove_from_basket():
    data = request.get_json()
    barcode = data.get('barcode')
    user_id = session.get('user_id', 'anonymous-user')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get basket ID
    cursor.execute("SELECT BasketID FROM ShoppingBasket WHERE UserID = ?", user_id)
    basket_row = cursor.fetchone()

    if basket_row:
        basket_id = basket_row[0]
        cursor.execute("""
            DELETE FROM BasketItems WHERE BasketID = ? AND Barcode = ?
        """, basket_id, barcode)
        conn.commit()

    return jsonify({"success": True})

@app.route('/basket')
def basket_page():
    return render_template('basket.html')

if __name__ == '__main__':
    app.run(debug=True)