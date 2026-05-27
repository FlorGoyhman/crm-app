def get_gsheet_data(spreadsheet_name, sheet_name):
    """Obtiene datos de una pestaña específica de Google Sheets y los devuelve como un DataFrame"""
    try:
        client = get_gsheet_client()
        # Abre el archivo de Google Sheets por su nombre
        sheet = client.open(spreadsheet_name).worksheet(sheet_name)
        # Trae todos los registros de la pestaña
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error obteniendo datos de la pestaña {sheet_name} en el archivo {spreadsheet_name}: {e}")
        raise

def clean_dataframe_columns(df):
    """Limpia los nombres de las columnas para evitar espacios en blanco o problemas de formato"""
    if df is not None and not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df
