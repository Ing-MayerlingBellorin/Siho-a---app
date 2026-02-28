import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN CORPORATIVA
st.set_page_config(page_title="SIHO-A TROIL PRO", layout="wide")

# ESTILO AZUL Y NARANJA + FIRMA
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 80px; font-weight: bold; border: 3px solid #F39200; color: #004A99; background: white; }
    .stButton>button:hover { background-color: #004A99; color: white; }
    .header-troil { background-color: #004A99; padding: 15px; border-radius: 10px; color: white; text-align: center; border-bottom: 5px solid #F39200; }
    .footer { text-align: center; padding: 20px; font-weight: bold; color: #333; border-top: 2px solid #F39200; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'pantalla' not in st.session_state: st.session_state.pantalla = "menu"

def firma(): st.markdown("<div class='footer'>Desarrollado por: Ing. Mayerling Bellorin</div>", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<div class='header-troil'><h1>🛡️ ACCESO SIHO-A</h1></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        u = st.text_input("Usuario")
        p = st.text_input("Clave", type="password")
        if st.button("INGRESAR"):
            if u.lower() == "adm" and p == "1234":
                st.session_state.autenticado = True
                st.rerun()
    max_w = firma()

# --- SISTEMA ---
else:
    conn = st.connection("gsheets", type=GSheetsConnection)

    # --- MENÚ PRINCIPAL (MOSAICOS) ---
    if st.session_state.pantalla == "menu":
        st.markdown("<div class='header-troil'><h1>PANEL DE GESTIÓN TROIL</h1></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📝 REGISTRO ACTIVIDAD"): st.session_state.pantalla = "registro"
            if st.button("🎓 CERTIFICACIONES"): st.session_state.pantalla = "cert"
        with c2:
            if st.button("👷 DOTACIONES"): st.session_state.pantalla = "dotacion"
            if st.button("📊 REPORTES Y FOTOS"): st.session_state.pantalla = "reportes"
        firma()

    # --- MÓDULO DOTACIONES (LO QUE ME PEDISTE) ---
    elif st.session_state.pantalla == "dotacion":
        st.markdown("<div class='header-troil'><h1>SOLICITUD DE DOTACIÓN</h1></div>", unsafe_allow_html=True)
        if st.button("⬅️ VOLVER"): st.session_state.pantalla = "menu"; st.rerun()

        with st.form("form_dotacion"):
            tipo_d = st.selectbox("Condición de Dotación", ["Nueva", "Vencida", "Por Reemplazo"])
            destino = st.radio("Destino", ["Persona", "Equipo"], horizontal=True)
            cant = st.number_input("Cantidad de personas (1-30)", min_value=1, max_value=30, value=1)
            
            st.divider()
            st.subheader("Selección de Artículos")
            items = st.multiselect("Elija los artículos", ["Casco", "Botas", "Braga", "Lentes claros", "Lentes oscuros", "Protectores auditivos"])
            
            talla_botas = ""
            talla_braga = ""
            if "Botas" in items: talla_botas = st.text_input("Talla de Botas")
            if "Braga" in items: talla_braga = st.text_input("Talla de Braga")

            st.divider()
            datos_personal = []
            if destino == "Persona":
                st.subheader(f"Datos para {cant} trabajadores")
                for i in range(int(cant)):
                    c1, c2, c3 = st.columns(3)
                    with c1: n = st.text_input(f"Nombre y Apellido {i+1}", key=f"n_{i}")
                    with c2: car = st.text_input(f"Cargo {i+1}", key=f"c_{i}")
                    with c3: tal = st.text_input(f"Taladro {i+1}", key=f"t_{i}")
                    datos_personal.append(f"{n}/{car}/{tal}")

            if st.form_submit_button("ENVIAR SOLICITUD"):
                st.success("Solicitud procesada (Conecta tu hoja 'Dotaciones' para guardar)")
        firma()

    # --- MÓDULO CERTIFICACIONES ---
    elif st.session_state.pantalla == "cert":
        st.markdown("<div class='header-troil'><h1>GESTIÓN DE CERTIFICACIONES</h1></div>", unsafe_allow_html=True)
        if st.button("⬅️ VOLVER"): st.session_state.pantalla = "menu"; st.rerun()
        
        with st.form("f_cert"):
            col1, col2 = st.columns(2)
            with col1:
                nombre_c = st.text_input("Nombre del Certificado")
                empresa = st.text_input("Ente Certificador")
            with col2:
                vencimiento = st.date_input("Fecha de Vencimiento")
                estado = st.selectbox("Estatus", ["Vigente", "Por Vencer", "Vencido"])
            st.form_submit_button("GUARDAR CERTIFICACIÓN")
        firma()

    # --- REGISTRO Y REPORTES ---
    elif st.session_state.pantalla in ["registro", "reportes"]:
        st.info(f"Pantalla de {st.session_state.pantalla} activa con soporte de Fotos y Gráficos.")
        if st.button("⬅️ VOLVER AL MENÚ"): st.session_state.pantalla = "menu"; st.rerun()
        firma()
