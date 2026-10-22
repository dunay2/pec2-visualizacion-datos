# PEC 2 · Visualizaciones reproducibles

[Descargar el paquete reproducible completo](PEC2_paquete_reproducible.zip) · [Guía de uso](como_reproducir.html)

El ZIP reúne el cuaderno, el generador, los CSV y sus metadatos, los auxiliares JSON/CSV/SVG de `output/` y las pruebas de `tests/`. Descomprímelo antes de ejecutar los comandos de este README. Los HTML autónomos se producen al ejecutar el generador y no se incluyen en la descarga compacta.

**Diego Javier Ríos Sánchez · Visualización de Datos · UOC**

Este proyecto genera un gráfico de sectores, un gráfico de velas y un beeswarm a partir de tres CSV. Las funciones que dibujan las técnicas son **`plotly.express.pie`**, **`plotly.graph_objects.Candlestick`** y **`seaborn.swarmplot`**. Seaborn calcula la colocación del enjambre; Plotly muestra esas posiciones y permite consultar cada observación al pasar el cursor.

El cuaderno `PEC2_visualizaciones.ipynb` y el script `generar.py` contienen las mismas operaciones en siete secciones. El cuaderno muestra las llamadas y sus parámetros: no delega toda la práctica en una función opaca. Los HTML exportados se pueden abrir localmente o publicar en GitHub Pages, sin que el lector necesite una cuenta.

## 1. Ejecutar desde un ordenador

Se ha comprobado con **Python 3.12.14**. Se recomienda Python 3.11 o 3.12 y un entorno virtual.

```bash
python -m venv .venv
```

Activar el entorno en macOS/Linux:

