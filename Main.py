iimport streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SIHO-A TROIL", layout="wide", initial_sidebar_state="collapsed")

# ESTILO CSS PERSONALIZADO (Azul y Naranja de TROIL)
st.markdown(f"""
    <style>
    /* Botones del Menú Principal */
    .stButton>button {{
        width: 100%;
        border-radius: 15px;
        height: 120px;
        font-weight: bold;
        font-size: 20px;
        border: 3px solid #F39200; /* Naranja TROIL */
        color: #004A99; /* Azul TROIL */
        background-color: white;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #004A99;
        color: white;
        border: 3px solid white;
    }}
    /* Cabeceras */
    .header-troil {{
        background-color: #004A99;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        border-bottom: 5px solid #F39200;
        margin-bottom: 25px;
    }}
    /* Firma de la Creadora */
    .footer-signature {{
        text-align: center;
        padding: 20px;
        font-size: 14px;
        color: #555;
        border-top: 1px solid #ddd;
        margin-top: 50px;
    }}
    </style>
    """, unsafe_allow_html=True)

# Firma común para todas las páginas
def mostrar_firma():
    st.markdown("<div class='footer-signature'>Desarrollado por: <b>Ing. Mayerling Bellorin</b></div>", unsafe_allow_html=True)

# Lógica de Navegación
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = "menu"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- PANTALLA 1: MENÚ DE CATEGORÍAS (Referencia Imagen 2) ---
if st.session_state.pantalla == "menu":
    st.markdown("<div class='header-troil'><h1>Gestión de Seguridad SIHO-A</h1><h3>Elija el tipo de informe</h3></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚠️\n\nDivergencia"):
            st.session_state.pantalla = "divergencia"
        if st.button("🚫\n\nObservación"):
            st.session_state.pantalla = "observacion"
    with col2:
        if st.button("🚑\n\nAccidente"):
            st.session_state.pantalla = "accidente"
        if st.button("📢\n\nCasi Suceso"):
            st.session_state.pantalla = "casi_suceso"
    
    mostrar_firma()

# --- PANTALLA 2: FORMULARIO DETALLADO (Referencia Imagen 3) ---
else:
    tipo_titulo = st.session_state.pantalla.replace("_", " ").upper()
    st.markdown(f"<div class='header-troil'><h1>Informe de {tipo_titulo}</h1></div>", unsafe_allow_html=True)
    
    if st.button("⬅️ Regresar al Menú Principal"):
        st.session_state.pantalla = "menu"
        st.rerun()

    with st.form("form_troil"):
        st.subheader("📍 Datos de Identificación")
        c1, c2 = st.columns(2)
        with c1:
            f = st.date_input("Fecha y hora", datetime.now())
            loc = st.selectbox("Localización", ["Base - Caracas", "Base - Anaco", "Troil-01", "Pariaguán"])
        with c2:
            sec = st.text_input("Sección / Área")
            proy = st.text_input("Proyecto / Referencia")
        
        st.divider()
        st.subheader("📝 Detalles de la Gestión")
        desc = st.text_area("Describa el suceso detalladamente")
        accion = st.text_area("¿Qué acción inmediata se tomó?")
        
        st.divider()
        st.subheader("🛡️ Personal y Certificaciones")
        c3, c4 = st.columns(2)
        with c3:
            cert = st.text_input("Certificaciones involucradas")
            est_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "No Aplica"])
        with c4:
            pers = st.selectbox("Personal", ["Propio", "Contratista", "Visitante"])
            dot = st.selectbox("Dotación de EPP", ["Completa", "Incompleta", "N/A"])
            
        foto = st.file_uploader("📸 Evidencia Fotográfica", type=['jpg', 'png', 'jpeg'])

        # Botones de acción al estilo Imagen 3
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.form_submit_button("🗑️ BORRAR TODO"):
                st.rerun()
        with col_b2:
            enviar = st.form_submit_button("✅ ENVIAR A GOOGLE SHEETS")

        if enviar:
            try:
                # Sincronización con el Excel
                df_old = conn.read(worksheet="Datos", ttl=0)
                df_old.columns = df_old.columns.str.strip()
                
                nueva_data = pd.DataFrame([{
                    "Fecha": str(f),
                    "Centro de Costo": loc,
                    "Actividad": tipo_titulo,
                    "Responsable": "Mayerling Bellorin",
                    "Descripción": desc,
                    "Certificaciones": cert,
                    "Estatus Certificación": est_cert,
                    "Personal": pers,
                    "Dotación": dot
                }])
                
                df_final = pd.concat([df_old, nueva_data], ignore_index=True)
                conn.update(worksheet="Datos", data=df_final)
                st.success(f"¡Informe de {tipo_titulo} registrado correctamente!")
                st.balloons()
            except Exception as e:
                st.error(f"Fallo de conexión: {e}")

    mostrar_firma()
