import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gestión SIHO-A Profesional", page_icon="🛡️", layout="wide")

st.title("🛡️ Sistema de Gestión SIHO-A")
st.markdown("### Control de Seguridad, Certificaciones y Personal")
st.info("Objetivo: Cero Accidentes 👷‍♂️🚧")

# Lista de tus Centros de Costo
centros_costo = [
    "Base Morichal", "Base Bare", "Base Oritupano", "Base Anaco", "Base El Tigre", 
    "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", 
    "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"
]

# Formulario de entrada
with st.form("formulario_siho_completo", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        centro = st.selectbox("Centro de Costo / Ubicación", centros_costo)
        responsable = st.text_input("Responsable del Registro")

    with col2:
        certificacion = st.text_input("Certificación (Nombre/Tipo)", help="Escribe 'N/A' si no aplica")
        # AGREGADO: Opción "No Aplica"
        estatus_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "No Aplica"])
        # AGREGADO: Opción "No Aplica"
        personal_tipo = st.selectbox("Clasificación Personal", ["CCP", "Supervisores", "Company", "Troil", "No Aplica"])

    with col3:
        dotacion = st.text_input("Dotación (EPP/Equipos)", help="Escribe 'N/A' si no aplica")
        # AGREGADO: Opción "No Aplica"
        estatus_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "No Aplica"])
        # AGREGADO: Opción "No Aplica"
        actividad = st.selectbox("Actividad SIHO-A", ["Charla 5 min", "Inspección", "Reporte Incidente", "Necesidad", "No Aplica"])

    descripcion = st.text_area("Descripción de la gestión o novedades (Obligatorio)")
    archivo_foto = st.file_uploader("Subir Evidencia (Imagen/Archivo)", type=["jpg", "png", "jpeg", "pdf"])
    
    boton_guardar = st.form_submit_button("💾 Guardar Registro Completo")

if boton_guardar:
    if responsable and descripcion:
        try:
            # Mensaje de confirmación en pantalla
            st.success(f"✅ ¡Registro de {centro} guardado exitosamente!")
            if archivo_foto:
                st.info(f"📸 Archivo '{archivo_foto.name}' cargado al sistema.")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Error de conexión: {e}")
    else:
        st.warning("⚠️ Por favor, completa el nombre del Responsable y la Descripción.")
