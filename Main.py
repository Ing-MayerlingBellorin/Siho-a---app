
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="SIHO-A Gestión Total", page_icon="🛡️", layout="wide")

# 2. FUNCIÓN PARA CARGAR DATOS DEL EXCEL
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

# 3. MENÚ LATERAL
st.sidebar.title("🛡️ Gestión SIHO-A")
pagina = st.sidebar.radio("Navegación:", ["Registro Diario", "Bitácora y Reportes"])

# Lista de Centros de Costo
centros = ["Base Morichal", "Base Caracas", "Base pariaguan", "Base Anaco", "Base El Tigre", 
           "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", 
           "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"]

# --- SECCIÓN 1: REGISTRO ---
if pagina == "Registro Diario":
    st.title("🛡️ Sistema de Gestión SIHO-A")
    
    # CONTADOR CERO ACCIDENTES
    if 'f_inicio' not in st.session_state:
        st.session_state.f_inicio = datetime(2026, 1, 1).date()
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        f_inc = st.date_input("Inicio de conteo:", st.session_state.f_inicio)
        st.session_state.f_inicio = f_inc
    
    dias = (datetime.now().date() - f_inc).days
    with col_c2:
        st.markdown(f"""
            <div style="background-color:#d4edda;padding:20px;border-radius:10px;border:2px solid #28a745;text-align:center;">
                <h1 style="color:#155724;margin:0;font-size:35px;">{dias} DÍAS SIN ACCIDENTES</h1>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # FORMULARIO
    with st.form("form_siho", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            f_reg = st.date_input("Fecha Registro", datetime.now())
            ubi = st.selectbox("Ubicación", centros)
            resp = st.text_input("Responsable")
        with c2:
            cert = st.text_input("Certificación / Item")
            e_cert = st.selectbox("Estatus Cert.", ["Vigente", "Vencida", "N/A"])
            pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
        with c3:
            dot = st.text_input("Dotación / EPP")
            e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "N/A"])
            act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación", "N/A"])
        
        desc = st.text_area("Descripción de la Gestión")
        foto_archivo = st.file_uploader("📸 Cargar Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
        
        btn_save = st.form_submit_button("💾 GUARDAR REGISTRO")

    if btn_save:
        if resp and desc:
            try:
                # Guardamos el nombre de la foto
                nombre_foto = foto_archivo.name if foto_archivo else "Sin foto"
                
                nuevo_reg = pd.DataFrame([{
                    "Fecha": f_reg.strftime('%Y-%m-%d'),
                    "Centro de Costo": ubi,
                    "Responsable": resp,
                    "Certificación": cert,
                    "Estatus Certificación": e_cert,
                    "Personal": pers,
                    "Dotación": dot,
                    "Estatus Dotación": e_dot,
                    "Actividad": act,
                    "Descripción": desc,
                    "Evidencia": nombre_foto
                }])

                conn = st.connection("gsheets", type=GSheetsConnection)
                df_old = conn.read(worksheet="Datos")
                df_new = pd.concat([df_old, nuevo_reg], ignore_index=True)
                conn.update(worksheet="Datos", data=df_new)
                
                st.success("✅ ¡Registro guardado exitosamente!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error al conectar con Excel: {e}")
        else:
            st.warning("⚠️ Responsable y Descripción son obligatorios.")

# --- SECCIÓN 2: BITÁCORA Y REPORTES ---
else:
    st.title("📊 Bitácora e Indicadores")
    
    if st.button("🔄 Sincronizar con Excel"):
        st.cache_data.clear()
        st.rerun()

    if df_principal.empty:
        st.warning("⚠️ No hay datos registrados aún.")
    else:
        # Filtros
        df_ord = df_principal.sort_values(by='Fecha', ascending=False)
        busq = st.sidebar.text_input("🔍 Buscar por texto:")
        if busq:
            df_ord = df_ord[df_ord.astype(str).apply(lambda x: x.str.contains(busq, case=False)).any(axis=1)]

        # Dashboard
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Actividades", len(df_ord))
        vencidos = len(df_ord[df_ord['Estatus Dotación'] == 'Vencida'])
        m2.metric("EPP Vencidos", vencidos, delta_color="inverse")
        m3.metric("Ubicación con más reportes", df_ord['Centro de Costo'].mode()[0] if not df_ord.empty else "N/A")

        # Gráficos
        g1, g2 = st.columns(2)
        with g1:
            fig_pie = px.pie(df_ord, names='Estatus Dotación', title="Estatus Normativo",
                             color='Estatus Dotación', color_discrete_map={'Vigente':'#28a745','Vencida':'#dc3545','N/A':'#6c757d'})
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            fig_bar = px.bar(df_ord['Centro de Costo'].value_counts(), title="Reportes por Centro")
            st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📜 Historial Detallado (Bitácora)")
        st.dataframe(df_ord, use_container_width=True)
