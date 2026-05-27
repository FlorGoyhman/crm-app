import streamlit as st
from config import get_conn, insert_into_table
import logging

logger = logging.getLogger(__name__)

st.title("➕ Crear Cliente")

# --- VALIDACIÓN DE DATOS (Se mantiene tu lógica intacta) ---
def validar_cliente(nombre, domicilio, edad, numero):
    """Valida los datos del cliente"""
    errores = []
    
    if not nombre or not nombre.strip():
        errores.append("Nombre es obligatorio")
    if not numero or not numero.strip():
        errores.append("Número (ID) es obligatorio")
    if edad < 18 or edad > 120:
        errores.append("Edad debe estar entre 18 y 120 años")
    if len(nombre.strip()) < 3:
        errores.append("Nombre debe tener al menos 3 caracteres")
    
    return errores

# --- FORMULARIO CON RESETEO NATIVO ---
# Al usar clear_on_submit=True, Streamlit limpia los campos automáticamente al enviar sin romper el Session State
with st.form("formulario_clientes", clear_on_submit=True):
    
    # Inputs limpios sin depender de keys conflictivas en el session_state
    nombre = st.text_input("👤 Nombre", placeholder="Ej: Juan Pérez")
    domicilio = st.text_input("🏠 Domicilio", placeholder="Ej: Calle 123, Apt 5")
    edad = st.number_input("📅 Edad", min_value=0, max_value=120, step=1, value=18)
    numero = st.text_input("🔢 Número (ID)", placeholder="Ej: CLI-001")
    
    # El botón oficial de envío del Form
    guardar = st.form_submit_button("💾 Guardar Cliente", type="primary", use_container_width=True)

# --- PROCESAMIENTO AL DAR CLICK ---
if guardar:
    # Validar
    errores = validar_cliente(nombre, domicilio, edad, numero)
    
    if errores:
        st.error("❌ Errores en el formulario:")
        for error in errores:
            st.write(f"  • {error}")
    else:
        try:
            conn = get_conn()
            cursor = conn.cursor()
            
            # Verificar que no exista (Usa nuestro cursor simulado que devuelve None)
            cursor.execute(
                "SELECT * FROM Partners WHERE numero = ?",
                (numero.strip(),)
            )
            
            if cursor.fetchone():
                st.error(f"❌ Ya existe un cliente con ID '{numero}'")
            else:
                # Insertar simulado
                cursor.execute(
                    """
                    INSERT INTO Partners (nombre, domicilio, edad, numero)
                    VALUES (?, ?, ?, ?)
                    """,
                    (nombre.strip(), domicilio.strip(), int(edad), numero.strip())
                )
                
                # Cerramos conexiones seguras simuladas
                if hasattr(conn, 'commit'): conn.commit()
                if hasattr(conn, 'close'): conn.close()
                
                # Feedback positivo en pantalla
                st.success(f"✅ ¡Cliente '{nombre}' guardado correctamente!")
                logger.info(f"Cliente creado: {nombre} (ID: {numero})")
                
                # Forzamos el rerun para consolidar el formulario limpio
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error al guardar: {str(e)}")
            logger.error(f"Error guardando cliente: {e}")
