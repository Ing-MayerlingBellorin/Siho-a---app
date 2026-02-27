import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")

# 2. CONEXIÓN A DATOS
def cargar_datos():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Datos")
        if not df.empty and 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        return df
    except Exception:
        return pd.DataFrame()

df_principal = cargar_datos()

# 3. NAVEGACIÓN
st.sidebar.title("🛡️ Panel SIHO-A")
pagina = st.sidebar.radio("Ir a:", ["Registro Diario", "Bitácora y Reportes"])

centros = ["Base Morichal", "Base Bare", "Base Oritupano", "Base Anaco", "Base El Tigre", "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"]

# --- SECCIÓN: REGISTRO ---
if pagina == "Registro Diario":
    st.title("🛡️ Sistema de Gestión SIHO-A")
    
    # CONTADOR (Ya funcionando a 787 días)
    if 'f_inicio' not in st.session_state:
        st.session_state.f_inicio = datetime(2024, 1, 1).date()
    
    f_inc = st.date_input("Inicio de conteo:", st.session_state.f_inicio)
    st.session_state.f_inicio = f_inc
    dias = (datetime.now().date() - f_inc).days
    
    st.markdown(f"""
        <div style="background-color:#d4edda;padding:20px;border-radius:10px;border:2px solid #28a745;text-align:center;">
            <h1 style="color:#155724;margin:0;font-size:40px;">{dias} DÍAS SIN ACCIDENTES</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    with st.form("form_registro", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            f_reg = st.date_input("Fecha", datetime.now())
            ubi = st.selectbox("Ubicación", centros)
            resp = st.text_input("Responsable")
        with c2:
            item = st.text_input("Certificación / Item")
            e_c = st.selectbox("Estatus Cert.", ["Vigente", "Vencida", "N/A"])
            per = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
        with c3:
            dot = st.text_input("Dotación / EPP")
            e_d = st.selectbox("Estatus Dot.", ["Vigente", "Vencida", "N/A"])
            act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación", "N/A"])
        
        obs = st.text_area("Descripción de la Gestión")
        st.form_submit_button("💾 GUARDAR REGISTRO")

# --- SECCIÓN: BITÁCORA Y REPORTES ---
else:
    st.title("📊 Bitácora Histórica SIHO-A")
    
    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

    if df_principal.empty:
        st.warning("⚠️ No hay datos registrados aún.")
    else:
        # Ordenar: Lo más nuevo arriba
        df_ord = df_principal.sort_values(by='Fecha', ascending=False)
        
        # Filtros
        f_filtro = st.sidebar.date_input("Filtrar desde:", datetime(2024, 1, 1))
        df_final = df_ord[df_ord['Fecha'] >= pd.Timestamp(f_filtro)]
        
        # MÉTRICAS NORMADAS
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Total Actividades", len(df_final))
        with m2:
            vencidos = len(df_final[df_final['Estatus Dotación'] == 'Vencida'])
            st.metric("EPP Vencidos", vencidos, delta_color="inverse")

        # TABLA HISTÓRICA (Tu Bitácora)
        st.subheader("📜 Registros por Fecha")
        st.dataframe(df_final, use_container_width=True)

        # GRÁFICOS
        st.markdown("---")
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Estatus de Seguridad")
            fig = px.pie(df_final, names='Estatus Dotación', color='Estatus Dotación',
                         color_discrete_map={'Vigente':'#28a745','Vencida':'#dc3545','N/A':'#6c757d'})
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.subheader("Gestión por Centro")
            st.bar_chart(df_final['Centro de Costo'].value_counts())
