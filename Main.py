import streamlit as st
import pandas as pd

# Título de la App
st.title("🛡️ Sistema SIHO-A")

# Lista de Centros de Costos según tu requerimiento
centros = [
    "Siho-a", "Base Anaco", "Base el Tigre", "Base Morichal",
    "Troil-01", "Troil-02", "Troil-03", "Troil-05", "Troil-06",
    "Troil-07", "Troil-08", "Troil-09", "Troil-10", "Troil-41", 
    "Troil-62", "Troil-111"
]

# Menú lateral para navegación
st.sidebar.header("Menú de Navegación")
opcion = st.sidebar.selectbox("Seleccione Centro de Costo:", centros)

st.header(f"Gestión: {opcion}")

# Aquí iremos agregando los módulos de Charlas, Accidentes y Dotación
st.info(f"Has seleccionado el centro {opcion}. Los módulos se están cargando...")
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configuración de página
st.set_page_config(page_title="Sistema SIHO-A", page_icon="🛡️")

# Conexión con Google Sheets usando los "Secrets" de Streamlit
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    # Intenta leer las credenciales desde los Secrets que pegaste
    creds_dict = st.secrets["GOOGLE_CREDENTIALS"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Nombre exacto de tu hoja de Excel
    sheet = client.open("Base_Datos_Siho_A").sheet1

    st.title("🛡️ Sistema SIHO-A")
    st.subheader("Registro de Dotación")

    # Formulario
    with st.form("registro_form"):
        centro = st.selectbox("Centro de Costo", ["Troil-06", "Base Anaco", "San Tomé", "Guico"])
        trabajador = st.text_input("Nombre del Trabajador")
        item = st.selectbox("Implemento", ["Botas", "Casco", "Braga", "Guantes"])
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        boton = st.form_submit_button("Registrar en Excel")

    if boton:
        # Guardar en la hoja de cálculo
        sheet.append_row([centro, trabajador, item, cantidad])
        st.success(f"✅ ¡Registrado con éxito en Base_Datos_Siho_A!")

except Exception as e:
    st.error("Error de conexión. Revisa si compartiste el Excel con el correo de Google Cloud.")
    st.info("El correo es: siho-a-manager@siho-a-app.iam.gserviceaccount.com")
