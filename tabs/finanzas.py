import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime
import calendar

def mostrar():
    st.header("📈 Estado de Resultados (Condovive)")
    st.info("Conectado directamente a la API de Condovive")

    # Controles para seleccionar el mes y año
    col1, col2, col3 = st.columns(3)
    with col1:
        mes_seleccionado = st.selectbox("Mes", range(1, 13), index=datetime.datetime.now().month - 1)
    with col2:
        anio_seleccionado = st.selectbox("Año", range(2024, 2030), index=2026 - 2024)
    with col3:
        st.write("") # Espaciador
        btn_consultar = st.button("Consultar API", use_container_width=True)

    st.divider()

    if btn_consultar:
        with st.spinner("Conectando con los servidores de Condovive..."):
            
            # 1. Calcular el primer y último día del mes seleccionado
            _, ultimo_dia = calendar.monthrange(anio_seleccionado, mes_seleccionado)
            fecha_inicio = f"{anio_seleccionado}-{mes_seleccionado:02d}-01"
            fecha_fin = f"{anio_seleccionado}-{mes_seleccionado:02d}-{ultimo_dia}"
            
            url = "https://app.condovive.com/a/eggrld/s/estadoderesultadosmodaldistshared.php"
            
            # 2. Configurar los Headers de la petición
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://app.condovive.com",
                "Referer": f"https://app.condovive.com/a/eggrld/s/estadoderesultados?m={mes_seleccionado:02d}&a={anio_seleccionado}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
                # Llama a la cookie desde los secretos de Streamlit por seguridad
                "Cookie": st.secrets["CONDOVIVE_COOKIE"] 
            }
            
            # 3. Datos (Payload)
            payload = {
                "id": "1",
                "initialDate": fecha_inicio,
                "lastDate": fecha_fin
            }
            
            # 4. Ejecutar la petición
            respuesta = requests.post(url, headers=headers, data=payload)
            
            if respuesta.status_code == 200:
                # Condovive suele devolver tablas HTML en este tipo de peticiones modales
                try:
                    # Intenta leer las tablas HTML que devolvió el PHP
                    tablas = pd.read_html(StringIO(respuesta.text))
                    
                    if tablas:
                        df_finanzas = tablas[0]
                        st.success(f"Datos obtenidos exitosamente: {fecha_inicio} al {fecha_fin}")
                        
                        # Mostrar la tabla cruda extraída
                        st.dataframe(df_finanzas, use_container_width=True)
                        
                        # --- Aquí puedes agregar después las gráficas estadísticas ---
                        
                    else:
                        st.warning("La respuesta fue exitosa, pero no se detectaron tablas financieras en el formato esperado.")
                        with st.expander("Ver código crudo de respuesta"):
                            st.code(respuesta.text[:1000]) # Muestra una parte para depurar
                except Exception as e:
                    # Si no es HTML, a lo mejor devolvió JSON directamente
                    try:
                        datos_json = respuesta.json()
                        st.dataframe(pd.DataFrame(datos_json))
                    except:
                        st.error(f"Error procesando la respuesta: {e}")
            else:
                st.error(f"Error de conexión. Código HTTP: {respuesta.status_code}")
