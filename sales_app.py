import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# Definición de la función
def obtencion_datos():
    # Paso 1: Variables globales
    global df_ventas
    global df_ventas_limpio

    # Paso 2: Obtención de los datos
    # Cargar archivo "reporte_ventas.csv" en df_ventas
    df_ventas = pd.read_csv("reporte_ventas.csv")

    # Formatear columnas de fechas a formato datetime
    df_ventas['fecha_pedido'] = pd.to_datetime(df_ventas['fecha_pedido'], format='%Y-%m-%d')
    df_ventas['fecha_envio'] = pd.to_datetime(df_ventas['fecha_envio'], format='%Y-%m-%d')

    # Eliminar registros duplicados y guardar en df_ventas_limpio
    df_ventas_limpio = df_ventas.drop_duplicates()

    # Eliminar registros de prueba en la columna 'nombre_cliente' y guardar en df_ventas_limpio
    df_ventas_limpio = df_ventas_limpio[df_ventas_limpio['nombre_cliente'] != 'prueba']

    # Eliminar registros con valor nulo en la columna 'nombre_cliente' y guardar en df_ventas_limpio
    df_ventas_limpio = df_ventas_limpio.dropna(subset=['nombre_cliente'])

    # Filtrar operaciones sin ganancia y guardar en df_ventas_limpio
    df_ventas_limpio = df_ventas_limpio[df_ventas_limpio['total_ganancia'] > 0]

    # Actualizar el índice del dataframe final
    df_ventas_limpio = df_ventas_limpio.reset_index(drop=True)

    # Mostrar el resultado (puedes ajustar según tus necesidades)
    #st.dataframe(df_ventas_limpio)  # Muestra el DataFrame en Streamlit

    # Puedes agregar más visualizaciones o análisis aquí si lo deseas

# Llamada a la función
obtencion_datos()

def pregunta_1(df_ventas_limpio):
    # Crear una copia de df_ventas_limpio
    df_ventas_año = df_ventas_limpio[['fecha_pedido', 'total_venta']].copy()

    # Verificar si la columna 'fecha_pedido' está en formato de fecha
    if not pd.api.types.is_datetime64_any_dtype(df_ventas_año['fecha_pedido']):
        st.error("Error: La columna 'fecha_pedido' no está en formato de fecha.")
        return

    # Crear una nueva columna 'año' en df_ventas_año
    df_ventas_año['año'] = df_ventas_año['fecha_pedido'].dt.year

    # Verificar si todos los valores en la columna 'año' son enteros
    if not df_ventas_año['año'].apply(lambda x: isinstance(x, int)).all():
        st.error("Error: La columna 'año' no contiene años enteros.")
        return

    # Eliminar la columna 'fecha_pedido'
    df_ventas_año.drop('fecha_pedido', axis=1, inplace=True)

    # Agrupar por la columna 'año' y sumarizar los valores de 'total_venta'
    df_ventas_año = df_ventas_año.groupby('año').aggregate({'total_venta': 'sum'}).reset_index()

    # Configuración de la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))

    # Datos para el gráfico
    ejeX = df_ventas_año['año']
    ejeY = df_ventas_año['total_venta']
    colores = ['#CDDBF3'] * (len(df_ventas_año) - 1) + ['#0077b6']  # Último año en color diferente
    width = 0.8

    # Crear el gráfico de barras verticales
    ax.bar(ejeX, ejeY, color=colores, width=width)

    ax.set_xticks(ax.get_xticks()[::2])  # Mostrar cada segunda etiqueta

    # Colocar los valores sobre cada barra
    for bar in ax.patches:
        valor = bar.get_height()
        qtd = f"${valor:,.2f}"  # Formatear el valor con formato de dólar
        ax.text(bar.get_x() + bar.get_width() / 2.0, valor, qtd,
                ha='center', va='bottom')

    # Configuración adicional del gráfico (puedes ajustar según tus necesidades)
    ax.set_title(f'Ventas totales por año ({df_ventas_año["año"].min()}-{df_ventas_año["año"].max()})',
                 fontsize=16, pad=40, fontweight='bold')
    ax.set_xlabel('Año')
    ax.set_ylabel('Total Venta ($)')

    # Quitar el borde del plano de coordenadas
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Quitar los labels del eje y
    ax.get_yaxis().set_visible(False)

    ax.set_xlabel('')

    ax.tick_params(axis='x', rotation=0)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Texto adicional a la derecha del título
    primer_año = int(df_ventas_año['año'].min())
    ultimo_año = int(df_ventas_año['año'].max())
    ventas_ultimo_año = df_ventas_año.loc[df_ventas_año['año'] == ultimo_año, 'total_venta'].values[0]
    ventas_año_anterior = df_ventas_año.loc[df_ventas_año['año'] == ultimo_año - 1, 'total_venta'].values[0]
    porcentaje_aumento = ((ventas_ultimo_año - ventas_año_anterior) / ventas_año_anterior) * 100

    etiqueta = f"En {ultimo_año}, las ventas subieron aproximadamente {porcentaje_aumento:.2f}% comparado con el {ultimo_año-1}."
    st.markdown(etiqueta)


