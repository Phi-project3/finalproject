import os
import urllib
from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

app = Flask(__name__)

# Set up the connection string from an environment variable or hardcode it for testing
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

# URL-encode and create the engine
params = urllib.parse.quote_plus(raw_connection_string)
engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query-soups')
def query_soups():
    query = text("SELECT * FROM [dbo].[my_table] WHERE pnns_groups_2 = :group")
    with engine.connect() as conn:
        result = conn.execute(query, {"group": "Soups"})
        # Convert each row to a dictionary using its _mapping attribute
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form.get('search_term')
        # Use a parameterized query with LIKE operator:
        query = text("SELECT * FROM [dbo].[my_table] WHERE product_name LIKE :term")
        with engine.connect() as conn:
            result = conn.execute(query, {"term": f"%{search_term}%"})
            records = [dict(row._mapping) for row in result.fetchall()]
        return render_template('search_results.html', records=records, search_term=search_term)
    # For GET requests, simply show the search form
    return render_template('search.html')

@app.route('/product/<code>')
def product_details(code):
    query = text("SELECT * FROM [dbo].[my_table] WHERE code = :code")
    with engine.connect() as conn:
        result = conn.execute(query, {"code": code})
        product = result.fetchone()

        # Convert the row to a dictionary if a product is found
        if product:
            product = dict(product._mapping)
        else:
            product = None

    return render_template('product_details.html', product=product)

@app.route('/omg')
def page2():
    return render_template('omg.html')

@app.route('/winteriscoming')
def page3():
    return render_template('winteriscoming.html')

if __name__ == '__main__':
    app.run(debug=True)