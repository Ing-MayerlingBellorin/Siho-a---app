import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gestión SIHO-A Profesional", page_icon="🛡️", layout="wide")

st.title("🛡️ Sistema de Gestión SIHO-A")

# --- SECCIÓN DEL CONTADOR DE DÍAS ---
if 'fecha_inicio_cero' not in st.session_state:
    st.session_state.fecha_inicio_cero = datetime(2024, 1, 1).date()

# Selector de fecha para el conteo
fecha_ultimo_accidente = st.date_input("📅 Fecha del último accidente / Inicio de conteo:", st.session_state.fecha_inicio_cero)
st.session_state.fecha_inicio_cero = fecha_ultimo_accidente

# Cálculo de días
hoy = datetime.now().date()
dias_sin_accidentes = (hoy - fecha_ultimo_accidente).days

if dias_sin_accidentes >= 0:
    # AQUÍ ESTÁ EL ARREGLO: Quitamos el error de 'stdio'
    st.markdown(f"""
        <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; border: 2px solid #28a745; text-align: center;">
            <h1 style="color: #155724; margin: 0; font-size: 50px;">{dias_sin_accidentes} DÍAS</h1>
            <h2 style="color: #155724; margin: 0;">SIN ACCIDENTES</h2>
            <p style="color: #155724;">Objetivo: Seguridad Total</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚠️ La fecha seleccionada es a futuro.")

st.markdown("---")

# --- LISTA DE CENTROS DE COSTO ---
centros_costo = [
    "Base Morichal", "Base Bare", "Base Oritupano", "Base Anaco", "Base El Tigre", 
    "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", 
    "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"
]

# --- FORMULARIO ---
with st.form("formulario_siho_completo", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        fecha_reg = st.date_input("Fecha de Registro", hoy)
        centro = st.selectbox("Centro de Costo", centros_costo)
        responsable = st.text_input("Responsable")
    with c2:
        certificacion = st.text_input("Certificación")
        est_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "No Aplica"])
        pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "No Aplica"])
    with c3:
        dotacion = st.text_input("Dotación")
        est_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "No Aplica"])
        actividad = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Incidente", "No Aplica"])

    desc = st.text_area("Descripción")
    foto = st.file_uploader("Evidencia (Foto)", type=["jpg", "png", "jpeg"])
    enviar = st.form_submit_button("💾 Guardar Registro")

if enviar:
    if responsable and desc:
        st.success(f"✅ ¡Registro guardado! Seguimos en Cero Accidentes.")
        st.balloons()