def pregunta_2(df_ventas_limpio):
    # Crea una copia de df_ventas_limpio
    df_top_ganancias = df_ventas_limpio[['tipo_producto', 'total_ganancia', 'departamento_producto']].copy()

    # Agrupar por 'tipo_producto', sumarizar 'total_ganancia' y ordenar en orden descendente
    df_top_ganancias = df_top_ganancias.groupby(['tipo_producto', 'departamento_producto']).aggregate({'total_ganancia': 'sum'}).reset_index()
    df_top_ganancias = df_top_ganancias.sort_values(by='total_ganancia', ascending=False)

    # Seleccionar los primeros 7 registros
    df_top_ganancias = df_top_ganancias.head(7)

    # Configuración de la figura y el eje
    fig, ax = plt.subplots(figsize=(10, 4))

    # Datos para el gráfico de barras horizontales
    ejeX = df_top_ganancias['total_ganancia']
    ejeY = df_top_ganancias['tipo_producto']
    colores_departamento = df_top_ganancias['departamento_producto'].map({'Electrónicos': '#0077b6', 'Ropa': '#adb5bd', 'Productos de Limpieza': '#0C8040'}).dropna()

    # Crear el gráfico de barras horizontales
    ax.barh(ejeY, ejeX, color=colores_departamento, align='center')

    ax.invert_yaxis()

    # Colocar los valores sobre cada barra
    for i, valor in enumerate(df_top_ganancias['total_ganancia']):
        qtd = f"${valor:,.2f}"  # Formatear el valor con formato de dólar
        ax.text(valor, i, qtd, ha='right', va='center', color='white')

    # Configuración adicional del gráfico
    ax.set_title('Top 7 de productos con mayor ganancia', fontsize=16, pad=40, fontweight='bold')
    ax.set_xlabel('Total Ganancia ($)')
    ax.set_ylabel('Tipo de Producto')

    # Quitar el borde del plano de coordenadas
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Quitar los labels del eje y
    ax.get_yaxis().set_visible(False)

    ax.set_xlabel('')

    ax.tick_params(axis='x', rotation=0)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Texto adicional a la derecha del título
    departamento_mayor_ganancia = df_ventas_limpio.loc[df_ventas_limpio['total_ganancia'].idxmax(), 'departamento_producto']
    etiqueta = f"Los datos indican que los productos que generan mayor ganancia son del departamento {departamento_mayor_ganancia}."
    st.markdown(etiqueta)


