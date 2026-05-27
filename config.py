import pandas as pd
import streamlit as st

# --- INICIALIZACIÓN DE LA BASE DE DATOS SIMULADA ---
if "bd_partners" not in st.session_state:
    # Cargamos tus 5 clientes iniciales por defecto
    st.session_state["bd_partners"] = [
        {"partner_id": 1, "nombre": "Distribuidora Alvear", "domicilio": "Av. Alvear 123", "edad": 45, "numero": "CLI-001"},
        {"partner_id": 2, "nombre": "Logística Sur S.A.", "domicilio": "Ruta 3 Km 10", "edad": 38, "numero": "CLI-002"},
        {"partner_id": 3, "nombre": "Comercializadora del Plata", "domicilio": "Florida 456", "edad": 52, "numero": "CLI-003"},
        {"partner_id": 4, "nombre": "Mundo Retail", "domicilio": "Av. Santa Fe 2200", "edad": 29, "numero": "CLI-004"},
        {"partner_id": 5, "nombre": "Global Trading Inc", "domicilio": "🌍 Comercio Exterior", "edad": 41, "numero": "CLI-005"}
    ]

def query(sql_expression):
    sql_expression_clean = sql_expression.strip().lower()
    
    # Si la pestaña Clientes pide la tabla de Partners:
    if "from partners" in sql_expression_clean:
        # Devolvemos la lista dinámica de la memoria global convertida en DataFrame
        return pd.DataFrame(st.session_state["bd_partners"])
        
    elif "from orders" in sql_expression_clean:
        return pd.DataFrame({
            "order_id": [101, 102, 103, 104, 105],
            "product": ["Laptop Core i7", "Mouse Inalámbrico", "Monitor 24'", "Teclado Mecánico", "Impresora Láser"],
            "amount": [1200.50, 25.00, 300.75, 70.00, 180.00]
        })
    return pd.DataFrame()

def clean_dataframe_columns(df):
    if df is not None and not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df

# --- CURSOR INTELIGENTE PARA AGREGAR DATOS REALMENTE ---
class CursorSimulado:
    def execute(self, query_string, params=None):
        query_clean = query_string.strip().lower()
        
        # Si la pestaña Acciones está queriendo INSERTAR un cliente:
        if "insert into partners" in query_clean and params:
            nuevo_id = len(st.session_state["bd_partners"]) + 1
            nuevo_cliente = {
                "partner_id": nuevo_id,
                "nombre": params[0],
                "domicilio": params[1],
                "edad": params[2],
                "numero": params[3]
            }
            # ¡Lo guardamos en la memoria global compartida!
            st.session_state["bd_partners"].append(nuevo_cliente)
        return True
    
    def fetchone(self): return None
    def fetchall(self): return []
    def commit(self): pass
    def close(self): pass

class ConexionSimulada:
    def cursor(self): return CursorSimulado()
    def commit(self): pass
    def close(self): pass

def get_conn():
    return ConexionSimulada()
