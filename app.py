import streamlit as st

# Importamos los cuatro módulos desde la carpeta 'tabs'
from tabs import calendarios, tickets, mejoras, finanzas

# Configuración general de la página web
st.set_page_config(page_title="Dashboard Lechuguilla", layout="wide")
st.title("🏢 Panel de Control - Mesa Directiva")

# Definición de todas las pestañas de navegación
tab_calendarios, tab_tickets, tab_mejoras, tab_finanzas = st.tabs([
    "📅 Calendarios y Visitas", 
    "📋 Monitoreo de Tickets", 
    "🚀 Puntos de Mejora",
    "💰 Finanzas"
])

# Renderizado del contenido llamando a la función mostrar() de cada archivo
with tab_calendarios:
    calendarios.mostrar()

with tab_tickets:
    tickets.mostrar()

with tab_mejoras:
    mejoras.mostrar()
    
with tab_finanzas:
    finanzas.mostrar()
