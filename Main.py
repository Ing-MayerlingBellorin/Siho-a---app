import pandas as pd
from datetime import datetime
import plotly.express as px

# 1. CONFIGURACIÓN
st.set_page_config(page_title="SIHO-A Gestión", page_icon="🛡️", layout="wide")

# 2. CONEXIÓN MEJORADA AL EXCEL
def cargar_datos():
    try:
        # Usamos st.connection para una lectura más estable
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Lee la hoja llamada 'Datos'
        df = conn.read(worksheet="Datos")
        # Limpieza básica de datos
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        return df
    except Exception as e:
        return pd.DataFrame() # Retorna vacío si falla

df_principal = cargar_datos()

# 3. NAVEGACIÓN
st.sidebar.title("🛡️ Navegación SIHO-A")
pagina = st.sidebar.radio("Ir a:", ["Registro Diario", "Panel de Reportes Normativos"])

centros_costo = ["Base Morichal", "Base Bare", "Base Oritupano", "Base Anaco", "Base El Tigre", "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"]

# --- PÁGINA DE REGISTRO ---
if pagina == "Registro Diario":
    st.title("🛡️ Sistema de Gestión SIHO-A")
    
    # Contador (Mantenemos tu lógica que ya funciona)
    if 'fecha_inicio_cero' not in st.session_state:
        st.session_state.fecha_inicio_cero = datetime(2024, 1, 1).date()
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        f_incidente = st.date_input("Fecha Inicio Conteo:", st.session_state.fecha_inicio_cero)
        st.session_state.fecha_inicio_cero = f_incidente
    dias_sin = (datetime.now().date() - f_incidente).days
    with col_c2:
        st.markdown(f'<div style="background-color:#d4edda;padding:20px;border-radius:10px;text-align:center;"><h1 style="color:#155724;">{dias_sin} DÍAS SIN ACCIDENTES</h1></div>', unsafe_allow_html=True)

    st.markdown("---")
    with st.form("formulario_siho", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            f_reg = st.date_input("Fecha Registro", datetime.now())
            centro = st.selectbox("Ubicación", centros_costo)
            resp = st.text_input("Responsable")
        with f2:
            cert = st.text_input("Certificación")
            e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "No Aplica"])
            pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "No Aplica"])
        with f3:
            dot = st.text_input("Dotación")
            e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "No Aplica"])
            act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Incidente", "No Aplica"])
        desc = st.text_area("Descripción")
        btn = st.form_submit_button("💾 GUARDAR REGISTRO")
    
    if btn:
        if resp and desc:
            st.success("✅ ¡Registro guardado! Ahora ve al Panel de Reportes.")
            st.balloons()

# --- PÁGINA DE REPORTES ---
else:
    st.title("📊 Indicadores de Cumplimiento")
    
    if df_principal.empty or len(df_principal) == 0:
        st.error("⚠️ No hay datos para mostrar. Asegúrate de haber guardado al menos un registro en el Excel.")
    else:
        # Filtros
        c_sel = st.sidebar.selectbox("Filtrar por Centro", ["Todos"] + centros_costo)
        df_f = df_principal if c_sel == "Todos" else df_principal[df_principal['Centro de Costo'] == c_sel]
        
        # Gráficos Normativos
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Cumplimiento de EPP (Norma)")
            fig_pie = px.pie(df_f, names='Estatus Dotación', color='Estatus Dotación',
                             color_discrete_map={'Vigente':'#28a745', 'Vencida':'#dc3545', 'No Aplica':'#6c757d'})
            st.plotly_chart(fig_pie)
        with g2:
            st.subheader("Actividades por Centro")
            fig_bar = px.bar(df_f, x='Centro de Costo', color='Actividad')
            st.plotly_chart(fig_bar)
        
        st.dataframe(df_f)
