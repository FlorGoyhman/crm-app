import pandas as pd
import pyodbc
import gspread

from oauth2client.service_account import ServiceAccountCredentials


# =========================
# GOOGLE SHEETS
# =========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    r"C:\Users\florg\Downloads\CPythonCRM\credenciales.json",
    scope
)

client = gspread.authorize(creds)

print("GOOGLE OK")


# =========================
# ABRIR SHEET
# =========================

sheet = client.open("Python")

print("SHEET OK")


# =========================
# LEER PRODUCTS
# =========================

products_tab = sheet.worksheet("Products")

products_data = products_tab.get_all_records()

df_products = pd.DataFrame(products_data)

print(df_products.head())


# =========================
# LEER PAYMENTS
# =========================

payments_tab = sheet.worksheet("Payments")

payments_data = payments_tab.get_all_records()

df_payments = pd.DataFrame(payments_data)

print(df_payments.head())


# =========================
# SQL SERVER
# =========================

conn = pyodbc.connect(
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=DESKTOP-D5LVCOT\SQLEXPRESS;"
    r"DATABASE=BaseFlor;"
    r"Trusted_Connection=yes;"
)

cursor = conn.cursor()

print("SQL OK")


# =========================
# INSERT PRODUCTS
# =========================

for index, row in df_products.iterrows():

    query = """
    INSERT INTO products
    (
        product_id,
        name,
        category,
        price,
        stock,
        Partner_id
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        query,
        (
            row["product_id"],
            row["name"],
            row["category"],
            row["price"],
            row["stock"],
            row["Partner_id"]
        )
    )

conn.commit()

print("PRODUCTS IMPORTADOS")


# =========================
# INSERT PAYMENTS
# =========================

for index, row in df_payments.iterrows():

    query = """
    INSERT INTO payments
    (
        payment_id,
        order_id,
        method,
        amount,
        status,
        date,
        Partner_id
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        query,
        (
            row["payment_id"],
            row["order_id"],
            row["method"],
            row["amount"],
            row["status"],
            row["date"],
            row["Partner_id"]
        )
    )

conn.commit()

print("PAYMENTS IMPORTADOS")


# =========================
# CERRAR
# =========================

cursor.close()
conn.close()

print("FIN")
