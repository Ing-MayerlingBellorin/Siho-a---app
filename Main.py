import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
from streamlit_gsheets import GSheetsConnection

# 1. SEGURIDAD Y ACCESO
USUARIOS = {"adm": "1234", "supervisor1": "1234"}

st.set_page_config(page_title="Gestión SIHO-A", page_icon="🛡️", layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

# --- PANTALLA DE LOGIN ---
if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align:center;'>🛡️ SIHO-A: SISTEMA DE GESTIÓN</h1>", unsafe_allow_html=True)
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
                    st.error("❌ Acceso denegado")

else:
    # Conexión a Google Sheets usando Secrets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Sidebar con información del usuario
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    
    menu = st.sidebar.radio("Menú Principal:", ["Registro de Gestión", "Bitácora y Reportes"])

    # --- SECCIÓN 1: REGISTRO ---
    if menu == "Registro de Gestión":
        st.title("🛡️ Registro de Gestión SIHO-A")
        
        # CONTEO DE SEGURIDAD (Desde el 01-01-2026)
        fecha_inicio_conteo = datetime(2026, 1, 1).date()
        dias_sin_accidentes = (datetime.now().date() - fecha_inicio_conteo).days
        
        st.markdown(f"""
            <div style="background-color:#f0f2f6;padding:15px;border-radius:10px;border-left:5px solid #28a745;text-align:center;">
                <h1 style="color:#28a745;margin:0;font-size:40px;">{max(0, dias_sin_accidentes)} DÍAS SIN ACCIDENTES</h1>
                <p style="color:#6c757d;margin:0;">Récord Operativo desde el 01/01/2026</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("form_siho", clear_on_submit=True):
            st.markdown("### 📝 Ingreso de Datos")
            c1, c2, c3 = st.columns(3)
            with c1:
                f_reg = st.date_input("Fecha", datetime.now())
                # UBICACIONES SOLICITADAS
                ubi = st.selectbox("Centro de Costo", [
                    "Base - Caracas", "Base - Anaco", "Pariaguán", "El Tigre", "Morichal",
                    "Troil-01", "Troil-02", "Troil-03", "Troil-04", "Troil-05", 
                    "Troil-06", "Troil-07", "Troil-08", "Troil-09", "Troil-10"
                ])
                resp = st.text_input("Responsable", value=st.session_state.usuario_actual, disabled=True)
            with c2:
                act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación EPP", "Incidente", "Vigilancia"])
                cert = st.text_input("Certificaciones")
                e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
            with c3:
                dot = st.text_input("Dotación")
                e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "N/A"])
                pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
            
            desc = st.text_area("Descripción de la Gestión")
            # CARGA DE FOTO ACTUALIZADA
            foto = st.file_uploader("📸 Cargar Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
            
            btn_save = st.form_submit_button("💾 GUARDAR Y SINCRONIZAR", use_container_width=True)

        if btn_save:
            if desc:
                try:
                    # Leer datos actuales para concatenar
                    df_old = conn.read(worksheet="Datos", ttl=0)
                    nombre_archivo = foto.name if foto else "Sin foto"
                    
                    # Nombres de columnas EXACTOS como en tus fotos
                    nueva_fila = pd.DataFrame([{
                        "Fecha": f_reg.strftime('%Y-%m-%d'),
                        "Centro de Costo": ubi,
                        "Actividad": act,
                        "Responsable": resp,
                        "Descripción": desc,
                        "Certificaciones": cert,
                        "Estatus Certificación": e_cert,
                        "Dotación": dot,
                        "Estatus Dotación": e_dot,
                        "Personal": pers,
                        "Evidencia Foto": nombre_archivo
                    }])
                    
                    df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_new)
                    
                    st.balloons()
                    st.success("✅ ¡Registro sincronizado con éxito!")
                    st.toast("Datos guardados en Google Sheets", icon="🛡️")
                except Exception as e:
                    st.error("❌ Error de nombres. Revisa que las columnas de tu Excel coincidan con el formulario.")
            else:
                st.warning("⚠️ Completa la descripción antes de guardar.")

    # --- SECCIÓN 2: BITÁCORA Y REPORTES ---
    else:
        st.title("📊 Bitácora de Gestión")
        try:
            df_bitacora = conn.read(worksheet="Datos", ttl=0)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                # DESCARGA EXCEL
                output_ex = io.BytesIO()
                with pd.ExcelWriter(output_ex, engine='xlsxwriter') as writer:
                    df_bitacora.to_excel(writer, index=False, sheet_name='Datos')
                st.download_button(
                    label="📥 Descargar Reporte (Excel)",
                    data=output_ex.getvalue(),
                    file_name=f"Reporte_SIHOA_{datetime.now().strftime('%d%m%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with col_d2:
                # INSTRUCCIÓN PDF
                st.info("💡 Para descargar como PDF: Presiona 'Ctrl + P' y selecciona 'Guardar como PDF'.")

            st.markdown("---")
            st.dataframe(df_bitacora.sort_values(by="Fecha", ascending=False), use_container_width=True)
            
        except Exception as e:
            st.info("Aún no hay datos para mostrar.")
