import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

st.title('Vissualización de Logs')

# Ruta del archivo de texto
archivo = st.file_uploader("Cargar archivo de texto (.txt)", type=["txt"])

# Verificar si se ha cargado un archivo
if archivo is not None:
    # Leer el contenido del archivo
    lines = archivo.read().decode('utf-8').splitlines()

    # Encontrar la línea que contiene los encabezados de los datos
    for i, line in enumerate(lines):
        if line.startswith("   DATE   ;  TIME  ;Pline; P2 ; P3 ;Ppilot;Ppower"):
            data_start_line = i + 1  # Línea siguiente a los encabezados
            break

    # Encontrar la línea que contiene "NUMBER OF EVENTS: 2724"
    events_line = None
    for i, line in enumerate(lines):
        if "NUMBER OF EVENTS: 2724" in line:
            events_line = i
            break

    # Obtener los datos de interés
    data_lines = lines[data_start_line:events_line]
    data = [line.strip().split(";") for line in data_lines]
    df = pd.DataFrame(data, columns=["DATE", "TIME", "Pline", "P2", "P3", "Ppilot", "Ppower"])

    # Convertir las columnas relevantes a tipos numéricos
    df["Pline"] = pd.to_numeric(df["Pline"])
    df["P2"] = pd.to_numeric(df["P2"])
    df["P3"] = pd.to_numeric(df["P3"])
    df["Ppilot"] = pd.to_numeric(df["Ppilot"])
    df["Ppower"] = pd.to_numeric(df["Ppower"])

    # Convertir la columna "DATE" a formato de fecha
    df["DATE"] = pd.to_datetime(df["DATE"])

    # Crear la visualización
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.plot(df["DATE"], df["Pline"], label="Pline")
    ax.plot(df["DATE"], df["P2"], label="P2")
    ax.plot(df["DATE"], df["P3"], label="P3")
    ax.plot(df["DATE"], df["Ppilot"], label="Ppilot")
    ax.plot(df["DATE"], df["Ppower"], label="Ppower")
    ax.set_xlabel("Fecha y Hora")
    ax.set_ylabel("Presiones")
    ax.set_title('Estado de las Presiones a lo largo del tiempo')
    ax.legend()

    # Buscar la configuración hidráulica en el archivo
    config_lines = []
    start_line = None
    end_line = None

    for i, line in enumerate(lines):
        if "HYDRAULIC CONFIG" in line:
            start_line = i + 1
        elif start_line is not None and line.strip() == "":
            end_line = i
            break

    config_text = "".join(lines[start_line:end_line])

    ax.text(0.02, 0.98, config_text, transform=ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Encontrar las líneas que contienen los datos de battery status
    battery_lines = [line.strip().split(";") for line in lines if "BATTERY STATUS" in line]

    # Extraer fechas y tiempos
    dates = [datetime.strptime(entry[0] + ' ' + entry[1], '%m/%d/%Y %H:%M:%S') for entry in battery_lines]

    # Extraer valores de CB, PB1 y PB2
    cb_values = [float(entry[2].split(': ')[1]) for entry in battery_lines]
    pb1_values = [float(entry[3].split(': ')[1]) for entry in battery_lines]
    pb2_values = [float(entry[4].split(': ')[1]) for entry in battery_lines]

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(dates, cb_values, label='CB')
    ax.plot(dates, pb1_values, label='PB1')
    ax.plot(dates, pb2_values, label='PB2')
    ax.set_xlabel('Fecha y Hora')
    ax.set_ylabel('Estado de la Batería')
    ax.set_title('Estado de la Batería a lo largo del tiempo')
    ax.legend()
    plt.tight_layout()

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Encontrar la línea que contiene los eventos
    for i, line in enumerate(lines):
        if line.startswith("NUMBER OF EVENTS:"):
            events_start_line = i + 2  # Línea siguiente a "NUMBER OF EVENTS:"
            break

    # Obtener los eventos a partir de la línea encontrada
    event_data = [line.strip().split(";") for line in lines[events_start_line:]]

    # Obtener el número máximo de columnas en los eventos
    max_columns = max(len(event) for event in event_data)

    # Rellenar los eventos con menos columnas con valores nulos
    event_data = [event + [None] * (max_columns - len(event)) for event in event_data]

    # Obtener el encabezado del DataFrame a partir de la primera fila
    header = event_data[0]

    # Crear un DataFrame de pandas con los datos de eventos, utilizando el encabezado como columnas
    df = pd.DataFrame(event_data[1:], columns=header)

    # Excluir los eventos que contienen "BATTERY STATUS (CB)" en la columna 'EVENT ID'
    filtered_df = df[~df['EVENT ID'].str.contains("BATTERY STATUS \(CB\)|TEMPERATURE STATUS", regex=True)]

    # Obtener el top 10 de eventos más recurrentes
    top_10_eventos = filtered_df['EVENT ID'].value_counts().head(10)

    # Mostrar el top 10 de eventos en Streamlit
    st.write("Top 10 de eventos más recurrentes (excluyendo BATTERY STATUS y TEMPERATURE STATUS:")
    st.write(top_10_eventos)
else:
    st.write(" ")
