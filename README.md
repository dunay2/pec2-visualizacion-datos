# PEC 2 · Visualización de datos

**Autor del proyecto:** Diego Javier Ríos Sánchez · Universitat Oberta de Catalunya (UOC).

Tres visualizaciones con datos abiertos para explorar la relación entre técnica, datos y objetivo comunicativo:

- `pie.html`: composición de la población de 16 y más años de Canarias según su relación con la actividad, EPA del segundo trimestre de 2026.
- `candlestick.html`: apertura, máximo, mínimo y cierre del índice TAIEX en 11 sesiones del 1 al 16 de octubre de 2026.
- `beeswarm.html`: masa corporal de 342 observaciones de pingüinos Adélie, Chinstrap y Gentoo de Palmer, 2007–2009.

`index.html` reúne las tres visualizaciones. Cada página incluye explicación, objetivo, audiencia, limitaciones, procedencia, tabla accesible y descarga CSV. Las gráficas se implementan con HTML, CSS y JavaScript/SVG, sin bibliotecas ni servicios externos necesarios para mostrarlas.

## Publicación en GitHub Pages

El sitio está preparado para publicarse desde la raíz de una rama mediante **Settings → Pages → Deploy from a branch → `/ (root)`**. No necesita instalación ni compilación. Todas las rutas de navegación, estilos, scripts y datos son relativas y funcionan dentro del subdirectorio del repositorio. `.nojekyll` evita el procesamiento de Jekyll.

Las rutas directas del sitio publicado son `pie.html`, `candlestick.html` y `beeswarm.html`, añadidas a la URL base que proporcione GitHub Pages. No se incluyen servicios de autenticación, claves, credenciales ni analítica.

## Datos, fuentes y licencias

Datos consultados el **22 de octubre de 2026**. Los archivos incluidos son instantáneas para que las visualizaciones sean reproducibles.

| Visualización | Fuente | Licencia y preparación |
| --- | --- | --- |
| Pie chart | [INE, EPA, tabla 65291](https://www.ine.es/jaxiT3/Tabla.htm?L=0&t=65291) | [CC BY 4.0, según el aviso legal del INE](https://www.ine.es/dyngs/AYU/index.htm?cid=125). Elaboración propia con datos del INE: filtro de Canarias, ambos sexos y 2026T2; selección de ocupados, parados e inactivos y cálculo de porcentajes. Resultados publicados el 28/07/2026. |
| Candlestick chart | [Taiwan Stock Exchange, Weighted Stock Price Index Historical Data](https://data.gov.tw/en/datasets/11755) | [Open Government Data License 1.0](https://data.gov.tw/license). Atribución: TWSE / Securities and Futures Bureau, 2026. Conversión de fechas del calendario ROC al gregoriano, conversión numérica y selección de 11 sesiones. |
| Beeswarm plot | [Palmer Penguins](https://allisonhorst.github.io/palmerpenguins/) | CC0 para los datos. Datos recogidos por Kristen Gorman y Palmer Station LTER, distribuidos por Allison Horst, Alison Hill y Kristen Gorman. De las 344 filas originales se excluyen únicamente las dos sin masa corporal; no se agregan las observaciones. |

Referencia de Palmer Penguins: Horst AM, Hill AP, Gorman KB (2020). *palmerpenguins: Palmer Archipelago (Antarctica) penguin data*. [doi:10.5281/zenodo.3960218](https://doi.org/10.5281/zenodo.3960218).

Los archivos `data/epa_canarias.json`, `data/taiex_provenance.json` y `data/penguins.json` documentan la procedencia y preparación. Las páginas enlazan también las referencias de cada técnica.

## Notas de interpretación

- En el pie chart, el 6,8 % de personas paradas utiliza como denominador toda la población de 16 y más años; no es la tasa de paro sobre la población activa.
- Las velas se expresan en puntos del índice. El color compara el cierre con la apertura de la misma sesión; no revela el orden de los extremos intradía.
- En el beeswarm, cada punto conserva su masa corporal horizontal. El desplazamiento vertical solo evita solapamientos. Las especies tienen tamaños de muestra diferentes.
