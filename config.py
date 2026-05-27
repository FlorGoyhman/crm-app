import pandas as pd

def query(sql_expression):
    """
    Simula la conexión a SQL Server devolviendo DataFrames hardcodeados
    según la consulta que le pida la página para evitar errores de red.
    """
    # Pasamos la consulta a minúsculas para comparar fácil
    sql_expression_clean = sql_expression.strip().lower()
    
    # 👤 SI LA PÁGINA PIDE LOS CLIENTES / PARTNERS:
    if "from partners" in sql_expression_clean:
        datos_partners = {
            "partner_id": [1, 2, 3, 4, 5],
            "name": ["Distribuidora Alvear", "Logística Sur S.A.", "Comercializadora del Plata", "Mundo Retail", "Global Trading Inc"],
            "country": ["Argentina", "Argentina", "Uruguay", "Chile", "Brasil"],
            "status": ["Activo", "Activo", "Inactivo", "Activo", "Pendiente"],
            "contact_email": ["info@alvear.com", "contacto@logisur.com", "ventas@delplata.uy", "retail@mundo.cl", "trading@global.br"]
        }
        return pd.DataFrame(datos_partners)
        
    # 📦 SI LA PÁGINA PIDE LAS ÓRDENES:
    elif "from orders" in sql_expression_clean:
        datos_orders = {
            "order_id": [101, 102, 103, 104, 105, 106, 107],
            "partner_id": [1, 1, 2, 4, 5, 3, 2],
            "product": ["Laptop Core i7", "Mouse Inalámbrico", "Monitor 24' LED", "Teclado Mecánico", "Impresora Láser", "Silla Ergonómica", "Webcam HD"],
            "amount": [1200.50, 25.00, 300.75, 70.00, 180.00, 250.00, 45.00],
            "status": ["Entregado", "Entregado", "En Proceso", "Entregado", "Cancelado", "En Proceso", "Entregado"],
            "date": ["2026-05-10", "2026-05-11", "2026-05-12", "2026-05-14", "2026-05-15", "2026-05-16", "2026-05-17"]
        }
        return pd.DataFrame(datos_orders)
        
    # Por si se pide otra cosa, devolvemos una estructura vacía segura
    return pd.DataFrame()

def clean_dataframe_columns(df):
    """Limpia los espacios y pasa a minúsculas los nombres de las columnas"""
    if df is not None and not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df
