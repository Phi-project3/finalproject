import os
import urllib
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from sqlalchemy import create_engine, text
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pyodbc

app = Flask(__name__)

# Set a fixed secret key for development
app.secret_key = 'your-secret-key-here'  # Change this in production!

def get_db_connection():
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
    conn = pyodbc.connect(raw_connection_string)
    
    # Create basket tables if they don't exist
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ShoppingBasket')
        BEGIN
            CREATE TABLE ShoppingBasket (
                BasketID INT IDENTITY(1,1) PRIMARY KEY,
                UserID VARCHAR(100) NOT NULL,
                CreatedDate DATETIME NOT NULL,
                LastModified DATETIME NOT NULL
            )
        END
    """)
    
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'BasketItems')
        BEGIN
            CREATE TABLE BasketItems (
                ItemID INT IDENTITY(1,1) PRIMARY KEY,
                BasketID INT NOT NULL,
                Barcode VARCHAR(50) NOT NULL,
                Quantity INT NOT NULL,
                DateAdded DATETIME NOT NULL,
                FOREIGN KEY (BasketID) REFERENCES ShoppingBasket(BasketID)
            )
        END
    """)
    conn.commit()
    
    return conn

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


@app.route('/product/<code>')
def product_details(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT *
        FROM [dbo].[sustainabite]
        WHERE Barcode = ?
    """, code)
    
    product = cursor.fetchone()
    
    if product:
        # Convert the row to a dictionary
        columns = [column[0] for column in cursor.description]
        product = dict(zip(columns, product))
    
    return render_template('product_details.html', product=product)




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
            return redirect(url_for('landing'))  # Redirect to home page after successful login
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
    try:
        if 'user_id' not in session:
            session['user_id'] = 'anonymous-user'
        
        user_id = session['user_id']
        print(f"DEBUG: Getting basket for user: {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get basket ID
            cursor.execute("SELECT BasketID FROM ShoppingBasket WHERE UserID = ?", user_id)
            basket_row = cursor.fetchone()
            
            if not basket_row:
                print("DEBUG: No basket found for user")
                return jsonify({"items": []})
            
            basket_id = basket_row[0]
            print(f"DEBUG: Found basket ID: {basket_id}")
            
            # Get basket items with product details in a single query
            query = """
                SELECT 
                    bi.Barcode,
                    bi.Quantity,
                    s.[Product name],
                    s.[Environmental score],
                    s.[Carbon footprint 1kg]
                FROM BasketItems bi
                INNER JOIN [dbo].[sustainabite] s ON CAST(bi.Barcode AS VARCHAR) = CAST(s.Barcode AS VARCHAR)
                WHERE bi.BasketID = ?
            """
            cursor.execute(query, basket_id)
            rows = cursor.fetchall()
            print(f"DEBUG: Found {len(rows)} items")
            
            items = []
            for row in rows:
                try:
                    item = {
                        "barcode": row[0],
                        "quantity": row[1],
                        "productName": row[2],
                        "environmentalScore": float(row[3]) if row[3] is not None else 0,
                        "carbonFootprint": float(row[4]) if row[4] is not None else 0
                    }
                    print(f"DEBUG: Created item: {item}")
                    items.append(item)
                except Exception as item_error:
                    print(f"DEBUG: Error processing row {row}: {str(item_error)}")
                    continue
            
            response = {"items": items}
            print(f"DEBUG: Returning response: {response}")
            return jsonify(response)
            
        except Exception as inner_error:
            print(f"DEBUG: Database error: {str(inner_error)}")
            import traceback
            traceback.print_exc()
            return jsonify({"error": f"Database error: {str(inner_error)}"}), 500
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"DEBUG: Error in get_basket: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/basket/add', methods=['POST'])
def add_to_basket():
    try:
        data = request.get_json()
        barcode = data.get('barcode')
        quantity = data.get('quantity', 1)  # Default to 1 if not specified
        
        # Ensure we have a user_id in session
        if 'user_id' not in session:
            session['user_id'] = 'anonymous-user'
        
        user_id = session['user_id']
        print(f"DEBUG: Adding to basket - Barcode: {barcode}, User ID: {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # First verify the product exists in sustainabite table
            cursor.execute("SELECT [Product name] FROM [dbo].[sustainabite] WHERE Barcode = ?", barcode)
            product = cursor.fetchone()
            if not product:
                return jsonify({
                    "success": False,
                    "error": "Product not found in database"
                }), 404
            
            # Get or create basket
            cursor.execute("SELECT BasketID FROM ShoppingBasket WHERE UserID = ?", user_id)
            basket_row = cursor.fetchone()
            
            if not basket_row:
                print("DEBUG: Creating new basket")
                cursor.execute("""
                    INSERT INTO ShoppingBasket (UserID, CreatedDate, LastModified)
                    OUTPUT INSERTED.BasketID
                    VALUES (?, GETDATE(), GETDATE())
                """, user_id)
                basket_id = cursor.fetchone()[0]
            else:
                basket_id = basket_row[0]
                print(f"DEBUG: Using existing basket: {basket_id}")
            
            # Check if item exists in basket
            cursor.execute("""
                SELECT ItemID, Quantity FROM BasketItems 
                WHERE BasketID = ? AND Barcode = ?
            """, basket_id, barcode)
            
            item_row = cursor.fetchone()
            
            if item_row:
                # If quantity is not explicitly specified (adding from product page), set to 1
                # If quantity is specified (updating from basket page), use that quantity
                new_quantity = 1 if not 'quantity' in data else quantity
                print(f"DEBUG: Updating existing item quantity to {new_quantity}")
                cursor.execute("""
                    UPDATE BasketItems SET Quantity = ?
                    WHERE ItemID = ?
                """, new_quantity, item_row[0])
            else:
                # Add new item
                print("DEBUG: Adding new item to basket")
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
            
            # Get total items in basket
            cursor.execute("""
                SELECT SUM(Quantity) FROM BasketItems 
                WHERE BasketID = ?
            """, basket_id)
            basket_count = cursor.fetchone()[0] or 0
            print(f"DEBUG: New basket count: {basket_count}")
            
            return jsonify({
                "success": True,
                "basket_count": basket_count
            })
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"DEBUG: Error in add_to_basket: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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

@app.route('/api/basket/empty', methods=['POST'])
def empty_basket():
    user_id = session.get('user_id', 'anonymous-user')
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get basket ID
        cursor.execute("SELECT BasketID FROM ShoppingBasket WHERE UserID = ?", user_id)
        basket_row = cursor.fetchone()

        if basket_row:
            basket_id = basket_row[0]
            # Delete all items from the basket
            cursor.execute("DELETE FROM BasketItems WHERE BasketID = ?", basket_id)
            conn.commit()

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error emptying basket: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/basket')
def basket_page():
    return render_template('basket.html')

@app.route('/api/basket/count', methods=['GET'])
def get_basket_count():
    try:
        if 'user_id' not in session:
            session['user_id'] = 'anonymous-user'
        
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get basket ID
            cursor.execute("SELECT BasketID FROM ShoppingBasket WHERE UserID = ?", user_id)
            basket_row = cursor.fetchone()
            
            if not basket_row:
                return jsonify({"count": 0})
            
            basket_id = basket_row[0]
            
            # Get total items count
            cursor.execute("""
                SELECT SUM(Quantity) FROM BasketItems 
                WHERE BasketID = ?
            """, basket_id)
            
            count = cursor.fetchone()[0] or 0
            return jsonify({"count": count})
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        print(f"Error in get_basket_count: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test_basket_tables')
def test_basket_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Test ShoppingBasket table
            cursor.execute("""
                SELECT COUNT(*) FROM ShoppingBasket
            """)
            basket_count = cursor.fetchone()[0]
            
            # Test BasketItems table
            cursor.execute("""
                SELECT COUNT(*) FROM BasketItems
            """)
            items_count = cursor.fetchone()[0]
            
            return jsonify({
                "success": True,
                "basket_count": basket_count,
                "items_count": items_count
            })
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/debug/check_products')
def debug_check_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check specific barcodes
        barcodes = ['646670523281', '6411402159403']
        results = {}
        
        for barcode in barcodes:
            cursor.execute("""
                SELECT [Product name], [Environmental score], [Carbon footprint 1kg]
                FROM [dbo].[sustainabite]
                WHERE Barcode = ?
            """, barcode)
            product = cursor.fetchone()
            results[barcode] = {
                'found': product is not None,
                'details': {
                    'name': product[0] if product else None,
                    'score': product[1] if product else None,
                    'footprint': product[2] if product else None
                } if product else None
            }
        
        # Also check basket items
        cursor.execute("SELECT BasketID FROM ShoppingBasket WHERE UserID = ?", session.get('user_id', 'anonymous-user'))
        basket_row = cursor.fetchone()
        
        if basket_row:
            basket_id = basket_row[0]
            cursor.execute("SELECT Barcode, Quantity FROM BasketItems WHERE BasketID = ?", basket_id)
            basket_items = cursor.fetchall()
            results['basket_items'] = [{'barcode': item[0], 'quantity': item[1]} for item in basket_items]
        else:
            results['basket_items'] = []
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)