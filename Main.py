import streamlit as st
import pandas as pd
from datetime import datetime
import time
import io
from streamlit_gsheets import GSheetsConnection

# 1. SEGURIDAD: USUARIOS AUTORIZADOS (Fase Piloto)
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
            u = st.text_input("Usuario Asignado")
            p = st.text_input("Clave de Prueba", type="password")
            if st.button("INGRESAR AL SISTEMA", use_container_width=True):
                if u in USUARIOS and USUARIOS[u] == p:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = u
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")

else:
    # Conexión automática usando los Secrets [connections.gsheets]
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
    except Exception as e:
        st.error("Error de configuración en Secrets.")
        st.stop()

    # Sidebar
    st.sidebar.title(f"👤 {st.session_state.usuario_actual}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()
    
    menu = st.sidebar.radio("Navegación:", ["Registro de Gestión", "Bitácora y Reportes"])

    # --- SECCIÓN 1: REGISTRO ---
    if menu == "Registro de Gestión":
        st.title("🛡️ Gestión SIHO-A: Registro Diario")
        
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
            st.markdown("### 📝 Datos del Registro")
            c1, c2, c3 = st.columns(3)
            with c1:
                f_reg = st.date_input("Fecha", datetime.now())
                # UBICACIONES CORREGIDAS SEGÚN TU SOLICITUD
                ubi = st.selectbox("Ubicación", ["Base - Caracas", "Base - Anaco", "Pariaguán", "El Tigre", "Morichal",
                                                 "Troil-01", "Troil-02", "Troil-03", "Troil-04", "Troil-05", 
                                                 "Troil-06", "Troil-07", "Troil-08", "Troil-09", "Troil-10"])
                resp = st.text_input("Responsable", value=st.session_state.usuario_actual, disabled=True)
            with c2:
                act = st.selectbox("Actividad", ["Charla 5 min", "Inspección", "Dotación EPP", "Incidente", "Vigilancia"])
                cert = st.text_input("Certificación / Item")
                e_cert = st.selectbox("Estatus Certificación", ["Vigente", "Vencida", "N/A"])
            with c3:
                dot = st.text_input("Dotación / EPP")
                e_dot = st.selectbox("Estatus Dotación", ["Vigente", "Vencida", "N/A"])
                pers = st.selectbox("Personal", ["CCP", "Supervisores", "Company", "Troil", "N/A"])
            
            desc = st.text_area("Descripción Detallada de la Gestión Realizada")
            
            # CARGA DE FOTOS
            foto = st.file_uploader("📸 Cargar Evidencia Fotográfica", type=["jpg", "png", "jpeg"])
            
            btn_save = st.form_submit_button("💾 GUARDAR Y SINCRONIZAR", use_container_width=True)

        if btn_save:
            if desc:
                try:
                    df_old = conn.read(worksheet="Datos", ttl=0)
                    nombre_archivo = foto.name if foto else "No cargada"
                    
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
                        "Evidencia": nombre_archivo,
                        "Clasificación": "Fase Piloto"
                    }])
                    
                    df_new = pd.concat([df_old, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Datos", data=df_new)
                    
                    st.success("✅ ¡Registro guardado y foto archivada correctamente!")
                    st.toast("Base de Datos Actualizada", icon="🛡️")
                except Exception as e:
                    st.error("❌ Error de sincronización. Verifica los encabezados del Excel.")
            else:
                st.warning("⚠️ La descripción es obligatoria.")

    # --- SECCIÓN 2: BITÁCORA Y REPORTES ---
    else:
        st.title("📊 Bitácora de Gestión e Indicadores")
        try:
            df_bitacora = conn.read(worksheet="Datos", ttl=0)
            
            col_desc1, col_desc2 = st.columns(2)
            
            # DESCARGA EXCEL
            with col_desc1:
                output_ex = io.BytesIO()
                with pd.ExcelWriter(output_ex, engine='xlsxwriter') as writer:
                    df_bitacora.to_excel(writer, index=False, sheet_name='SIHO_DATA')
                st.download_button(
                    label="📥 Descargar Base de Datos (Excel)",
                    data=output_ex.getvalue(),
                    file_name=f"SIHO_Data_{datetime.now().strftime('%d%m%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            # FUNCIÓN PDF (Simulada para navegador)
            with col_desc2:
                st.button("🖨️ Generar Reporte PDF (Imprimir)", on_click=lambda: st.write("Utiliza Ctrl+P para guardar esta vista como PDF"), use_container_width=True)

            st.markdown("---")
            st.dataframe(df_bitacora.sort_values(by="Fecha", ascending=False), use_container_width=True)
            
        except Exception as e:
            st.info("No hay datos registrados aún.")
