import os
import urllib
from flask import Flask, render_template, request
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
def query_soups():
    query = text("SELECT * FROM [dbo].[my_table] WHERE pnns_groups_2 = :group")
    with engine.connect() as conn:
        result = conn.execute(query, {"group": "Chocolate products"})
        # Convert each row to a dictionary using its _mapping attribute
        records = [dict(row._mapping) for row in result.fetchall()]
    return render_template('results.html', records=records)


@app.route('/teamphi')
def page3():
    return render_template('winteriscoming.html')

if __name__ == '__main__':
    app.run(debug=True)