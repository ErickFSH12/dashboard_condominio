import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime
import calendar
import plotly.express as px

def mostrar():
    st.header("📈 Dashboard Financiero (Condovive)")
    st.info("Conexión automática autenticada por API")

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
        with st.spinner("🔄 Autenticando y extrayendo información financiera..."):
            
            try:
                # 1. Crear una sesión HTTP para retener las cookies de acceso
                session = requests.Session()
                
                # Obtener la página de login para extraer tokens de seguridad si los hubiera
                login_page = session.get("https://app.condovive.com/")
                
                # 2. Enviar credenciales de acceso (ajusta las llaves si tu formulario usa otros nombres)
                login_payload = {
                    "email": st.secrets["CONDOVIVE_USER"],
                    "password": st.secrets["CONDOVIVE_PASS"]
                }
                
                # Petición POST para iniciar sesión
                response_login = session.post("https://app.condovive.com/login.php", data=login_payload)
                
                # 3. Calcular fechas del mes seleccionado
                _, ultimo_dia = calendar.monthrange(anio_seleccionado, mes_seleccionado)
                fecha_inicio = f"{anio_seleccionado}-{mes_seleccionado:02d}-01"
                fecha_fin = f"{anio_seleccionado}-{mes_seleccionado:02d}-{ultimo_dia}"
                
                url_reporte = "https://app.condovive.com/a/eggrld/s/estadoderesultadosmodaldistshared.php"
                
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": f"https://app.condovive.com/a/eggrld/s/estadoderesultados?m={mes_seleccionado:02d}&a={anio_seleccionado}"
                }
                
                payload_reporte = {
                    "id": "1",
                    "initialDate": fecha_inicio,
                    "lastDate": fecha_fin
                }
                
                # 4. Descargar el reporte financiero usando la sesión ya logueada
                respuesta = session.post(url_reporte, headers=headers, data=payload_reporte)
                
                if respuesta.status_code == 200:
                    tablas = pd.read_html(StringIO(respuesta.text)) 
                    
                    if len(tablas) >= 2:
                        # Limpieza de Ingresos (Tabla 1)
                        df_ingresos = tablas[0].copy()
                        df_ingresos.columns = ["Concepto", "Monto"]
                        df_ingresos = df_ingresos[df_ingresos["Concepto"] != "Subtotal"]
                        df_ingresos["Monto"] = pd.to_numeric(df_ingresos["Monto"], errors="coerce").fillna(0)
                        
                        # Limpieza de Egresos (Tabla 2)
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
                        st.warning("La sesión se estableció, pero la respuesta no contiene las tablas financieras esperadas.")
                else:
                    st.error(f"Error al solicitar el reporte. Código HTTP: {respuesta.status_code}")
                    
            except Exception as e:
                st.error(f"Ocurrió un error en la conexión: {e}")
