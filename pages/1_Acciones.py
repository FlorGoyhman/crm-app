import streamlit as st
from config import get_conn
import logging

logger = logging.getLogger(__name__)

st.title("➕ Crear Cliente")

# --- VALIDACIÓN DE DATOS (Tu lógica intacta) ---
def validar_cliente(nombre, domicilio, edad, numero):
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

# --- FORMULARIO CONTENIDO ---
with st.form("formulario_clientes", clear_on_submit=True):
    nombre = st.text_input("👤 Nombre", placeholder="Ej: Juan Pérez")
    domicilio = st.text_input("🏠 Domicilio", placeholder="Ej: Calle 123, Apt 5")
    edad = st.number_input("📅 Edad", min_value=0, max_value=120, step=1, value=18)
    numero = st.text_input("🔢 Número (ID)", placeholder="Ej: CLI-001")
    
    guardar = st.form_submit_button("💾 Guardar Cliente", type="primary", use_container_width=True)

    # --- LA LÓGICA TIENE QUE ESTAR ACÁ ADENTRO PARA QUE EL BOTÓN RESPONDA ---
    if guardar:
        errores = validar_cliente(nombre, domicilio, edad, numero)
        
        if errores:
            st.error("❌ Errores en el formulario:")
            for error in errores:
                st.write(f"  • {error}")
        else:
            try:
                conn = get_conn()
                cursor = conn.cursor()
                
                # Verificar con nuestro simulador
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
                    
                    if hasattr(conn, 'commit'): conn.commit()
                    if hasattr(conn, 'close'): conn.close()
                    
                    # Guardamos el mensaje de éxito en el session_state antes del rerun
                    st.session_state["mensaje_exito"] = f"✅ ¡Cliente '{nombre}' guardado correctamente!"
                    logger.info(f"Cliente creado: {nombre} (ID: {numero})")
                    
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error al guardar: {str(e)}")

# --- MOSTRAR EL CARTEL VERDE DESPUÉS DE REINICIAR LA PANTALLA ---
if "mensaje_exito" in st.session_state:
    st.success(st.session_state["mensaje_exito"])
    del st.session_state["mensaje_exito"] # Lo borramos para que no aparezca eternamente
