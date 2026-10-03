import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime
import calendar
import json

def mostrar():
    st.header("📈 Estado de Resultados (Condovive)")
    st.info("Conectado directamente a la API de Condovive")

    col1, col2, col3 = st.columns(3)
    with col1:
        mes_seleccionado = st.selectbox("Mes", range(1, 13), index=datetime.datetime.now().month - 1)
    with col2:
        anio_seleccionado = st.selectbox("Año", range(2024, 2030), index=2026 - 2024)
    with col3:
        st.write("") 
        btn_consultar = st.button("Consultar API", use_container_width=True)

    st.divider()

    if btn_consultar:
        with st.spinner("Conectando con los servidores de Condovive..."):
            
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
                # 1. Intentar leer como JSON primero
                try:
                    datos_json = respuesta.json()
                    st.success("Datos recibidos en formato JSON.")
                    try:
                        st.dataframe(pd.DataFrame(datos_json), use_container_width=True)
                    except:
                        st.json(datos_json)
                        
                except json.JSONDecodeError:
                    # 2. Si no es JSON, intentar extraer tablas HTML
                    try:
                        tablas = pd.read_html(StringIO(respuesta.text)) 
                        if tablas:
                            st.success(f"Datos obtenidos exitosamente: {fecha_inicio} al {fecha_fin}. Se encontraron {len(tablas)} tablas.")
                            
                            # Crear sub-pestañas automáticas para cada tabla que encuentre
                            nombres_tabs = [f"Sección {i+1}" for i in range(len(tablas))]
                            tabs_datos = st.tabs(nombres_tabs)
                            
                            for i, tabla in enumerate(tablas):
                                with tabs_datos[i]:
                                    st.write(f"**Estructura cruda de la Tabla {i+1}**")
                                    st.dataframe(tabla, use_container_width=True)
                                    # Genera un cuadro de texto fácil de copiar
                                    st.code(tabla.to_csv(index=False))
                    except ValueError:
                        st.error("No se detectaron tablas financieras.")
                        st.warning("⚠️ Diagnóstico: Esto es lo que Condovive respondió realmente. Revisa si es la pantalla de Login (Cookie expirada) o un formato distinto.")
                        with st.expander("🔍 Ver respuesta cruda del servidor"):
                            st.code(respuesta.text[:2000])
                            
            else:
                st.error(f"Error de conexión HTTP: {respuesta.status_code}")
                with st.expander("Ver detalles del error"):
                    st.write(respuesta.text)
