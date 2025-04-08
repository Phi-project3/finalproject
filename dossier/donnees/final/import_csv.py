# CSV importation to our Azure Database
import pandas as pd
from sqlalchemy import create_engine
import urllib

# In the Database > Settings > Connection strings > ODBC (don’t forget the password)
raw_connection_string = "Driver={ODBC Driver 18 for SQL Server};Server=tcp:sustainabite-server.database.windows.net,1433;Database=sustainabite-database;Uid=sustainabite-server-admin;Pwd={Qvs6YFz6AN$ekYvN};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
params = urllib.parse.quote_plus(raw_connection_string)

engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

df = pd.read_csv('https://raw.githubusercontent.com/Phi-project3/finalproject/refs/heads/main/dossier/donnees/final/sustainabite.csv')

# if_exists="replace" creates the table and replaces it if it exists
df.to_sql("sustainabite", con=engine, if_exists="replace", index=False)