import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime
import calendar
import json
import plotly.express as px

def mostrar():
    st.header("📈 Dashboard Financiero (Condovive)")
    st.info("Conectado directamente a la API de Condovive")

    # Selectores de fecha
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
        with st.spinner("Procesando datos y generando gráficas..."):
            
            _, ultimo_dia = calendar.monthrange(anio_seleccionado, mes_seleccionado)
            fecha_inicio = f"{anio_seleccionado}-{mes_seleccionado:02d}-01"
            fecha_fin = f"{anio_seleccionado}-{mes_seleccionado:02d}-{ultimo_dia}"
            
            url = "https://app.condovive.com/a/eggrld/s/estadoderesultadosmodaldistshared.php"
            
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://app.condovive.com",
                "Referer": f"https://app.condovive.com/a/eggrld/s/estadoderesultados?m={mes_seleccionado:02d}&a={anio_seleccionado}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
                "Cookie": st.secrets["CONDOVIVE_COOKIE"] 
            }
            
            payload = {
                "id": "1",
                "initialDate": fecha_inicio,
                "lastDate": fecha_fin
            }
            
            respuesta = requests.post(url, headers=headers, data=payload)
            
            if respuesta.status_code == 200:
                try:
                    # Leemos el HTML de Condovive
                    tablas = pd.read_html(StringIO(respuesta.text)) 
                    
                    if len(tablas) >= 2:
                        # ------------------------------------------------
                        # 1. LIMPIEZA DE DATOS AUTOMÁTICA
                        # ------------------------------------------------
                        
                        # Extraer Tabla 1: INGRESOS
                        df_ingresos = tablas[0].copy()
                        df_ingresos.columns = ["Concepto", "Monto"]
                        df_ingresos = df_ingresos[df_ingresos["Concepto"] != "Subtotal"]
                        df_ingresos["Monto"] = pd.to_numeric(df_ingresos["Monto"], errors="coerce").fillna(0)
                        
                        # Extraer Tabla 2: EGRESOS
                        df_egresos = tablas[1].copy()
                        df_egresos.columns = ["Concepto", "Monto"]
                        df_egresos = df_egresos[df_egresos["Concepto"] != "Subtotal"]
                        df_egresos["Monto"] = pd.to_numeric(df_egresos["Monto"], errors="coerce").fillna(0)

                        # Cálculos matemáticos
                        total_ingresos = df_ingresos["Monto"].sum()
                        total_egresos = df_egresos["Monto"].sum()
                        flujo_neto = total_ingresos - total_egresos

                        # ------------------------------------------------
                        # 2. RENDERIZADO VISUAL DEL DASHBOARD
                        # ------------------------------------------------
                        st.subheader(f"📊 Resumen del Mes ({fecha_inicio} al {fecha_fin})")
                        kpi1, kpi2, kpi3 = st.columns(3)
                        
                        kpi1.metric("Ingresos Totales", f"${total_ingresos:,.2f} MXN")
                        kpi2.metric("Egresos Totales", f"${total_egresos:,.2f} MXN")
                        kpi3.metric("Flujo Neto (Balance)", f"${flujo_neto:,.2f} MXN", delta=float(flujo_neto))

                        st.divider()

                        # Gráficos
                        col_graf1, col_graf2 = st.columns(2)
                        
                        with col_graf1:
                            st.markdown("### 💸 ¿En qué se gastó el presupuesto?")
                            if not df_egresos.empty and total_egresos > 0:
                                # Gráfica de Dona
                                fig_gastos = px.pie(
                                    df_egresos, 
                                    values="Monto", 
                                    names="Concepto", 
                                    hole=0.4,
                                    color_discrete_sequence=px.colors.qualitative.Pastel
                                )
                                fig_gastos.update_traces(textposition='inside', textinfo='percent')
                                st.plotly_chart(fig_gastos, use_container_width=True)
                            else:
                                st.info("No hay gastos registrados en este periodo.")

                        with col_graf2:
                            st.markdown("### ⚖️ Flujo: Ingresos vs Egresos")
                            # Gráfica de Barras
                            df_balance = pd.DataFrame({
                                "Categoría": ["Ingresos", "Egresos"],
                                "Monto": [total_ingresos, total_egresos]
                            })
                            fig_balance = px.bar(
                                df_balance, 
                                x="Categoría", 
                                y="Monto", 
                                color="Categoría",
                                color_discrete_sequence=["#28a745", "#dc3545"],
                                text_auto='.2s'
                            )
                            st.plotly_chart(fig_balance, use_container_width=True)

                        # Tablas de detalle desplegables (para no saturar la vista)
                        with st.expander("🔍 Ver desglose contable detallado"):
                            c1, c2 = st.columns(2)
                            with c1:
                                st.write("**Detalle de Ingresos**")
                                st.dataframe(df_ingresos, use_container_width=True, hide_index=True)
                            with c2:
                                st.write("**Detalle de Egresos**")
                                st.dataframe(df_egresos, use_container_width=True, hide_index=True)

                    else:
                        st.warning("Se conectó a Condovive, pero la estructura no coincide con las tablas esperadas.")
                
                except ValueError:
                    st.error("No se detectaron tablas financieras. Verifica que la sesión de Condovive siga activa.")
            else:
                st.error(f"Error de conexión HTTP: {respuesta.status_code}")