def pregunta_3(df_ventas_limpio):
    # Crea una copia de la base df_ventas_limpio en un nuevo dataframe df_ventas_año_region
    df_ventas_año_region = df_ventas_limpio[['fecha_pedido', 'region', 'total_venta']].copy()

    # Crea una nueva columna en df_ventas_año_region llamada año
    df_ventas_año_region['año'] = df_ventas_año_region['fecha_pedido'].dt.year

    # Elimina la columna fecha_pedido de df_ventas_año_region
    df_ventas_año_region.drop('fecha_pedido', axis=1, inplace=True)

    # Genera una tabla cruzada con el método pd.crosstab
    df_ventas_año_region = pd.crosstab(index=df_ventas_año_region['año'], columns=df_ventas_año_region['region'], values=df_ventas_año_region['total_venta'], aggfunc="sum")

    # Cambia el orden de las columnas en el DataFrame
    new_order = ['Sureste', 'Noreste', 'Centro-Oeste', 'Norte', 'Sur']
    df_ventas_año_region = df_ventas_año_region[new_order]

    # Crea una lista con 5 colores, uno por cada región
    colores = ['#0077b6', '#00b4d8', '#90e0ef', '#adb5bd', '#dee2e6']

    # Visualización del gráfico de columnas apiladas
    fig, ax = plt.subplots(figsize=(15, 8))
    df_ventas_año_region.plot(kind='bar', stacked=True, color=colores, ax=ax)

    # Colocar valores dentro de cada contenedor de la pila de barras
    for i, container in enumerate(ax.containers):
        for j, rect in enumerate(container.patches):
            value = rect.get_height()
            if value > 0:  # Mostrar etiqueta solo si el valor es mayor que cero
                formatted_value = f"${round(value / 1000):,d}K"  # Redondear y convertir a entero
                ax.text(rect.get_x() + rect.get_width() / 2,
                        rect.get_y() + rect.get_height() / 2,
                        formatted_value,
                        ha='center', va='center', color='white', fontsize=8, fontweight='bold')

    # Configurar el título y el subtítulo
    ax.set_title('Ventas del Supermercado por región (2019-2022)', fontsize=16, pad=40, fontweight='bold')

    # Calcular y mostrar la suma de los porcentajes de cada región que superó la condición
    ventas_totales_todas_region = df_ventas_año_region.sum().sum()
    regiones_seleccionadas = df_ventas_año_region.columns[df_ventas_año_region.sum() > 0.25 * ventas_totales_todas_region]
    suma_porcentajes = df_ventas_año_region[regiones_seleccionadas].sum() / ventas_totales_todas_region
    suma_porcentajes_text = f"{suma_porcentajes.sum() * 100:.2f}% de las ventas en el Supermercado están concentradas en las regiones {', '.join(regiones_seleccionadas)} desde el 2019"


    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Mostrar el texto adicional en Streamlit
    st.write(suma_porcentajes_text)


def pregunta4(df_ventas_limpio):
    # Crea una copia de df_ventas_limpio
    df_modo_envio = df_ventas_limpio[['segmento_cliente','modo_envio']].copy()

    # Creamos una tabla cruzada entre modo envío y segmento cliente
    df_modo_envio = pd.crosstab(index=df_modo_envio['modo_envio'], columns=df_modo_envio['segmento_cliente']).sort_values(by='B2B')

    # Creamos la Figura
    colores=['#0077b6','#CDDBF3']
    fig, ax = plt.subplots(figsize=(10,5))

    # Plotear las barras horizontales apiladas
    ax.barh(df_modo_envio.index, df_modo_envio['B2B'], color=colores[0])
    ax.barh(df_modo_envio.index, df_modo_envio['B2C'], left=df_modo_envio['B2B'], color=colores[1])

    # Agregar texto a las barras apiladas
    for container in ax.containers:
        ax.bar_label(container, label_type='center', fontsize=9, fontweight='bold', color='black')

    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_title('Método de envío más utilizado por los clientes B2B y B2C (2019-2022)', fontsize=16, pad=40, fontweight='bold')

    # Calcular el porcentaje y agregar texto
    porcentaje = df_ventas_limpio['modo_envio'].value_counts(normalize=True)[0] * 100
    texto_adicional = f"La entrega Estándar es el método de envío preferido por los clientes del Supermercado, representando el {round(porcentaje, 2)}% de los pedidos. No hay diferencia significativa entre los segmentos."

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)

    # Mostrar el texto adicional en Streamlit
    st.write(texto_adicional)


