import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# 1. SEGURIDAD: USUARIOS AUTORIZADOS
USUARIOS = {"adm": "1234", "supervisor1": "1234"}

# 2. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center;'>🛡️ SIHO-A: ACCESO RESTRINGIDO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            u = st.text_input("Usuario")
            p = st.text_input("Clave", type="password")
            if st.button("INGRESAR", use_container_width=True):
                if u in USUARIOS and USUARIOS[u] == p:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = u
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")

else:
    # Conexión automática usando Secrets
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error("Error en Secrets. Revisa el formato TOML.")
        st.stop()

    # Sidebar
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    
    menu = st.sidebar.radio("Menú", ["Registro Diario", "Bitácora y Reportes"])

    # --- SECCIÓN 1: REGISTRO ---
    if menu == "Registro Diario":
        st.title("🛡️ Registro de Gestión Operativa")
        
        # CONTEO DE SEGURIDAD (Desde el 01-01-2026)
        fecha_inicio_conteo = datetime(2026, 1, 1).date()
        dias_sin_accidentes = (datetime.now().date() - fecha_inicio_conteo).days
        
        st.markdown(f"""
            <div style="background-color:#f0f2f6;padding:15px;border-radius:10px;border-left:5px solid #28a745;text-align:center;">
                <h1 style="color:#28a745;margin:0;font-size:40px;">{max(0, dias_sin_accidentes)} DÍAS SIN ACCIDENTES</h1>
                <p style="color:#6c757d;margin:0;">Desde el 01 de Enero de 2026</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("form_siho", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                f_reg = st.date_input("Fecha", datetime.now())
                # UBICACIONES CORREGIDAS
                ubi = st.selectbox("Ubicación", ["Anaco", "Morichal", "El Tigre", "Caracas", "Pariaguán", 
                                                 "Troil-01", "Troil-02", "Troil-03", "Troil-04", "Troil-05", 
                                                 "Troil-06", "Troil-07", "Troil-08", "Troil-09", "Troil-10"])
                resp = st.text_input("Responsable", value=st.session_state.usuario_actual, disabled=True)
            with col_b:
                act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación", "Incidente"])
                cert = st.text_input("Certificación / Item")
                e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
            with col_c:
                dot = st.text_input("Dotación / EPP")
                e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "N/A"])
                pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
            
            desc = st.text_area("Descripción Detallada de la Gestión")
            
            if st.form_submit_button("💾 GUARDAR REGISTRO EN EXCEL", use_container_width=True):
                if desc:
                    try:
                        df_old = conn.read(worksheet="Datos", ttl=0)
                        
                        nueva_fila = pd.DataFrame([{
                            "Fecha": f_reg.strftime('%Y-%m-%d'),
                            "Centro de Costo": ubi,
                            "Actividad": act,
                            "Responsable ": resp,
                            "Descripción": desc,
                            "Certificaciones": cert,
                            "Estatus Certificacion": e_cert,
                            "Dotación": dot,
                            "Estatus Dotación": e_dot,
                            "Personal": pers,
                            "Clasificación": "Fase Piloto"
                        }])
                        
                        df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                        conn.update(worksheet="Datos", data=df_new)
                        
                        st.success("✅ ¡Registro sincronizado con éxito!")
                        st.toast("Datos Guardados", icon="🛡️")
                        time.sleep(1)
                    except Exception as e:
                        st.error("❌ Error de conexión. Verifica los encabezados de tu Excel.")
                else:
                    st.warning("⚠️ Debes completar la descripción.")

    # --- SECCIÓN 2: BITÁCORA ---
    else:
        st.title("📊 Bitácora de Gestión")
        try:
            df_bitacora = conn.read(worksheet="Datos", ttl=0)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_bitacora.to_excel(writer, index=False, sheet_name='SIHO_DATA')
            
            st.download_button(
                label="📥 Descargar Reporte Completo (.xlsx)",
                data=output.getvalue(),
                file_name=f"Reporte_SIHOA_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.dataframe(df_bitacora.sort_values(by="Fecha", ascending=False), use_container_width=True)
            
        except Exception as e:
            st.info("No se pudieron cargar los datos.")
