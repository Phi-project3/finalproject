import os
import urllib
from flask import Flask, render_template
from sqlalchemy import create_engine, text

app = Flask(__name__)

# Set up the connection string from an environment variable or hardcode it for testing
raw_connection_string = os.environ.get('DATABASE_URL')
if raw_connection_string is None:
    raw_connection_string = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=tcp:your-server.database.windows.net,1433;"
        "Database=sustainabite-database;"
        "Uid=sustainabite-server-admin;"
        "Pwd={Qvs6YFz6AN$ekYvN};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/omg')
def page2():
    return render_template('omg.html')

@app.route('/winteriscoming')
def page3():
    return render_template('winteriscoming.html')

if __name__ == '__main__':
    app.run(debug=True)