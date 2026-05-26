import pyodbc
import pandas as pd

def get_conn():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=DESKTOP-D5LVCOT\\SQLEXPRESS;"
        "DATABASE=BaseFlor;"
        "Trusted_Connection=yes;"
    )
    return conn

def query(sql):
    conn = get_conn()
    df = pd.read_sql(sql, conn)
    conn.close()
    return df