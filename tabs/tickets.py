import streamlit as st
import pandas as pd
import uuid

def mostrar():
    # Inicializar la base de datos temporal para los tickets
    if 'tickets' not in st.session_state:
        st.session_state.tickets = pd.DataFrame(columns=["ID", "Titulo", "Descripcion", "Estatus", "Prioridad"])

    st.header("📋 Tablero Kanban de Pendientes")

    # ----------------------------------------
    # FORMULARIO PARA CREAR NUEVO TICKET
    # ----------------------------------------
    with st.expander("➕ Crear Nuevo Pendiente Administrativo", expanded=False):
        with st.form("form_nuevo_ticket"):
            titulo = st.text_input("Título del pendiente")
            descripcion = st.text_area("Descripción detallada")
            col1, col2 = st.columns(2)
            with col1:
                prioridad = st.selectbox("Prioridad", ["Baja", "Media", "Alta"])
            with col2:
                estatus = st.selectbox("Estatus inicial", ["Por Iniciar", "En Progreso", "Terminado"])
            
            btn_guardar = st.form_submit_button("Guardar Ticket")
            
            if btn_guardar and titulo:
                nuevo_id = str(uuid.uuid4())[:8] # Genera un ID único corto para cada tarjeta
                nueva_fila = pd.DataFrame({
                    "ID": [nuevo_id],
                    "Titulo": [titulo],
                    "Descripcion": [descripcion],
                    "Estatus": [estatus],
                    "Prioridad": [prioridad]
                })
                st.session_state.tickets = pd.concat([st.session_state.tickets, nueva_fila], ignore_index=True)
                st.rerun()

    st.divider()

    # Funciones de control para mover las tarjetas
    def cambiar_estatus(ticket_id, nuevo_estatus):
        st.session_state.tickets.loc[st.session_state.tickets['ID'] == ticket_id, 'Estatus'] = nuevo_estatus
    
    def eliminar_ticket(ticket_id):
        st.session_state.tickets = st.session_state.tickets[st.session_state.tickets['ID'] != ticket_id]

    # ----------------------------------------
    # VISTA VISUAL KANBAN (3 COLUMNAS)
    # ----------------------------------------
    col_todo, col_doing, col_done = st.columns(3)

    # 🔴 COLUMNA 1: POR INICIAR
    with col_todo:
        st.subheader("🔴 Por Iniciar")
        tickets_todo = st.session_state.tickets[st.session_state.tickets['Estatus'] == 'Por Iniciar']
        for _, row in tickets_todo.iterrows():
            with st.container(border=True): # Crea la forma de tarjeta
                st.markdown(f"**{row['Titulo']}**")
                st.caption(f"Prioridad: {row['Prioridad']}")
                st.write(row['Descripcion'])
                
                # Botones de acción en la tarjeta
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("▶️ Iniciar", key=f"start_{row['ID']}"):
                        cambiar_estatus(row['ID'], "En Progreso")
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_todo_{row['ID']}"):
                        eliminar_ticket(row['ID'])
                        st.rerun()

    # 🟡 COLUMNA 2: EN PROGRESO
    with col_doing:
        st.subheader("🟡 En Progreso")
        tickets_doing = st.session_state.tickets[st.session_state.tickets['Estatus'] == 'En Progreso']
        for _, row in tickets_doing.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['Titulo']}**")
                st.caption(f"Prioridad: {row['Prioridad']}")
                st.write(row['Descripcion'])
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("◀️", key=f"back_doing_{row['ID']}"):
                        cambiar_estatus(row['ID'], "Por Iniciar")
                        st.rerun()
                with c2:
                    if st.button("✅", key=f"fin_doing_{row['ID']}"):
                        cambiar_estatus(row['ID'], "Terminado")
                        st.rerun()
                with c3:
                    if st.button("🗑️", key=f"del_doing_{row['ID']}"):
                        eliminar_ticket(row['ID'])
                        st.rerun()

    # 🟢 COLUMNA 3: TERMINADO
    with col_done:
        st.subheader("🟢 Terminado")
        tickets_done = st.session_state.tickets[st.session_state.tickets['Estatus'] == 'Terminado']
        for _, row in tickets_done.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['Titulo']}**")
                st.caption(f"Prioridad: {row['Prioridad']}")
                st.write(row['Descripcion'])
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("◀️ Volver", key=f"back_done_{row['ID']}"):
                        cambiar_estatus(row['ID'], "En Progreso")
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_done_{row['ID']}"):
                        eliminar_ticket(row['ID'])
                        st.rerun()
