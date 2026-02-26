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
