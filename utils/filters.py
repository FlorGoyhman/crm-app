import pandas as pd
import streamlit as st

def create_partner_filter(df_partners, column_name="nombre"):
    """
    Crea un selector de partner
    
    Args:
        df_partners: DataFrame de partners
        column_name: Nombre de la columna a mostrar
    
    Returns:
        str: Nombre del partner seleccionado
    """
    if df_partners.empty or column_name not in df_partners.columns:
        st.warning(f"No se encontró columna '{column_name}'")
        return "Todos"
    
    lista = ["Todos"] + sorted(
        df_partners[column_name].dropna().unique().tolist()
    )
    return st.selectbox("👤 Filtrar por Cliente", lista)

def apply_partner_filter(df, partner_name, df_partners, merge_column="numero"):
    """
    Aplica filtro de partner al dataframe
    
    Args:
        df: DataFrame a filtrar
        partner_name: Nombre del partner seleccionado
        df_partners: DataFrame de partners para búsqueda
        merge_column: Columna para relacionar
    
    Returns:
        DataFrame filtrado
    """
    if partner_name == "Todos":
        return df
    
    if "nombre" not in df_partners.columns or merge_column not in df_partners.columns:
        return df
    
    partner_id = df_partners[df_partners["nombre"] == partner_name][
        merge_column
    ].values
    
    if len(partner_id) > 0 and "partner_id" in df.columns:
        return df[df["partner_id"].astype(str).str.strip() == str(partner_id[0])]
    
    return df

def create_status_filter(df, column="status", key=None, label="Filtrar estado"):
    """
    Crea un selector de status
    
    Args:
        df: DataFrame para obtener valores únicos
        column: Nombre de la columna de estado
        key: Key único para Streamlit
        label: Etiqueta del selector
    
    Returns:
        str: Estado seleccionado
    """
    if df.empty or column not in df.columns:
        return "Todos"
    
    lista = ["Todos"] + sorted(
        df[column].dropna().unique().tolist()
    )
    return st.selectbox(label, lista, key=key)

def apply_status_filter(df, status, column="status"):
    """
    Aplica filtro de status al dataframe
    
    Args:
        df: DataFrame a filtrar
        status: Status seleccionado
        column: Nombre de la columna de estado
    
    Returns:
        DataFrame filtrado
    """
    if status == "Todos" or column not in df.columns:
        return df
    
    return df[df[column] == status]

def clean_dataframe_columns(df):
    """
    Limpia nombres de columnas (minúsculas y espacios)
    
    Args:
        df: DataFrame a limpiar
    
    Returns:
        DataFrame con columnas limpias
    """
    df.columns = df.columns.str.lower().str.strip()
    return df
