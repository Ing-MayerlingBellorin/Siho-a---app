import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. IDENTIDAD CORPORATIVA SIHO-A
st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")

# 2. CARGA DE DATOS
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
st.sidebar.markdown("### 🛡️ PANEL DE CONTROL")
pagina = st.sidebar.radio("Menú:", ["Registro Diario", "Bitácora e Indicadores"])

centros = ["Base Morichal", "Base Caracas", "Base Pariaguan", "Base Anaco", "Base El Tigre", 
           "Troil 1", "Troil 2", "Troil 3", "Troil 4", "Troil 5", "Troil 6", 
           "Troil 7", "Troil 8", "Troil 9", "Troil 10", "Troil 11"]

# --- SECCIÓN: REGISTRO ---
if pagina == "Registro Diario":
    st.title("🛡️ Registro de Gestión Operativa SIHO-A")
    
    if 'f_inicio' not in st.session_state:
        st.session_state.f_inicio = datetime(2026, 1, 1).date()
    
    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        f_inc = st.date_input("Inicio de conteo:", st.session_state.f_inicio)
        st.session_state.f_inicio = f_inc
    
    dias = (datetime.now().date() - f_inc).days
    with col_c2:
        st.markdown(f"""
            <div style="background-color:#f0f2f6;padding:15px;border-radius:10px;border-left:5px solid #28a745;text-align:center;">
                <h2 style="color:#1e3d59;margin:0;font-size:20px;">ESTADO DE SEGURIDAD</h2>
                <h1 style="color:#28a745;margin:0;font-size:40px;">{dias} DÍAS SIN ACCIDENTES</h1>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    with st.form("form_siho", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            f_reg = st.date_input("Fecha Registro", datetime.now())
            ubi = st.selectbox("Ubicación", centros)
            resp = st.text_input("Responsable del Registro")
        with c2:
            cert = st.text_input("Certificación / Item")
            e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
            pers = st.selectbox("Personal Involucrado", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
        with c3:
            dot = st.text_input("Dotación / EPP")
            e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "N/A"])
            act = st.selectbox("Tipo de Actividad", ["Charla 5 min", "Inspección", "Dotación", "Incidente", "N/A"])
        
        desc = st.text_area("Descripción Detallada de la Gestión")
        foto_archivo = st.file_uploader("📸 Cargar Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
        
        btn_save = st.form_submit_button("💾 FINALIZAR Y GUARDAR REGISTRO")

    if btn_save:
        if resp and desc:
            try:
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
                
                with st.spinner('Archivando en servidor SIHO-A...'):
                    time.sleep(1.2)
                
                if act == "Incidente":
                    st.warning(f"⚠️ REPORTE DE INCIDENTE ARCHIVADO. Atención inmediata en {ubi}.")
                elif act == "Inspección":
                    st.info(f"🔍 INSPECCIÓN REGISTRADA. Documentación guardada correctamente.")
                else:
                    st.success(f"✅ GESTIÓN EXITOSA. Registro de {resp} almacenado.")
                
                st.toast('Base de Datos Actualizada', icon='🛡️')
                
            except Exception as e:
                st.error(f"❌ ERROR DE CONEXIÓN: Verifica los permisos del Excel.")
        else:
            st.error("⚠️ CAMPOS REQUERIDOS: Falta Responsable o Descripción.")

# --- SECCIÓN: BITÁCORA ---
else:
    st.title("📊 Bitácora e Indicadores de Gestión")
    
    col_act, col_desc = st.columns([1, 1])
    with col_act:
        if st.button("🔄 Sincronizar Base de Datos"):
            st.cache_data.clear()
            st.rerun()
    
    if not df_principal.empty:
        # LÓGICA DE DESCARGA
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_principal.to_excel(writer, index=False, sheet_name='Reporte_SIHO')
        processed_data = output.getvalue()

        with col_desc:
            st.download_button(
                label="📥 Descargar Reporte en Excel",
                data=processed_data,
                file_name=f'Reporte_SIHO_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        df_ord = df_principal.sort_values(by='Fecha', ascending=False)
        
        # Dashboard
        col1, col2 = st.columns(2)
        col1.metric("Total Actividades", len(df_ord))
        vencidos = len(df_ord[df_ord['Estatus Dotación'] == 'Vencida'])
        col2.metric("Alertas de Dotación", vencidos, delta_color="inverse")

        st.subheader("📜 Historial Detallado")
        st.dataframe(df_ord, use_container_width=True)

        st.markdown("---")
        # Gráficos
        g1, g2 = st.columns(2)
        with g1:
            fig = px.pie(df_ord, names='Estatus Dotación', title="Cumplimiento Normativo EPP",
                         color='Estatus Dotación', color_discrete_map={'Vigente':'#28a745','Vencida':'#dc3545','N/A':'#6c757d'})
            st.plotly_chart(fig, use_container_width=True)
        with g2:
            st.subheader("Reportes por Centro de Costo")
            st.bar_chart(df_ord['Centro de Costo'].value_counts())
    else:
        st.warning("⚠️ No se pudo cargar el reporte. Verifica la conexión al Excel.")