def pregunta_5(df_ventas_limpio):
    # Filtrar filas donde el estado sea Sao Paulo
    # y seleccionar las columnas fecha_pedido y total_venta
    df_ventas_sp = df_ventas_limpio.copy()
    df_ventas_sp = df_ventas_limpio[df_ventas_limpio['estado'] == 'São Paulo'][['fecha_pedido', 'total_venta']]

    # Establece como índice la columna fecha_pedido
    df_ventas_sp.set_index('fecha_pedido', inplace=True)

    # Sumar las ventas totales por trimestre
    df_ventas_sp = df_ventas_sp.resample('Q').sum()

    # Expresar 'total_venta' en miles y redondear a dos decimales
    df_ventas_sp['total_venta'] = (df_ventas_sp['total_venta'] / 1000).round(1)

    # Restaurar 'fecha_pedido' como columna
    df_ventas_sp.reset_index(inplace=True)

    # Crear el gráfico

    fig, ax = plt.subplots(figsize=(14, 4))

    
    ax.plot(df_ventas_sp['fecha_pedido'], df_ventas_sp['total_venta'], marker='o', markevery=[i for i in range(3, len(df_ventas_sp), 4)],
        color='lightblue', markerfacecolor='blue', markeredgecolor='black')

    # Eliminar los bordes
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Formato del título y subtítulo
    ax.set_title('Ventas por Trimestre en el estado de São Paulo', loc='left', fontsize=18)
    fig.suptitle('De 2019 a 2022 (en miles de dólares)', x=0.13, y=0.87, ha='left', fontsize=14, color='gray')

    # Ocultar el eje y
    ax.get_yaxis().set_visible(False)

    # Configurar el eje x
    x_labels = ["Mar", "Jun", "Set", "Dic"] * 4
    ax.set_xticks(df_ventas_sp.fecha_pedido)
    ax.set_xticklabels(x_labels, ha="center")
    ax.tick_params(axis='x', length=0, width=0, colors='black')

    # Poner el texto de total_venta y número del trimestre y año
    for i in range(3, len(df_ventas_sp["total_venta"]), 4):
        trimestre = (i // 4) + 1
        year = df_ventas_sp["fecha_pedido"].iloc[i].year
        venta_text = f"${df_ventas_sp['total_venta'].iloc[i]}"
        trim_text = f' (4° Tri {year})'
        ax.text(df_ventas_sp.fecha_pedido.iloc[i] - pd.to_timedelta("30 days"), df_ventas_sp["total_venta"].iloc[i] + 20, venta_text, color='blue', fontweight='bold')
        ax.text(df_ventas_sp.fecha_pedido.iloc[i] + pd.to_timedelta("43 days"), df_ventas_sp["total_venta"].iloc[i] + 20, trim_text, fontweight='bold')

    # Obtener las coordenadas horizontales para el eje X
    for i in range(3, len(df_ventas_sp["total_venta"]), 4):
        year = df_ventas_sp["fecha_pedido"].iloc[i].year
        jun_date = pd.to_datetime(f"July 15, {year}")
        sep_date = pd.to_datetime(f"September 15, {year}")
        feb_date = pd.to_datetime(f"February 15, {year}")
        dec_22 = pd.to_datetime(f"January 15, 2023")
        mid_point = jun_date + (sep_date - jun_date) / 2
        # En el xlabel poner el año del trim y barras verticales
        ax.text(mid_point, -30, str(year), ha='center', va='top')  # Etiqueta de año
        ax.text(feb_date, -30, '|', ha='center', va='top')  # Etiqueta de |
        ax.text(dec_22, -30, '|', ha='center', va='top')  # Etiqueta de |

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)


