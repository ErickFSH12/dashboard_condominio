import streamlit as st

# Importamos los tres módulos que ya construimos en la carpeta 'tabs'
from tabs import calendarios, tickets, mejoras

# Configuración general de la página web
st.set_page_config(page_title="Dashboard Lechuguilla", layout="wide")
st.title("🏢 Panel de Control - Mesa Directiva")

# Definición de las pestañas
tab_calendarios, tab_tickets, tab_mejoras = st.tabs([
    "📅 Calendarios y Visitas", 
    "📋 Monitoreo de Tickets", 
    "🚀 Puntos de Mejora"
])

# Renderizado del contenido llamando a la función mostrar() de cada archivo
with tab_calendarios:
    calendarios.mostrar()

with tab_tickets:
    tickets.mostrar()

with tab_mejoras:
    mejoras.mostrar()
