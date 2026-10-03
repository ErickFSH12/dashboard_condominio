import streamlit as st
from tabs import calendarios

st.set_page_config(page_title="Dashboard Lechuguilla", layout="wide")
st.title("🏢 Panel de Control - Mesa Directiva")

tab_calendarios, tab_tickets, tab_mejoras = st.tabs([
    "📅 Calendarios y Visitas", 
    "📋 Monitoreo de Tickets", 
    "🚀 Puntos de Mejora"
])

with tab_calendarios:
    calendarios.mostrar()

with tab_tickets:
    st.info("Módulo de tickets en desarrollo.")

with tab_mejoras:
    st.info("Módulo de mejoras en desarrollo.")
