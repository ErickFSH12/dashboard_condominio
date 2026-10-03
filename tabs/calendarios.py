import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

def mostrar():
    if 'registro_visitas' not in st.session_state:
        st.session_state.registro_visitas = pd.DataFrame(columns=["Fecha", "Proveedor", "Actividad", "Estatus"])

    st.header("Configuración de Proveedores")
    num_calendarios = st.number_input("¿Cuántos proveedores deseas visualizar?", min_value=1, max_value=10, value=3, step=1)
    
    cols = st.columns(num_calendarios)
    nombres_proveedores = []
    
    for i in range(num_calendarios):
        with cols[i]:
            nombre = st.text_input(f"Nombre del Proveedor {i+1}", key=f"prov_{i}", placeholder="Ej. Jardinería...")
            nombres_proveedores.append(nombre if nombre else f"Proveedor {i+1}")

    st.divider()
    
    # ----------------------------------------
    # MÓDULO VISUAL: CALENDARIO
    # ----------------------------------------
    st.subheader("📅 Calendario de Mantenimientos")
    
    eventos = []
    # Asignar un color visual a cada tarjeta según el estatus
    colores = {
        "Programada": "#3788d8", # Azul
        "En sitio": "#ffc107",   # Amarillo
        "Concluida": "#28a745",  # Verde
        "Cancelada": "#dc3545"   # Rojo
    }
    
    # Convertir las filas de la tabla en eventos para el calendario
    if not st.session_state.registro_visitas.empty:
        for index, row in st.session_state.registro_visitas.iterrows():
            fecha_str = row["Fecha"].strftime("%Y-%m-%d")
            evento = {
                "title": f"{row['Proveedor']} - {row['Actividad']}",
                "start": fecha_str,
                "end": fecha_str,
                "color": colores.get(row["Estatus"], "#3788d8")
            }
            eventos.append(evento)
    
    # Configuración de los botones y vistas del calendario
    opciones_calendario = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "initialView": "dayGridMonth",
    }
    
    # Renderizar el widget interactivo
    calendar(events=eventos, options=opciones_calendario, key="calendario_visual")

    st.divider()

    # ----------------------------------------
    # FORMULARIO DE CAPTURA
    # ----------------------------------------
    st.subheader("📝 Agendar Nueva Visita")
    with st.form("form_nueva_visita"):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1: fecha = st.date_input("Fecha de visita")
        with col2: proveedor_seleccionado = st.selectbox("Proveedor", options=nombres_proveedores)
        with col3: estatus = st.selectbox("Estatus de la visita", ["Programada", "En sitio", "Concluida", "Cancelada"])
            
        actividad = st.text_input("Actividad a realizar / Observaciones")
        btn_guardar = st.form_submit_button("Guardar Registro")
        
        if btn_guardar:
            nueva_fila = pd.DataFrame({"Fecha": [fecha], "Proveedor": [proveedor_seleccionado], "Actividad": [actividad], "Estatus": [estatus]})
            st.session_state.registro_visitas = pd.concat([st.session_state.registro_visitas, nueva_fila], ignore_index=True)
            # st.rerun() obliga a la página a refrescarse instantáneamente para que el bloque de color aparezca arriba
            st.rerun() 

    st.write("### Historial de Accesos")
    st.dataframe(st.session_state.registro_visitas, use_container_width=True, hide_index=True)
