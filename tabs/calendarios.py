import streamlit as st
import pandas as pd

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
    st.subheader("📝 Registro de Visitas")
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
            st.success("¡Visita registrada correctamente!")

    st.write("### Historial de Accesos")
    st.dataframe(st.session_state.registro_visitas, use_container_width=True, hide_index=True)
