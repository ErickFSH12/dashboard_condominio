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
    st.header("📈 Dashboard Financiero (Automatizado)")
    st.info("Conexión autónoma y procesamiento contable directo.")

    col1, col2, col3 = st.columns(3)
    with col1:
        mes_seleccionado = st.selectbox("Mes", range(1, 13), index=datetime.datetime.now().month - 1)
    with col2:
        anio_seleccionado = st.selectbox("Año", range(2024, 2030), index=2026 - 2024)
    with col3:
        st.write("") 
        btn_consultar = st.button("Consultar Estado de Resultados", use_container_width=True)

    st.divider()

    if "log_auditoria" not in st.session_state:
        st.session_state.log_auditoria = []

    def registrar_log(mensaje):
        tiempo_actual = datetime.datetime.now().strftime("%H:%M:%S")
        entrada = f"[{tiempo_actual}] {mensaje}"
        st.session_state.log_auditoria.append(entrada)

    if btn_consultar:
        st.session_state.log_auditoria = []
        registrar_log("🚀 Iniciando consulta financiera...")
        
        _, ultimo_dia = calendar.monthrange(anio_seleccionado, mes_seleccionado)
        fecha_inicio = f"{anio_seleccionado}-{mes_seleccionado:02d}-01"
        fecha_fin = f"{anio_seleccionado}-{mes_seleccionado:02d}-{ultimo_dia}"
        
        html_resultado = None
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto("https://app.condovive.com/")
                page.fill("input[type='email'], input[name='email'], input[name='username']", st.secrets["CONDOVIVE_USER"])
                page.fill("input[type='password'], input[name='password']", st.secrets["CONDOVIVE_PASS"])
                page.click("button[type='submit'], input[type='submit']")
                page.wait_for_load_state("networkidle")
                
                url_reporte = f"https://app.condovive.com/a/eggrld/s/estadoderesultados?m={mes_seleccionado:02d}&a={anio_seleccionado}&presupuesto="
                page.goto(url_reporte)
                page.wait_for_timeout(10000)
                
                html_resultado = page.content()
                browser.close()
            
            if html_resultado:
                tablas = pd.read_html(StringIO(html_resultado)) 
                
                if len(tablas) >= 2:
                    df_ingresos = tablas[0].copy()
                    df_egresos = tablas[1].copy()
                    
                    # 1. Normalizar nombres de columnas basadas en el diagnóstico
                    # La primera columna es el concepto, la columna de dinero se llama "Total"
                    df_ingresos.columns = ["Concepto", "Monto", "Porcentaje"]
                    df_egresos.columns = ["Concepto", "Monto", "Porcentaje"]
                    
                    # 2. Filtrar filas de subtotales y totales generales para no duplicar sumas
                    palabras_prohibidas = ["Subtotal", "Total", "TOTAL"]
                    patron = '|'.join(palabras_prohibidas)
                    
                    df_ingresos = df_ingresos[~df_ingresos["Concepto"].astype(str).str.contains(patron, case=False, na=False)]
                    df_ingresos["Monto"] = pd.to_numeric(df_ingresos["Monto"].astype(str).str.replace(r'[\$,]', '', regex=True), errors="coerce").fillna(0)
                    
                    df_egresos = df_egresos[~df_egresos["Concepto"].astype(str).str.contains(patron, case=False, na=False)]
                    df_egresos["Monto"] = pd.to_numeric(df_egresos["Monto"].astype(str).str.replace(r'[\$,]', '', regex=True), errors="coerce").fillna(0)

                    total_ingresos = df_ingresos["Monto"].sum()
                    total_egresos = df_egresos["Monto"].sum()
                    flujo_neto = total_ingresos - total_egresos

                    registrar_log(f"✨ Montos calculados correctamente -> Ingresos: ${total_ingresos:,.2f} | Egresos: ${total_egresos:,.2f}")

                    # Renderizado Visual
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
                        
                    with st.expander("🔍 Ver tablas de detalle procesadas"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write("Ingresos Limpios")
                            st.dataframe(df_ingresos, use_container_width=True, hide_index=True)
                        with c2:
                            st.write("Egresos Limpios")
                            st.dataframe(df_egresos, use_container_width=True, hide_index=True)
        except Exception as e:
            registrar_log(f"❌ ERROR CRÍTICO: {str(e)}")
            st.error(f"Error en la automatización: {e}")

    st.divider()
    with st.expander("🛠️ Panel de Auditoría y Logs del Sistema", expanded=False):
        if st.session_state.log_auditoria:
            st.code("\n".join(st.session_state.log_auditoria), language="text")
        else:
            st.info("Ejecuta la consulta para ver los registros.")
