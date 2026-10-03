import streamlit as st
import pandas as pd
from io import StringIO
import datetime
import calendar
import plotly.express as px
import os
import subprocess
import traceback

@st.cache_resource
def instalar_navegador():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception:
        os.system("playwright install chromium")

instalar_navegador()

from playwright.sync_api import sync_playwright

def mostrar():
    st.header("📈 Dashboard Financiero (Automatizado & Auditado)")
    st.info("Sistema inteligente con registro de auditoría en vivo.")

    col1, col2, col3 = st.columns(3)
    with col1:
        mes_seleccionado = st.selectbox("Mes", range(1, 13), index=datetime.datetime.now().month - 1)
    with col2:
        anio_seleccionado = st.selectbox("Año", range(2024, 2030), index=2026 - 2024)
    with col3:
        st.write("") 
        btn_consultar = st.button("Consultar Estado de Resultados", use_container_width=True)

    st.divider()

    # Inicializar el registro de logs en la sesión si no existe
    if "log_auditoria" not in st.session_state:
        st.session_state.log_auditoria = []

    def registrar_log(mensaje):
        tiempo_actual = datetime.datetime.now().strftime("%H:%M:%S")
        entrada = f"[{tiempo_actual}] {mensaje}"
        st.session_state.log_auditoria.append(entrada)

    if btn_consultar:
        st.session_state.log_auditoria = []  # Limpiar logs anteriores en cada consulta nueva
        registrar_log("🚀 Iniciando proceso de consulta financiera.")
        
        _, ultimo_dia = calendar.monthrange(anio_seleccionado, mes_seleccionado)
        fecha_inicio = f"{anio_seleccionado}-{mes_seleccionado:02d}-01"
        fecha_fin = f"{anio_seleccionado}-{mes_seleccionado:02d}-{ultimo_dia}"
        
        html_resultado = None
        
        try:
            with sync_playwright() as p:
                registrar_log("🌐 Lanzando navegador Chromium en modo headless...")
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                registrar_log("🔗 Navegando a la página principal de Condovive...")
                page.goto("https://app.condovive.com/")
                
                registrar_log("🔑 Rellenando credenciales de acceso...")
                page.fill("input[type='email'], input[name='email'], input[name='username']", st.secrets["CONDOVIVE_USER"])
                page.fill("input[type='password'], input[name='password']", st.secrets["CONDOVIVE_PASS"])
                
                registrar_log("🖱️ Enviando formulario de inicio de sesión...")
                page.click("button[type='submit'], input[type='submit']")
                page.wait_for_load_state("networkidle")
                registrar_log("✅ Inicio de sesión procesado con éxito.")
                
                url_reporte = f"https://app.condovive.com/a/eggrld/s/estadoderesultados?m={mes_seleccionado:02d}&a={anio_seleccionado}&presupuesto="
                registrar_log(f"📂 Navegando directamente al reporte: {url_reporte}")
                page.goto(url_reporte)
                
                registrar_log("⏳ Esperando renderizado de la tabla (4 segundos)...")
                page.wait_for_timeout(4000)
                
                html_resultado = page.content()
                registrar_log(f"📥 HTML extraído correctamente ({len(html_resultado)} caracteres).")
                browser.close()
                registrar_log("🔒 Navegador cerrado de forma segura.")
            
            if html_resultado:
                registrar_log("📊 Procesando tablas HTML mediante Pandas...")
                tablas = pd.read_html(StringIO(html_resultado)) 
                registrar_log(f"🔍 Se detectaron {len(tablas)} tablas en total en la página.")
                
                if len(tablas) >= 2:
                    df_ingresos = tablas[0].copy()
                    cols_ing = list(df_ingresos.columns)
                    cols_ing[0] = "Concepto"
                    cols_ing[-1] = "Monto"
                    df_ingresos.columns = cols_ing
                    df_ingresos = df_ingresos[~df_ingresos["Concepto"].astype(str).str.contains("Subtotal|Total", case=False, na=False)]
                    df_ingresos["Monto"] = pd.to_numeric(df_ingresos["Monto"].astype(str).str.replace(r'[\$,]', '', regex=True), errors="coerce").fillna(0)
                    
                    df_egresos = tablas[1].copy()
                    cols_eg = list(df_egresos.columns)
                    cols_eg[0] = "Concepto"
                    cols_eg[-1] = "Monto"
                    df_egresos.columns = cols_eg
                    df_egresos = df_egresos[~df_egresos["Concepto"].astype(str).str.contains("Subtotal|Total", case=False, na=False)]
                    df_egresos["Monto"] = pd.to_numeric(df_egresos["Monto"].astype(str).str.replace(r'[\$,]', '', regex=True), errors="coerce").fillna(0)

                    total_ingresos = df_ingresos["Monto"].sum()
                    total_egresos = df_egresos["Monto"].sum()
                    flujo_neto = total_ingresos - total_egresos
                    registrar_log("✨ Limpieza de datos y cálculos financieros completados exitosamente.")

                    st.subheader(f"📊 Resumen del Mes ({fecha_inicio} al {fecha_fin})")
                    kpi1, kpi2, kpi3 = st.columns(3)
                    kpi1.metric("Ingresos Totales", f"${total_ingresos:,.2f} MXN")
                    kpi2.metric("Egresos Totales", f"${total_egresos:,.2f} MXN")
                    kpi3.metric("Flujo Neto (Balance)", f"${flujo_neto:,.2f} MXN", delta=float(flujo_neto))

                    st.divider()

                    col_graf1, col_graf2 = st.columns(2)
                    with col_graf1:
                        st.markdown("### 💸 ¿En qué se gastó el presupuesto?")
                        if not df_egresos.empty and total_egresos > 0:
                            fig_gastos = px.pie(df_egresos, values="Monto", names="Concepto", hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                            fig_gastos.update_traces(textposition='inside', textinfo='percent')
                            st.plotly_chart(fig_gastos, use_container_width=True)

                    with col_graf2:
                        st.markdown("### ⚖️ Flujo: Ingresos vs Egresos")
                        df_balance = pd.DataFrame({"Categoría": ["Ingresos", "Egresos"], "Monto": [total_ingresos, total_egresos]})
                        fig_balance = px.bar(df_balance, x="Categoría", y="Monto", color="Categoría", color_discrete_sequence=["#28a745", "#dc3545"], text_auto='.2s')
                        st.plotly_chart(fig_balance, use_container_width=True)
                else:
                    registrar_log("⚠️ Advertencia: No se encontraron al menos 2 tablas financieras válidas.")
                    st.warning("La sesión se estableció, pero no se detectaron las tablas financieras esperadas.")
        except Exception as e:
            error_detalle = traceback.format_exc()
            registrar_log(f"❌ ERROR CRÍTICO: {str(e)}")
            st.error(f"Error en la automatización: {e}")

    # Mostrar siempre el panel de auditoría expandible al fondo de la pestaña de Finanzas
    st.divider()
    with st.expander("🛠️ Panel de Auditoría y Logs del Sistema", expanded=False):
        if st.session_state.log_auditoria:
            st.code("\n".join(st.session_state.log_auditoria), language="text")
        else:
            st.info("No hay registros de ejecución recientes. Presiona 'Consultar Estado de Resultados' para iniciar la auditoría.")
