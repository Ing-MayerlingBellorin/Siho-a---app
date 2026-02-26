import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gestión SIHO-A Profesional", page_icon="🛡️", layout="wide")

# --- SECCIÓN DEL CONTADOR DE DÍAS (EN GRANDE) ---
st.title("🛡️ Sistema de Gestión SIHO-A")

# Creamos una columna para el contador resaltado
col_logo, col_contador = st.columns([1, 3])

with col_contador:
    # Seleccionar la fecha del último accidente (por defecto hoy, pero puedes cambiarla)
    # Se guarda en el estado de la aplicación para que no se borre al escribir
    if 'fecha_inicio_cero' not in st.session_state:
        st.session_state.fecha_inicio_cero = datetime(2024, 1, 1).date()

    fecha_ultimo_accidente = st.date_input("📅 Fecha del último accidente / Inicio de conteo:", st.session_state.fecha_inicio_cero)
    st.session_state.fecha_inicio_cero = fecha_ultimo_accidente

    # Cálculo de días transcurridos
    hoy = datetime.now().date()
    dias_sin_accidentes = (hoy - fecha_ultimo_accidente).days

    if dias_sin_accidentes >= 0:
        # Estilo visual en grande y verde
        st.markdown(f"""
            <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; border: 2px solid #28a745; text-align: center;">
                <h1 style="color: #155724; margin: 0; font-size: 60px;">{dias_sin_accidentes} DÍAS</h1>
                <h2 style="color: #155724; margin: 0;">SIN ACCIDENTES (META: CERO ACCIDENTES)</h2>
                <p style="color: #155724;">Desde el {fecha_ultimo_accidente.strftime('%d/%m/%Y')}</p>
            </div>
        """, unsafe_allow_stdio=True, unsafe_allow_html=True)
    else:
        st.warning("⚠️ La fecha seleccionada es a futuro.")

st.markdown("---")
st.markdown("### Control de Seguridad, Certificaciones y Personal")

# --- RESTO DEL FORMULARIO ---
centros_costo = [
    "Base Morichal", "Base Bare", "Base Oritupano", "Base Anaco", "Base El Tigre", 
    "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", 
    "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"
]

with st.form("formulario_siho_completo", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    
    with c1:
        fecha_registro = st.date_input("Fecha de Registro", hoy)
        centro = st.selectbox("Centro de Costo / Ubicación", centros_costo)
        responsable = st.text_input("Responsable del Registro")

    with c2:
        certificacion = st.text_input("Certificación (Nombre/Tipo)")
        estatus_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "No Aplica"])
        personal_tipo = st.selectbox("Clasificación Personal", ["CCP", "Supervisores", "Company", "Troil", "No Aplica"])

    with c3:
        dotacion = st.text_input("Dotación (EPP/Equipos)")
        estatus_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "No Aplica"])
        actividad = st.selectbox("Actividad SIHO-A", ["Charla 5 min", "Inspección", "Reporte Incidente", "Necesidad", "No Aplica"])

    descripcion = st.text_area("Descripción de la gestión o novedades")
    archivo_foto = st.file_uploader("Subir Evidencia (Imagen/Archivo)", type=["jpg", "png", "jpeg", "pdf"])
    
    boton_guardar = st.form_submit_button("💾 Guardar Registro Completo")

if boton_guardar:
    if responsable and descripcion:
        st.success(f"✅ Registro guardado. ¡Sumamos un día más de seguridad en {centro}!")
        st.balloons()
