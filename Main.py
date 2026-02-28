import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE IMAGEN CORPORATIVA
st.set_page_config(page_title="SIHO-A TROIL PRO", layout="wide", initial_sidebar_state="collapsed")

# 2. ESTILO CSS PERSONALIZADO (AZUL Y NARANJA TROIL + FIRMA)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 12px; height: 90px; font-weight: bold; font-size: 18px;
        border: 3px solid #F39200; color: #004A99; background-color: white; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #004A99; color: white; border: 3px solid #F39200; }
    .header-troil {
        background-color: #004A99; padding: 15px; border-radius: 10px; color: white;
        text-align: center; border-bottom: 5px solid #F39200; margin-bottom: 20px;
    }
    .footer-signature {
        text-align: center; padding: 15px; font-size: 14px; color: #333;
        border-top: 2px solid #F39200; margin-top: 40px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Lógica de Sesión
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = "menu"

def mostrar_firma():
    st.markdown("<div class='footer-signature'>Desarrollado por: Ing. Mayerling Bellorin</div>", unsafe_allow_html=True)

# --- PANTALLA 1: ACCESO SEGURO (LOGIN) ---
if not st.session_state.autenticado:
    st.markdown("<div class='header-troil'><h1>🛡️ SISTEMA SIHO-A TROIL</h1><p>Ingreso de Personal Autorizado</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.container(border=True):
            user = st.text_input("Usuario")
            passw = st.text_input("Contraseña", type="password")
            if st.button("🔓 ENTRAR"):
                if user.lower() == "adm" and passw == "1234":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    mostrar_firma()

else:
    conn = st.connection("gsheets", type=GSheetsConnection)

    # --- PANTALLA 2: MENÚ DE MOSAICOS (PANEL DE CONTROL) ---
    if st.session_state.pantalla == "menu":
        st.markdown("<div class='header-troil'><h1>PANEL DE GESTIÓN SIHO-A</h1></div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝\n\nRegistrar Actividad"): st.session_state.pantalla = "formulario"
        with c2:
            if st.button("📊\n\nGráficos y Reportes"): st.session_state.pantalla = "reportes"
        
        if st.sidebar.button("🔒 Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()
        mostrar_firma()

    # --- PANTALLA 3: FORMULARIO INTEGRAL (DOTACIÓN, CERTIFICACIONES, FOTOS) ---
    elif st.session_state.pantalla == "formulario":
        st.markdown("<div class='header-troil'><h1>REGISTRO DE CAMPO</h1></div>", unsafe_allow_html=True)
        if st.button("⬅️ Volver al Menú"): st.session_state.pantalla = "menu"; st.rerun()

        with st.form("main_form", clear_on_submit=True):
            st.subheader("📍 Identificación")
            col_a, col_b = st.columns(2)
            with col_a:
                f = st.date_input("Fecha", datetime.now())
                act = st.selectbox("Actividad", ["Charla 5 min", "Divergencia", "Inspección", "Accidente", "Casi Suceso", "Observación"])
                loc = st.selectbox("Ubicación", ["Base - Anaco", "Base - Caracas", "Troil-01", "Pariaguán", "Morichal"])
            with col_b:
                sec = st.text_input("Sección / Área")
                responsable = st.text_input("Responsable", "Ing. Mayerling Bellorin")
                pers = st.selectbox("Personal", ["Propio", "Contratista", "Visitante"])

            st.divider()
            st.subheader("🛡️ Dotación y Certificaciones")
            col_c, col_d = st.columns(2)
            with col_c:
                dotacion = st.selectbox("Estatus Dotación/EPP", ["Completa", "Incompleta", "N/A"])
                cert = st.text_input("Certificaciones Observadas")
            with col_d:
                est_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
                foto = st.file_uploader("📸 Evidencia Fotográfica (Charlas/Hallazgos)", type=['jpg', 'png', 'jpeg'])

            st.divider()
            desc = st.text_area("Descripción detallada")
            accion = st.text_area("Acción inmediata tomada")

            if st.form_submit_button("💾 GUARDAR Y SINCRONIZAR"):
                try:
                    df_actual = conn.read(worksheet="Datos", ttl=0)
                    nombre_foto = foto.name if foto else "Sin foto"
                    nueva_fila = pd.DataFrame([{
                        "Fecha": str(f), "Centro de Costo": loc, "Actividad": act, 
                        "Responsable": responsable, "Sección": sec, "Personal": pers,
                        "Dotación": dotacion, "Certificación": cert, "Estatus Cert": est_cert,
                        "Descripción": desc, "Acción": accion, "Foto": nombre_foto
                    }])
                    df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_final)
                    st.balloons(); st.success("✅ Datos sincronizados con éxito.")
                except Exception as e:
                    st.error(f"Error: {e}. Revisa que la hoja se llame 'Datos'.")
        mostrar_firma()

    # --- PANTALLA 4: REPORTES Y GRÁFICOS ---
    elif st.session_state.pantalla == "reportes":
        st.markdown("<div class='header-troil'><h1>INDICADORES DE GESTIÓN</h1></div>", unsafe_allow_html=True)
        if st.button("⬅️ Volver al Menú"): st.session_state.pantalla = "menu"; st.rerun()

        try:
            df_rep = conn.read(worksheet="Datos", ttl=0)
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("📊 Por Actividad")
                st.plotly_chart(px.bar(df_rep, x='Actividad', color_discrete_sequence=['#004A99']), use_container_width=True)
            with c2:
                st.subheader("📍 Por Ubicación")
                st.plotly_chart(px.pie(df_rep, names='Centro de Costo', hole=0.4, color_discrete_sequence=['#004A99', '#F39200']), use_container_width=True)
            st.subheader("📋 Bitácora General")
            st.dataframe(df_rep, use_container_width=True)
        except:
            st.warning("No hay datos para graficar aún.")
        mostrar_firma()
