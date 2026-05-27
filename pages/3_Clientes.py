import pandas as pd
import streamlit as st
from config import get_conn, query
from gsheets import get_gsheet
from utils.filters import (
    clean_dataframe_columns,
    create_partner_filter,
    apply_partner_filter,
    create_status_filter,
    apply_status_filter
)
import logging

logger = logging.getLogger(__name__)

# --- CACHED LOADERS ---
@st.cache_data(ttl=300)
def load_partners():
    try:
        return query("SELECT * FROM Partners")
    except Exception as e:
        logger.error(f"Error cargando Partners: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_orders():
    try:
        return query("SELECT * FROM Orders")
    except Exception as e:
        logger.error(f"Error cargando Orders: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_payments():
    try:
        return get_gsheet("Python", "Payments")
    except Exception as e:
        logger.error(f"Error cargando Payments desde GSheet: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_products():
    try:
        return get_gsheet("Python", "Products")
    except Exception as e:
        logger.error(f"Error cargando Products desde GSheet: {e}")
        return pd.DataFrame()

st.title("🧑 Clientes")

try:
    # Cargar datos
    df_partners = load_partners()
    df_orders = load_orders()
    df_payments = load_payments()
    df_products = load_products()
    
    # Limpiar columnas
    df_partners = clean_dataframe_columns(df_partners)
    df_orders = clean_dataframe_columns(df_orders)
    df_payments = clean_dataframe_columns(df_payments)
    df_products = clean_dataframe_columns(df_products)
    
    # --- TABLA PRINCIPAL ---
    st.subheader("📊 Datos Actuales de Clientes")
    st.dataframe(df_partners, width='stretch')
    
    # --- BOTÓN LIMPIAR DATOS ---
    st.markdown("---")
    if st.button("🧹 Limpiar Duplicados y Nulls", type="secondary"):
        if st.checkbox("✅ Confirmar eliminación de duplicados", value=False):
            try:
                # Copiar para comparación
                df_original = df_partners.copy()
                
                # Limpiar espacios (CORREGIDO: Convierte a texto de forma segura primero)
                for col in df_partners.columns:
                    df_partners[col] = df_partners[col].astype(str).str.strip()
                
                # Convertir strings vacíos a nulls
                df_partners = df_partners.replace(
                    ["", " ", "null", "NULL", "None"],
                    pd.NA
                )
                
                # Eliminar nulls y duplicados
                df_clean = df_partners.dropna().drop_duplicates()
                
                filas_eliminadas = len(df_original) - len(df_clean)
                st.info(f"Se eliminaron {filas_eliminadas} filas duplicadas/vacías")
                
                # Actualizar SQL (con manejo seguro)
                conn = None
                try:
                    conn = get_conn()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Partners")
                    conn.commit()

                    for _, row in df_clean.iterrows():
                        try:
                            cursor.execute(
                                "INSERT INTO Partners (nombre, domicilio, edad, numero) VALUES (?, ?, ?, ?)",
                                (row.get('nombre'), row.get('domicilio'), row.get('edad'), row.get('numero'))
                            )
                        except Exception as e:
                            logger.warning(f"Fila omitida al insertar Partners: {e}")

                    conn.commit()
                finally:
                    if conn:
                        conn.close()
                
                st.success("✅ Tabla limpiada exitosamente")
                logger.info(f"Tabla limpiada: {filas_eliminadas} filas eliminadas")
                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error al limpiar: {str(e)}")
                logger.error(f"Error limpiando tabla: {e}")
    
    # --- ANÁLISIS CON FILTROS ---
    st.markdown("---")
    st.subheader("📈 Análisis de Pagos y Productos")
    
    # Filtro cliente
    cliente_seleccionado = create_partner_filter(df_partners, column_name="nombre")
    
    # --- TABS ---
    tab1, tab2 = st.tabs(["💰 Pagos", "📦 Productos"])
    
    with tab1:
        if not df_payments.empty and "partner_id" in df_payments.columns:
            # Merge
            df_pago_completo = pd.merge(
                df_payments,
                df_orders,
                on="partner_id",
                how="left"
            )
            df_pago_completo = pd.merge(
                df_pago_completo,
                df_partners,
                left_on="partner_id",
                right_on="numero",
                how="left"
            )
            
            # Aplicar filtros
            df_pago_completo = apply_partner_filter(
                df_pago_completo,
                cliente_seleccionado,
                df_partners
            )
            
            if "status" in df_pago_completo.columns:
                status = create_status_filter(
                    df_pago_completo,
                    column="status",
                    key="payment_status",
                    label="Filtrar estado de pago"
                )
                df_pago_completo = apply_status_filter(
                    df_pago_completo,
                    status,
                    column="status"
                )
            
            st.dataframe(df_pago_completo, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos de pagos disponibles")
    
    with tab2:
        if not df_products.empty and "partner_id" in df_products.columns:
            # Merge
            df_prod_completo = pd.merge(
                df_products,
                df_orders,
                on="partner_id",
                how="left"
            )
            df_prod_completo = pd.merge(
                df_prod_completo,
                df_partners,
                left_on="partner_id",
                right_on="numero",
                how="left"
            )
            
            # Aplicar filtros
            df_prod_completo = apply_partner_filter(
                df_prod_completo,
                cliente_seleccionado,
                df_partners
            )
            
            if "status" in df_prod_completo.columns:
                status = create_status_filter(
                    df_prod_completo,
                    column="status",
                    key="product_status",
                    label="Filtrar estado de producto"
                )
                df_prod_completo = apply_status_filter(
                    df_prod_completo,
                    status,
                    column="status"
                )
            
            st.dataframe(df_prod_completo, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos de productos disponibles")

except Exception as e:
    st.error(f"❌ Error al cargar clientes: {str(e)}")
    logger.error(f"Error en página clientes: {e}")