```bash
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instalar las versiones del proyecto y generar los gráficos:

```bash
python -m pip install -r requirements.txt
python generar.py
```

Abrir `output/pie.html`, `output/candlestick.html`, `output/beeswarm.html` o `output/tablas.html` en un navegador. Los HTML incluyen Plotly.js y funcionan sin conexión. La tabla es una alternativa textual a la lectura del gráfico y permite descargar los datos.

## 2. Ejecutar el cuaderno en Jupyter o Google Colab

Abrir `PEC2_visualizaciones.ipynb`. La primera celda de código instala las versiones fijadas si se cambia `INSTALAR_DEPENDENCIAS` a `True`. Si ya están instaladas, dejarlo en `False`. Después, **Ejecutar todas** en orden. Si se actualizan bibliotecas que ya estaban importadas, reiniciar el kernel antes de ejecutar las celdas de análisis.

El cuaderno admite dos formas de obtener datos:

- Con la carpeta `data/` al lado del cuaderno, usa los CSV locales.
- Si esos archivos no están presentes, el modo `auto` lee las copias públicas del mismo snapshot en GitHub Pages. Se puede fijar `ORIGEN_DATOS = "publico"` o sustituir `CSV_ENTRADA` por tres URL públicas propias.

Colab es un entorno opcional para ejecutar Python. No interviene en la visualización pública: los lectores abren los HTML publicados. Jupyter es el formato/entorno del cuaderno; `nbformat` permite escribirlo y comprobar su estructura. Ninguno sustituye las bibliotecas gráficas.

## 3. Reutilizar con nuevos datos

1. Sustituir los tres CSV de `data/` o editar `CSV_ENTRADA` en la primera sección. Es posible usar rutas locales o URL de descarga directa.
2. Si las cabeceras son distintas, editar `COLUMNAS`: el lado izquierdo es la columna original y el derecho es el nombre que utiliza el proyecto.
3. Actualizar `TITULOS`, las unidades y `ORDEN_ESPECIES`. Para el enjambre, `ETIQUETA_VALOR_SWARM`, `SUFIJO_VALOR_SWARM` y `DECIMALES_SWARM` controlan el eje, los valores del hover y las medianas. Actualizar también la fuente, la licencia y la explicación del objetivo: las afirmaciones sobre Canarias, TAIEX y Palmer Penguins pertenecen a los ejemplos incluidos.
4. Para otra escala de masas, cambiar `RANGO_SWARM = "auto"`, o indicar extremos que incluyan todas las observaciones. Si cambia el tamaño de la figura o de los puntos, volver a ejecutar Seaborn.
5. Ejecutar el script o todas las celdas. Revisar los gráficos y `output/verificacion.json` antes de publicarlos.

| Técnica | CSV incluido | Columnas mínimas | Condiciones |
|---|---|---|---|
| Pie | `data/epa_canarias.csv` | `category`, `thousands` | Una fila por categoría; nombres presentes; cantidades finitas y no negativas; suma positiva. Las categorías deben formar partes excluyentes de un mismo total. |
| Candlestick | `data/taiex.csv` | `date`, `open`, `high`, `low`, `close` | Una fila por sesión; fecha ISO `AAAA-MM-DD`, sin duplicados; cuatro valores numéricos; mínimo ≤ apertura/cierre ≤ máximo. |
| Beeswarm | `data/penguins_original.csv` | `species`, `body_mass_g` | Una fila por individuo; categoría presente para toda masa observada; masa numérica. Se excluye únicamente la masa ausente. |

Los nombres `thousands` y `body_mass_g` describen las unidades de los ejemplos. Si se reutiliza con otra variable, hay que cambiar también los títulos y las variables de unidad/etiqueta, además del mapeo de columnas.

No hace falta transformar los nuevos datos a JSON: el script lo exporta. Tampoco hay que editar trazados SVG a mano.

## 4. Qué hace cada técnica

### Sectores: `px.pie`

`names="category"` determina los sectores y `values="thousands"` su tamaño angular. Se vuelve a calcular cada proporción respecto a la suma de las cantidades. Se conservan el orden del CSV, la forma circular 2D y tres colores. La leyenda no permite ocultar sectores, para mantener estable el denominador.

El ejemplo representa la población de **16 o más años de Canarias en el segundo trimestre de 2026**: ocupados 1.035,5; parados 135,9; inactivos 817,8, en miles de personas. Total: 1.989,2. Los porcentajes son aproximadamente 52,1 %, 6,8 % y 41,1 %. El **6,8 % no es la tasa de paro**: aquí el denominador incluye inactivos. La tasa de paro requiere dividir los parados entre los activos.

### Velas: `go.Candlestick`

La función recibe `x`, `open`, `high`, `low` y `close`. El cuerpo une apertura y cierre; la mecha cubre mínimo y máximo. Turquesa indica cierre igual o superior a apertura; coral, cierre inferior. El eje X es categórico para espaciar por igual las sesiones realmente presentes. Se ordenan las fechas; no se imputan fines de semana, festivos ni otras sesiones ausentes. El eje Y se expresa en puntos del índice.

El snapshot contiene **11 sesiones del TAIEX, del 1 al 16 de octubre de 2026**. El 12 de octubre el cuerpo es de +29,88 puntos, pero el recorrido máximo–mínimo es de 644,08 puntos: un cambio neto pequeño puede coexistir con un recorrido intradía amplio. Las velas no revelan el orden de los acontecimientos dentro de cada sesión.

### Beeswarm: `sns.swarmplot` y `go.Scatter`

`sns.swarmplot(data=swarm, x="body_mass_g", y="species", orient="h")` calcula la colocación. Cada individuo mantiene su masa en el eje X; Seaborn solo desplaza los puntos sobre el eje categórico para evitar superposiciones. No se añade jitter aleatorio ni se implementa un algoritmo propio de colocación.

Después de fijar tamaño, márgenes y rangos, se ejecuta `fig.canvas.draw()`. `PathCollection.get_offsets()` devuelve las coordenadas de cada categoría. Se verifica que la cantidad de puntos y las masas coinciden con el orden de entrada. Los identificadores se vinculan por ese orden comprobado; **nunca se cruzan registros solo por su masa**, porque hay valores repetidos. Plotly recibe la masa original como X y la coordenada vertical calculada por Seaborn como Y.

Se convierten los tamaños de marcador de Matplotlib a píxeles mediante `sqrt(size_collection) × dpi / 72`; con la configuración entregada el diámetro es 8,333 píxeles. La figura de Seaborn y la de Plotly comparten un área de dibujo de 910 × 410 píxeles dentro de una figura de **1100 × 550**. Se comprueba que la menor distancia entre centros sea al menos el diámetro de los puntos.

**La geometría es fija:** los ejes de Plotly tienen `fixedrange=True` y la configuración usa `responsive=False`. La página debe permitir desplazamiento horizontal en pantallas pequeñas. No se debe reducir el ancho del gráfico con CSS ni activar zoom: las posiciones fueron calculadas para un tamaño concreto. Si se desean otras dimensiones o mayor densidad, hay que regenerar el enjambre. Si Seaborn avisa de puntos que no caben, el script termina con un mensaje para reducir el tamaño de los puntos o ampliar el área; no descarta individuos para ocultar el problema.

El original Palmer Penguins contiene 344 registros. Se excluyen **solo 2 masas ausentes**, conservando 342 observaciones: Adélie 151, Chinstrap 68 y Gentoo 123. Se conservan los casos con sexo ausente cuando tienen masa. Las medianas son 3.700, 3.700 y 5.000 g, respectivamente. La separación vertical alrededor de cada especie no representa otra variable.

## 5. Archivos que se generan

| Salida | Uso |
|---|---|
| `output/pie.html`, `candlestick.html`, `beeswarm.html` | Gráficos interactivos autónomos; incluyen Plotly.js. |
| `output/pie.json`, `candlestick.json`, `beeswarm.json` | Figuras Plotly para reutilización en una web o un cuaderno. Los datos se guardan en listas legibles. |
| `output/plotly_config.json` | Configuración de interacción por figura. Es necesario conservarla al volver a insertar el JSON en una web. |
| `output/beeswarm.svg` | Versión vectorial generada por Seaborn/Matplotlib. |
| `output/beeswarm_layout.csv` | `record_id`, `source_row`, `species`, `body_mass_g`, `category_y`, `y`, `y_offset` y diámetro del marcador. Permite reutilizar las posiciones de Seaborn sin recalcularlas a mano. |
| `output/datos_pie.csv`, `datos_velas.csv`, `datos_beeswarm.csv` | Datos que se han representado, con proporciones o identificadores calculados. |
| `output/resumen_beeswarm.csv` | Número de observaciones, mínimo, mediana y máximo por especie. |
| `output/tablas.html` | Tablas legibles y enlaces a gráficos y CSV. |
| `output/verificacion.json` | Versiones, hashes de entrada, recuentos, proporciones y comprobaciones de la geometría. |

Para insertar un gráfico en otra página se puede cargar su JSON con `plotly.io.read_json` y usar `plotly.io.to_html`. Aplicar la configuración correspondiente de `plotly_config.json`. Con `include_plotlyjs="cdn"` el lector necesita conexión; con `True`, el HTML incluye la biblioteca completa. La exportación de este proyecto usa `True` para facilitar la reproducción sin conexión.

## 6. Fuentes, licencias y preparación de los ejemplos

### EPA · INE

- [Tabla 65291: población por relación con la actividad, sexo y comunidad autónoma](https://www.ine.es/jaxiT3/Tabla.htm?L=0&t=65291).
- [API de la tabla](https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/65291?nult=1).
- Selección: Canarias, ambos sexos, segundo trimestre de 2026; ocupados, parados e inactivos. Cantidades en miles de personas. El CSV conserva los identificadores de serie además de las columnas mínimas.
- [Condiciones de reutilización del INE](https://www.ine.es/dyngs/AYU/index.htm?cid=125): Creative Commons Attribution 4.0. Atribución: INE, Encuesta de Población Activa, tabla 65291.

### TAIEX · Taiwan Stock Exchange

- [API oficial MI_5MINS_HIST](https://openapi.twse.com.tw/v1/indicesReport/MI_5MINS_HIST).
- [Catálogo oficial del conjunto de datos](https://data.gov.tw/en/datasets/11755).
- [Open Government Data License 1.0](https://data.gov.tw/license). Atribución: Taiwan Stock Exchange / Securities and Futures Bureau, Weighted Stock Price Index Historical Data, 2026.
- Preparación previa del CSV: conversión de año ROC a gregoriano (+1911), cadenas numéricas a números, selección inclusiva del 1–16 de octubre de 2026 y orden ascendente. Sin agregación ni imputación. El script entregado utiliza ese CSV y vuelve a validar/ordenar las sesiones.
- El endpoint cambia con el tiempo; el CSV incluido es el snapshot utilizado. No volver a consultar el endpoint para reproducir exactamente estas 11 velas.

### Palmer Penguins

- [Documentación y atribución del proyecto](https://allisonhorst.github.io/palmerpenguins/).
- [CSV original](https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/inst/extdata/penguins.csv).
- Horst, A. M.; Hill, A. P.; Gorman, K. B. (2020), *palmerpenguins: Palmer Archipelago (Antarctica) penguin data*. [DOI: 10.5281/zenodo.3960218](https://doi.org/10.5281/zenodo.3960218). Datos recopilados por Kristen Gorman y Palmer Station LTER; datos disponibles bajo **CC0**.
- El CSV original se incluye intacto. La preparación de esta versión usa pandas: lectura de `NA` como ausente, conversión numérica, identificación por fila y exclusión únicamente de las 2 masas ausentes.

Los tres CSV se copiaron de los snapshots usados por el proyecto publicado. `verificacion.json` registra sus hashes SHA-256. Los archivos sintéticos de pruebas no proceden de estas fuentes y están marcados expresamente como ficticios.

## 7. Herramientas y documentación

| Herramienta | Versión fijada | Papel |
|---|---|---|
| Plotly.py | 6.3.0 | Pie y candlestick nativos; scatter interactivo de coordenadas Seaborn; HTML/JSON. |
| Seaborn | 0.13.2 | Algoritmo estándar del beeswarm. |
| Matplotlib | 3.10.8 | Figura y transformaciones de Seaborn; lectura de offsets y exportación SVG. |
| pandas | 2.2.3 | Lectura de CSV, validación, selección, ordenación y resúmenes. |
| NumPy | 2.3.5 | Conversión de arrays y comprobaciones numéricas. |
| nbformat | 5.10.4 | Escritura y validación del archivo Jupyter. |

Plotly.py se distribuye con licencia MIT; Seaborn, BSD de tres cláusulas. Las licencias de los datos se mantienen separadas de las herramientas.

Documentación primaria:

- [Plotly: gráficos de sectores](https://plotly.com/python/pie-charts/), [candlestick](https://plotly.com/python/candlestick-charts/), [exportación HTML](https://plotly.com/python/interactive-html-export/) y [configuración de interacción](https://plotly.com/python/configuration-options/).
- [Plotly: uso gratuito y licencia](https://plotly.com/python/is-plotly-free/) y [archivo de licencia MIT](https://github.com/plotly/plotly.py/blob/main/LICENSE.txt).
- [Seaborn: swarmplot](https://seaborn.pydata.org/generated/seaborn.swarmplot.html) y [licencia BSD](https://github.com/mwaskom/seaborn/blob/master/LICENSE.md).
- [Matplotlib: Collections y get_offsets](https://matplotlib.org/stable/api/collections_api.html).

## 8. Comprobación de reutilización

`tests/datos_sinteticos/` contiene tres CSV **ficticios**, con las mismas columnas, para demostrar que los gráficos no están dibujados a mano para los originales. Incluye fechas desordenadas, masas repetidas, especies alternadas y una masa ausente.

En macOS/Linux:

```bash
PEC2_DATA_DIR=tests/datos_sinteticos \
PEC2_OUTPUT_DIR=tests/output_sintetico \
PEC2_ORIGEN_DATOS=local \
PEC2_SWARM_RANGE=auto \
PEC2_DEMO_LABEL="DATOS SINTÉTICOS · prueba de reutilización" \
python generar.py
```

También se puede usar el verificador independiente de los ejemplos:

```bash
python tests/verificar.py
```

Ese verificador ejecuta el script con originales y sintéticos, valida el formato del cuaderno y ejecuta sus celdas de análisis en un proceso nuevo. Comprueba recuentos, proporciones, OHLC, identidad de las observaciones, conservación de la masa y ausencia de superposición en la geometría fija. No necesita una sesión de Colab ni publica nada en Internet.


## Páginas públicas e integración

`index.html` enlaza `pie.html`, `candlestick.html` y `beeswarm.html`. `como_reproducir.html` explica el uso del cuaderno y cómo sustituir CSV y metadatos. Las páginas contienen tablas HTML de los snapshots originales que se leen sin JavaScript. Cargan Plotly.js desde su CDN; los HTML autónomos producidos por `generar.py` incluyen la biblioteca. Los auxiliares de `output/` y `tests/` se descargan en el [paquete ZIP](PEC2_paquete_reproducible.zip).

Ejecutar `generar.py` actualiza `output/`, no las narraciones, tablas ni metadatos de estas páginas explicativas. Si cambian los datos, revisar y actualizar también ese contexto antes de publicarlo. El beeswarm mantiene su tamaño para conservar la colocación de Seaborn.
