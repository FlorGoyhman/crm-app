def get_gsheet_data(spreadsheet_name, sheet_name):
    """Obtiene datos de una pestaña de Google Sheets convirtiendo celdas puras a DataFrame"""
    try:
        client = get_gsheet_client()
        sheet = client.open(spreadsheet_name).worksheet(sheet_name)
        
        # Traemos todas las celdas de la hoja como una lista de listas
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) == 0:
            logger.warning(f"La pestaña '{sheet_name}' está vacía.")
            return pd.DataFrame()
            
        # La primera fila (Fila 1) contiene los encabezados reales
        headers = [str(h).strip() for h in all_values[0]]
        rows = all_values[1:]
        
        # Creamos el DataFrame estructurado correctamente
        df = pd.DataFrame(rows, columns=headers)
        return df
        
    except Exception as e:
        # Usamos print como plan de respaldo por si el logger no está bien inicializado en config
        print(f"Error crítico leyendo {sheet_name}: {str(e)}")
        import logging
        logging.getLogger(__name__).error(f"Error en get_gsheet_data: {e}")
        return pd.DataFrame()
