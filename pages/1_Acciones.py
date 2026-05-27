import streamlit as st
from config import get_conn, insert_into_table
import logging

logger = logging.getLogger(__name__)

st.title("➕ Crear Cliente")

# --- INICIALIZAR SESSION STATE ---
if "nombre_input" not in st.session_state:
    st.session_state.nombre_input = ""
if "domicilio_input" not in st.session_state:
    st.session_state.domicilio_input = ""
if "edad_input" not in st.session_state:
    st.session_state.edad_input = 0
if "numero_input" not in st.session_state:
    st.session_state.numero_input = ""

# --- FORM CON INPUTS ---
nombre = st.text_input("👤 Nombre", key="nombre_input", placeholder="Ej: Juan Pérez")
domicilio = st.text_input("🏠 Domicilio", key="domicilio_input", placeholder="Ej: Calle 123, Apt 5")
edad = st.number_input("📅 Edad", min_value=0, max_value=120, step=1, key="edad_input")
numero = st.text_input("🔢 Número (ID)", key="numero_input", placeholder="Ej: CLI-001")

# --- VALIDACIÓN DE DATOS ---
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

# --- BOTÓN GUARDAR ---
if st.button("💾 Guardar Cliente", type="primary", use_container_width=True):
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
            
            # Verificar que no exista
            cursor.execute(
                "SELECT * FROM Partners WHERE numero = ?",
                (numero.strip(),)
            )
            
            if cursor.fetchone():
                st.error(f"❌ Ya existe un cliente con ID '{numero}'")
            else:
                # Insertar
                cursor.execute(
                    """
                    INSERT INTO Partners (nombre, domicilio, edad, numero)
                    VALUES (?, ?, ?, ?)
                    """,
                    (nombre.strip(), domicilio.strip(), int(edad), numero.strip())
                )
                conn.commit()
                conn.close()
                
                # Feedback positivo
                st.success(f"✅ ¡Cliente '{nombre}' guardado correctamente!")
                logger.info(f"Cliente creado: {nombre} (ID: {numero})")
                
                # Limpiar formulario
                st.session_state.nombre_input = ""
                st.session_state.domicilio_input = ""
                st.session_state.edad_input = 0
                st.session_state.numero_input = ""
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error al guardar: {str(e)}")
            logger.error(f"Error guardando cliente: {e}")