def pregunta6(df_ventas_limpio):
    # Paso 1: Preparación de los datos

    # Crea una copia de df_ventas_limpio
    df_ventas_tri = df_ventas_limpio[['fecha_pedido','departamento_producto','cantidad_pedido']].copy()

    # Filtramos la fecha de pedido solo el cuarto trimestre del año
    df_ventas_tri = df_ventas_tri[(df_ventas_tri['fecha_pedido'].dt.quarter == 4)]

    # Agrupamos por departamento y calculamos la cantidad vendida
    df_ventas_tri = df_ventas_tri.groupby('departamento_producto')['cantidad_pedido'].sum().reset_index()

    # Ordena los productos por la cantidad total vendida de forma descendente
    df_ventas_tri = df_ventas_tri.sort_values(by='cantidad_pedido', ascending=False)

    # Creamos la figura
    fig, ax = plt.subplots(figsize=(10,6))
    explodir = [0.08, 0, 0]
    ax.pie(df_ventas_tri['cantidad_pedido'], labels=df_ventas_tri['departamento_producto'], autopct='%1.1f%%', shadow=True,
           startangle=90, textprops={'weight': 'bold'}, explode=explodir, colors=['#7C93C3','#9EB8D9','#CAE7FF'])
    ax.set_title('Productos más vendidos en el último trimestre del año (2019-2022)', fontsize=15, pad=5, loc='left', weight='bold')

    # Añadir comentario
    ax.text(1.6, 0.48, "En el último trimestre del año (2019-2022)", fontsize=12)
    ax.text(1.6, 0.36, "el departamento con más ventas es el de ", fontsize=12)
    ax.text(1.6, 0.24, "Departamento de Limpieza con un 52.3% ", fontsize=12)
    ax.text(1.6, 0.12, "de productos vendidos más de la mitad ", fontsize=12)
    ax.text(1.6, 0.0, "comparado a los demás departamentos", fontsize=12)

    # Agregar leyenda
    ax.legend(df_ventas_tri['departamento_producto'], loc='lower center', bbox_to_anchor=(1.5, 0.1), shadow=True)

    # Mostrar el gráfico en Streamlit
    st.pyplot(fig)



# Pregunta 1
st.subheader('Pregunta 1: Ventas totales por año')
if st.button('Mostrar respuesta 1'):
    pregunta_1(df_ventas_limpio)

# Espaciado
st.markdown("<br><br>", unsafe_allow_html=True)

# Pregunta 2
st.subheader('Pregunta 2: Top 7 de productos con mayor ganancia')
if st.button('Mostrar respuesta 2'):
    pregunta_2(df_ventas_limpio)

# Espaciado
st.markdown("<br><br>", unsafe_allow_html=True)

# Pregunta 3
st.subheader('Pregunta 3: Ventas por región')
if st.button('Mostrar respuesta 3'):
    pregunta_3(df_ventas_limpio)

# Espaciado
st.markdown("<br><br>", unsafe_allow_html=True)

# Pregunta 4
st.subheader('Pregunta 4: Métodos de envío más utilizados')
if st.button('Mostrar respuesta 4'):
    pregunta4(df_ventas_limpio)

# Espaciado
st.markdown("<br><br>", unsafe_allow_html=True)

# Pregunta 5
#st.subheader('Pregunta 5: Ventas por trimestre en São Paulo')
#if st.button('Mostrar respuesta 5'):
#    pregunta_5(df_ventas_limpio)

#st.markdown("<br><br>", unsafe_allow_html=True)

# Pregunta 6
st.subheader('Pregunta 6: Productos más vendidos en el último trimestre')
if st.button('Mostrar respuesta 6'):
    pregunta6(df_ventas_limpio)
