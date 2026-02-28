import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px # Librería para los gráficos
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SIHO-A TROIL", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTILO CSS (TROIL: Azul y Naranja)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 15px; height: 90px; font-weight: bold; font-size: 18px;
        border: 3px solid #F39200; color: #004A99; background-color: white; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #004A99; color: white; border: 3px solid white; }
    .header-troil {
        background-color: #004A99; padding: 20px; border-radius: 10px; color: white;
        text-align: center; border-bottom: 5px solid #F39200; margin-bottom: 25px;
    }
    .footer-signature {
        text-align: center; padding: 20px; font-size: 14px; color: #555;
        border-top: 1px solid #ddd; margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# Lógica de Sesión
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = "menu"

def mostrar_firma():
    st.markdown("<div class='footer-signature'>Desarrollado por: <b>Ing. Mayerling Bellorin</b></div>", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<div class='header-troil'><h1>🛡️ SIHO-A TROIL</h1><p>Ingreso Seguro</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.button("INGRESAR"):
                if u.lower() == "adm" and p == "1234":
                    st.session_state.autenticado = True
                    st.rerun()
    mostrar_firma()

else:
    conn = st.connection("gsheets", type=GSheetsConnection)

    # --- MENÚ PRINCIPAL ---
    if st.session_state.pantalla == "menu":
        st.markdown("<div class='header-troil'><h1>Panel de Control SIHO-A</h1></div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝\n\nRegistrar Actividad"): st.session_state.pantalla = "registro"
        with c2:
            if st.button("📊\n\nGráficos y Reportes"): st.session_state.pantalla = "reportes"
        
        if st.sidebar.button("🔒 Salir"):
            st.session_state.autenticado = False
            st.rerun()
        mostrar_firma()

    # --- PANTALLA DE REGISTRO ---
    elif st.session_state.pantalla == "registro":
        st.markdown("<div class='header-troil'><h1>Nuevo Registro de Seguridad</h1></div>", unsafe_allow_html=True)
        if st.button("⬅️ Menú"): st.session_state.pantalla = "menu"; st.rerun()

        with st.form("form_registro"):
            col_a, col_b = st.columns(2)
            with col_a:
                f = st.date_input("Fecha", datetime.now())
                loc = st.selectbox("Ubicación", ["Base - Anaco", "Base - Caracas", "Troil-01", "Pariaguán"])
            with col_b:
                act = st.selectbox("Tipo de Actividad", ["Charla 5 min", "Divergencia", "Inspección", "Accidente"])
                resp = st.text_input("Responsable", "Ing. Mayerling Bellorin")

            desc = st.text_area("Descripción / Observaciones")
            
            # SECCIÓN DE FOTO (Solo si es Charla)
            foto_nombre = "Sin foto"
            if act == "Charla 5 min":
                st.info("📸 Registro de asistencia para Charlas")
                foto = st.file_uploader("Cargar evidencia de charla", type=['jpg', 'png', 'jpeg'])
                if foto: foto_nombre = foto.name

            if st.form_submit_button("💾 GUARDAR"):
                try:
                    df_old = conn.read(worksheet="Datos", ttl=0)
                    nueva_fila = pd.DataFrame([{"Fecha": str(f), "Centro de Costo": loc, "Actividad": act, "Responsable": resp, "Descripción": desc, "Foto": foto_nombre}])
                    df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_new)
                    st.balloons(); st.success("✅ ¡Guardado!")
                except Exception as e: st.error(f"Error: {e}")
        mostrar_firma()

    # --- PANTALLA DE REPORTES Y GRÁFICOS ---
    elif st.session_state.pantalla == "reportes":
        st.markdown("<div class='header-troil'><h1>Estadísticas de Gestión</h1></div>", unsafe_allow_html=True)
        if st.button("⬅️ Menú"): st.session_state.pantalla = "menu"; st.rerun()

        try:
            df = conn.read(worksheet="Datos", ttl=0)
            
            # Gráfico de Barras por Actividad
            st.subheader("📊 Frecuencia por Actividad")
            fig_act = px.bar(df, x='Actividad', color='Actividad', color_discrete_sequence=['#004A99', '#F39200'])
            st.plotly_chart(fig_act, use_container_width=True)

            # Gráfico de Torta por Ubicación
            st.subheader("📍 Registros por Sede")
            fig_loc = px.pie(df, names='Centro de Costo', hole=0.3, color_discrete_sequence=['#004A99', '#F39200', '#AABBCC'])
            st.plotly_chart(fig_loc, use_container_width=True)

            st.subheader("📑 Datos Consolidados")
            st.dataframe(df, use_container_width=True)
            
        except Exception as e: st.error("Aún no hay datos para graficar.")
        mostrar_firma()
