import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Gestión SIHO-A", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    u = st.text_input("Usuario")
    p = st.text_input("Clave", type="password")
    if st.button("INGRESAR"):
        if u == "adm" and p == "1234":
            st.session_state.autenticado = True
            st.rerun()
else:
    # CONEXIÓN DIRECTA
    conn = st.connection("gsheets", type=GSheetsConnection)

    st.title("🛡️ SIHO-A 2026")
    dias = (datetime.now().date() - datetime(2026, 1, 1).date()).days
    st.success(f"✅ {max(0, dias)} DÍAS SIN ACCIDENTES")

    with st.form("registro"):
        f = st.date_input("Fecha")
        ubi = st.selectbox("Ubicación", ["Base - Caracas", "Base - Anaco", "Troil-01"])
        act = st.text_input("Actividad")
        desc = st.text_area("Descripción")
        
        if st.form_submit_button("💾 GUARDAR"):
            try:
                # Leemos la hoja 'Datos'
                df_old = conn.read(worksheet="Datos", ttl=0)
                
                # Creamos la fila SOLO con las columnas básicas para probar conexión
                nueva_fila = pd.DataFrame([{
                    "Fecha": str(f),
                    "Centro de Costo": ubi,
                    "Actividad": act,
                    "Responsable": "adm",
                    "Descripción": desc
                }])
                
                # Intentamos actualizar
                df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                conn.update(worksheet="Datos", data=df_new)
                st.balloons()
                st.success("¡LO LOGRAMOS! Registro guardado.")
            except Exception as e:
                st.error(f"Error técnico: {e}")
                st.info("Asegúrate de que la pestaña se llame 'Datos' y que compartiste con el correo de servicio.")
