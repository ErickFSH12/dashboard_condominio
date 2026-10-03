import streamlit as st
import pandas as pd
from io import StringIO
import datetime
import calendar
import plotly.express as px
import os
import subprocess

# Función para asegurar que el navegador invisible esté disponible en Streamlit Cloud
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
    st.info("Iniciando sesión de forma autónoma en Condovive...")

    col1, col2, col3 = st.columns(3)
    with col1:
        mes_seleccionado = st.selectbox("Mes", range(1, 13), index=datetime.datetime.now().month - 1)
    with col2:
        anio_seleccionado = st.selectbox("Año", range(2024, 2030), index=2026 - 2024)
    with col3:
        st.write("") 
        btn_consultar = st.button("Consultar Estado de Resultados", use_container_width=True)

    st.divider()

    if btn_consultar:
        with st.spinner("🤖 Conectando con Condovive y extrayendo el reporte..."):
            
            _, ultimo_dia = calendar.monthrange(anio_seleccionado, mes_seleccionado)
            fecha_inicio = f"{anio_seleccionado}-{mes_seleccionado:02d}-01"
            fecha_fin = f"{anio_seleccionado}-{mes_seleccionado:02d}-{ultimo_dia}"
            
            html_resultado = None
            
            try:
                with sync_playwright() as p:
                    # Lanzar navegador en modo invisible
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                    
                    # 1. Ir a la página principal de Condovive
                    page.goto("https://app.condovive.com/")
                    
                    # 2. Llenar los campos de usuario y contraseña (tomados de Secrets)
                    page.fill("input[type='email'], input[name='email'], input[name='username']", st.secrets["CONDOVIVE_USER"])
                    page.fill("input[type='password'], input[name='password']", st.secrets["CONDOVIVE_PASS"])
                    
                    # 3. Hacer clic en el botón de acceso y esperar a que cargue
                    page.click("button[type='submit'], input[type='submit']")
                    page.wait_for_load_state("networkidle")
                    
                    # 4. Navegar directo al reporte financiero del mes seleccionado
                    url_reporte = f"https://app.condovive.com/a/eggrld/s/estadoderesultados?m={mes_seleccionado:02d}&a={anio_seleccionado}&presupuesto="
                    page.goto(url_reporte)
                    
                    # Pausa breve para asegurar que renderice la tabla completa por JavaScript
                    page.wait_for_timeout(4000)
                    
                    # Extraer el contenido HTML de la página ya autenticada
                    html_resultado = page.content()
                    browser.close()
                
                # Procesar la información con Pandas
                if html_resultado:
                    tablas = pd.read_html(StringIO(html_resultado)) 
                    
                    if len(tablas) >= 2:
                        df_ingresos = tablas[0].copy()
                        df_ingresos.columns = ["Concepto", "Monto"]
                        df_ingresos = df_ingresos[df_ingresos["Concepto"] != "Subtotal"]
                        df_ingresos["Monto"] = pd.to_numeric(df_ingresos["Monto"], errors="coerce").fillna(0)
                        
                        df_egresos = tablas[1].copy()
                        df_egresos.columns = ["Concepto", "Monto"]
                        df_egresos = df_egresos[df_egresos["Concepto"] != "Subtotal"]
                        df_egresos["Monto"] = pd.to_numeric(df_egresos["Monto"], errors="coerce").fillna(0)

                        total_ingresos = df_ingresos["Monto"].sum()
                        total_egresos = df_egresos["Monto"].sum()
                        flujo_neto = total_ingresos - total_egresos

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
                        st.warning("El inicio de sesión fue exitoso, pero no se detectaron las tablas financieras en la página.")
            except Exception as e:
                st.error(f"Error en la automatización: {e}")
