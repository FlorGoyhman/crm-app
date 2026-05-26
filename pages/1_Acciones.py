import streamlit as st
from config import get_conn

st.title("➕ Crear Cliente")

# INPUTS
nombre = st.text_input("Nombre")
domicilio = st.text_input("Domicilio")
edad = st.number_input("Edad", min_value=0, step=1)
numero = st.text_input("Número")

# BOTÓN
if st.button("Guardar"):

    if nombre.strip() == "":
        st.warning("El nombre es obligatorio")
    else:
        try:
            conn = get_conn()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Partners (nombre, domicilio, edad, numero)
                VALUES (?, ?, ?, ?)
            """, nombre, domicilio, edad, numero)

            conn.commit()
            conn.close()

            st.success("Cliente guardado correctamente")
            st.rerun()

        except Exception as e:
            st.error(f"Error al guardar: {e}")