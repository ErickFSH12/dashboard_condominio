import streamlit as st
import pandas as pd

def mostrar():
    st.header("🚀 Proyectos y Puntos de Mejora")
    
    # Inicializar datos de ejemplo para visualizar el módulo
    if 'mejoras' not in st.session_state:
        data = {
            "Proyecto": ["Pintura de Fachada Principal", "Instalación de Cámaras CCTV", "Mantenimiento Portón"],
            "Presupuesto (MXN)": [15000, 8500, 3200],
            "Progreso (%)": [75, 10, 100],
            "Estatus": ["En proceso", "Por iniciar", "Terminado"]
        }
        st.session_state.mejoras = pd.DataFrame(data)

    st.write("💡 **Tip:** Puedes hacer doble clic en cualquier celda para editarla. Agrega nuevos proyectos haciendo clic en el botón '+' al final de la tabla.")

    # Editor de datos interactivo con configuración de columnas visuales
    df_editado = st.data_editor(
        st.session_state.mejoras,
        column_config={
            "Progreso (%)": st.column_config.ProgressColumn(
                "Progreso (%)",
                help="Avance del proyecto de 0 a 100",
                format="%d%%",
                min_value=0,
                max_value=100,
            ),
            "Presupuesto (MXN)": st.column_config.NumberColumn(
                "Presupuesto (MXN)",
                help="Costo asignado al proyecto",
                format="$%d",
                step=500,
            ),
            "Estatus": st.column_config.SelectboxColumn(
                "Estatus",
                help="Fase del proyecto",
                options=["Por iniciar", "En proceso", "Terminado"],
                required=True,
            )
        },
        hide_index=True,
        num_rows="dynamic", # Permite agregar o eliminar filas dinámicamente
        use_container_width=True
    )

    # Actualizar la base temporal con los cambios hechos en la tabla
    st.session_state.mejoras = df_editado
    
    st.divider()
    
    # ----------------------------------------
    # MÉTRICAS DE RESUMEN AUTOMÁTICAS
    # ----------------------------------------
    st.subheader("📊 Resumen de Inversión")
    col1, col2, col3 = st.columns(3)
    
    presupuesto_total = df_editado["Presupuesto (MXN)"].sum()
    proyectos_activos = len(df_editado[df_editado["Estatus"] != "Terminado"])
    proyectos_terminados = len(df_editado[df_editado["Estatus"] == "Terminado"])
    
    with col1:
        st.metric("Presupuesto Total Comprometido", f"${presupuesto_total:,.2f} MXN")
    with col2:
        st.metric("Proyectos Activos", proyectos_activos)
    with col3:
        st.metric("Proyectos Terminados", proyectos_terminados)
