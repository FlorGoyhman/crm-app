def get_gsheet_data(spreadsheet_name, sheet_name):
    """Obtiene datos de una pestaña de Google Sheets de forma segura, incluso si la fila 1 varía"""
    try:
        client = get_gsheet_client()
        sheet = client.open(spreadsheet_name).worksheet(sheet_name)
        
        # Traemos absolutamente todos los valores de la hoja como una lista de listas
        all_values = sheet.get_all_values()
        
        if not all_values:
            logger.warning(f"La pestaña '{sheet_name}' está completamente vacía de celdas.")
            return pd.DataFrame()
            
        # Tomamos la primera fila con datos como encabezado, y el resto como registros
        headers = all_values[0]
        rows = all_values[1:]
        
        # Si la primera fila vino vacía o con datos extraños, inventamos nombres temporales
        if not any(headers):
            df = pd.DataFrame(all_values)
        else:
            df = pd.DataFrame(rows, columns=headers)
            
        return df
    except Exception as e:
        logger.error(f"Error obteniendo datos de la pestaña {sheet_name} en el archivo {spreadsheet_name}: {e}")
        raise

def clean_dataframe_columns(df):
    """Limpia los nombres de las columnas para evitar espacios en blanco o problemas de formato"""
    if df is not None and not df.empty:
        df.columns = [str(c).strip().lower() for c in df.columns]
    return df
