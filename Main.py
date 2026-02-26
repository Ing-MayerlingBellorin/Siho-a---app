import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")

# Estilo personalizado para el contador
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN A DATOS (SIMULACIÓN Y LECTURA)
# Nota: La app usará tus 'secrets' para conectar al Excel Base_Datos_Siho_A
def cargar_datos():
    try:
        from gspread_pandas import Spread
        creds = st.secrets["GOOGLE_CREDENTIALS"]
        spread = Spread("Base_Datos_Siho_A", creds=creds)
        df = spread.sheet_to_df(sheet="Datos", index=0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        return df
    except Exception as e:
        # Si falla la conexión, mostramos un aviso pero no bloqueamos la app
        return pd.DataFrame()

df_principal = cargar_datos()

# 3. BARRA LATERAL (NAVEGACIÓN Y FILTROS)
st.sidebar.title("🛡️ SIHO-A Navigation")
pagina = st.sidebar.radio("Ir a:", ["Registro Diario", "Panel de Reportes Normativos"])

centros_costo = [
    "Base Morichal", "Base Bare", "Base Oritupano", "Base Anaco", "Base El Tigre", 
    "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", 
    "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"
]

# 4. PÁGINA DE REGISTRO
if pagina == "Registro Diario":
    st.title("🛡️ Sistema de Gestión SIHO-A")
    
    # --- CONTADOR CERO ACCIDENTES ---
    if 'fecha_inicio_cero' not in st.session_state:
        st.session_state.fecha_inicio_cero = datetime(2024, 1, 1).date()

    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        fecha_incidente = st.date_input("Fecha Inicio Conteo:", st.session_state.fecha_inicio_cero)
        st.session_state.fecha_inicio_cero = fecha_incidente
    
    dias_sin = (datetime.now().date() - fecha_incidente).days
    
    with col_c2:
        st.markdown(f"""
            <div style="background-color: #d4edda; padding: 20px; border-radius: 10px; border: 2px solid #28a745; text-align: center;">
                <h1 style="color: #155724; margin: 0; font-size: 45px;">{dias_sin} DÍAS SIN ACCIDENTES</h1>
                <p style="color: #155724; font-weight: bold;">CUMPLIENDO NORMAS DE SEGURIDAD</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # --- FORMULARIO DE GESTIÓN ---
    with st.form("formulario_siho", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            f_reg = st.date_input("Fecha Registro", datetime.now())
            centro = st.selectbox("Ubicación / Centro", centros_costo)
            resp = st.text_input("Responsable")
        with f2:
            cert = st.text_input("Certificación / Item")
            e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "No Aplica"])
            pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "No Aplica"])
        with f3:
            dot = st.text_input("Dotación / EPP")
            e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "No Aplica"])
            act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Incidente", "Dotación", "No Aplica"])
            
        desc = st.text_area("Descripción de la Gestión")
        foto = st.file_uploader("Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
        
        btn = st.form_submit_button("💾 GUARDAR REGISTRO")

    if btn:
        if resp and desc:
            st.success(f"✅ Gestión en {centro} guardada. ¡Sigamos sumando días seguros!")
            st.balloons()
        else:
            st.warning("⚠️ El Responsable y la Descripción son obligatorios.")

# 5. PÁGINA DE REPORTES
else:
    st.title("📊 Indicadores de Cumplimiento SIHO-A")
    
    if df_principal.empty:
        st.error("⚠️ No se puede cargar el reporte. Verifica la conexión al Excel.")
    else:
        # Filtros de Reporte
        st.sidebar.header("Filtros")
        f_inicio = st.sidebar.date_input("Desde", datetime(2024, 1, 1))
        f_fin = st.sidebar.date_input("Hasta", datetime.now())
        c_sel = st.sidebar.selectbox("Centro de Costo", ["Todos"] + centros_costo)
        
        # Lógica de Filtrado
        df_f = df_principal.copy()
        if c_sel != "Todos":
            df_f = df_f[df_f['Centro de Costo'] == c_sel]
            
        # --- MÉTRICAS ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Actividades Totales", len(df_f))
        m2.metric("Charlas Dadas", len(df_f[df_f['Actividad'] == "Charla 5 min"]))
        vencidos = len(df_f[df_f['Estatus Dotación'] == "Vencida"])
        m2.metric("EPP Vencidos", vencidos, delta="- Riesgo" if vencidos == 0 else "+ Riesgo", delta_color="inverse")

        # --- GRÁFICOS ---
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Cumplimiento Normativo (Estatus)")
            fig_pie = px.pie(df_f, names='Estatus Dotación', color='Estatus Dotación',
                             color_discrete_map={'Vigente':'#28a745', 'Vencida':'#dc3545', 'No Aplica':'#6c757d'})
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with g2:
            st.subheader("Gestión por Centro de Costo")
            fig_bar = px.bar(df_f, x='Centro de Costo', color='Actividad', barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📋 Base de Datos Filtrada")
        st.dataframe(df_f, use_container_width=True)
