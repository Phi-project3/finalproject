import os
import urllib
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text


app = Flask(__name__)

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

@app.route('/scan')
def scan():
    return render_template('barcode_scan.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/about')
def about():
    return render_template('about.html')

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

@app.route('/teamphi')
def page3():
    return render_template('winteriscoming.html')

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

@app.route('/basket')
def basket_page():
    return render_template('basket.html')

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

if __name__ == '__main__':
    app.run(debug=True)