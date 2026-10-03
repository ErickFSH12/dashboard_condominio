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
                try:
                    datos_json = respuesta.json()
                    st.success("Datos recibidos en formato JSON.")
                    try:
                        st.dataframe(pd.DataFrame(datos_json), use_container_width=True)
                    except:
                        st.json(datos_json)
                        
                except json.JSONDecodeError:
                    try:
                        tablas = pd.read_html(StringIO(respuesta.text)) 
                        if tablas:
                            st.success(f"Datos obtenidos exitosamente. Se encontraron {len(tablas)} tablas.")
                            
                            # 1. Mostrar las pestañas visuales
                            nombres_tabs = [f"Sección {i+1}" for i in range(len(tablas))]
                            tabs_datos = st.tabs(nombres_tabs)
                            
                            # 2. Variable para agrupar todo el texto
                            texto_maestro = ""
                            
                            for i, tabla in enumerate(tablas):
                                with tabs_datos[i]:
                                    st.dataframe(tabla, use_container_width=True)
                                
                                # Agregar cada tabla al bloque de texto maestro
                                texto_maestro += f"=== ESTRUCTURA DE LA TABLA {i+1} ===\n"
                                texto_maestro += tabla.to_csv(index=False)
                                texto_maestro += "\n\n"
                            
                            st.divider()
                            st.subheader("📋 Bloque de texto para copiar")
                            st.info("Haz clic en el icono de copiar (esquina superior derecha de este cuadro negro) y pégalo en nuestro chat.")
                            
                            # Mostrar un solo cuadro con todo el texto combinado
                            st.code(texto_maestro, language="text")
                            
                    except ValueError:
                        st.error("No se detectaron tablas financieras.")
            else:
                st.error(f"Error de conexión HTTP: {respuesta.status_code}")
