#!/usr/bin/env python3
"""PEC 2 · Tres visualizaciones reproducibles con Plotly y Seaborn.

Ejecutar: python generar.py
Las secciones # %% son también las celdas del cuaderno entregado.
"""

# %% 1. Configuración: rutas, columnas, títulos y dimensiones
from pathlib import Path
import os
import sys
import json
import hashlib
import warnings
import html
import io
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
DATA_DIR = Path(os.environ.get("PEC2_DATA_DIR", str(ROOT / "data")))
OUTPUT_DIR = Path(os.environ.get("PEC2_OUTPUT_DIR", str(ROOT / "output")))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# "auto": archivos locales si existen; si no, copias públicas del mismo snapshot.
# Se pueden sustituir estas rutas por otros CSV locales o por URL públicas.
ORIGEN_DATOS = os.environ.get("PEC2_ORIGEN_DATOS", "auto")  # auto / local / publico
PUBLIC_BASE = "https://dunay2.github.io/pec2-visualizacion-datos/data/"
ARCHIVOS = {
    "pie": "epa_canarias.csv",
    "candlestick": "taiex.csv",
    "beeswarm": "penguins_original.csv",
}
CSV_ENTRADA = {
    nombre: (PUBLIC_BASE + archivo if ORIGEN_DATOS == "publico" or
             (ORIGEN_DATOS == "auto" and not (DATA_DIR / archivo).exists())
             else str(DATA_DIR / archivo))
    for nombre, archivo in ARCHIVOS.items()
}

# Izquierda: nombres de columna en el CSV. Derecha: nombres que usan las gráficas.
# Si el nuevo CSV tiene otras cabeceras, cambiar solo el lado izquierdo.
COLUMNAS = {
    "pie": {"category": "category", "thousands": "thousands"},
    "candlestick": {"date": "date", "open": "open", "high": "high",
                    "low": "low", "close": "close"},
    "beeswarm": {"species": "species", "body_mass_g": "body_mass_g"},
}

TITULOS = {
    "pie": "Situación laboral en Canarias · segundo trimestre de 2026",
    "candlestick": "TAIEX · 11 sesiones del 1 al 16 de octubre de 2026",
    "beeswarm": "Masa corporal de pingüinos adultos · Palmer, 2007–2009",
}
UNIDAD_PIE = "miles de personas de 16 o más años"
UNIDAD_VELAS = "Puntos del índice"
ETIQUETA_VALOR_SWARM = "Masa corporal"
SUFIJO_VALOR_SWARM = "g"
DECIMALES_SWARM = 0
UNIDAD_SWARM = f"{ETIQUETA_VALOR_SWARM} ({SUFIJO_VALOR_SWARM})"
ROTULO_DEMO = os.environ.get("PEC2_DEMO_LABEL", "")
if ROTULO_DEMO:
    TITULOS = {k: f"{ROTULO_DEMO} · {k}" for k in TITULOS}
    UNIDAD_PIE = "unidades sintéticas"
    UNIDAD_VELAS = "Valores OHLC sintéticos"

# Con nuevos datos, usar "auto" o elegir otros extremos que incluyan todos los casos.
RANGO_SWARM = os.environ.get("PEC2_SWARM_RANGE", "2500,6500")
RANGO_SWARM = "auto" if RANGO_SWARM == "auto" else tuple(map(float, RANGO_SWARM.split(",")))
ORDEN_ESPECIES = ["Adelie", "Chinstrap", "Gentoo"]  # se añaden nuevas categorías al final
ANCHO, ALTO = 1100, 550
MARGEN_SWARM = dict(l=150, r=40, t=70, b=70)
TAMANO_SWARM_PT = 6  # parámetro size de Seaborn; se convierte a píxeles para Plotly
COLORES = ["#007F86", "#E76850", "#4F6ACB"]
FONDO, TEXTO = "#F7F5EF", "#102A43"

# Evita escribir la caché de Matplotlib en ubicaciones de solo lectura.
os.environ.setdefault("MPLCONFIGDIR", str(Path(os.environ.get("TMPDIR", "/tmp")) / "pec2_matplotlib"))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # también funciona sin escritorio; no cambia el algoritmo de Seaborn
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
import seaborn as sns
import plotly
import plotly.express as px
import plotly.graph_objects as go

VERSIONES = {
    "python": sys.version.split()[0], "plotly": plotly.__version__,
    "pandas": pd.__version__, "numpy": np.__version__,
    "seaborn": sns.__version__, "matplotlib": matplotlib.__version__,
}


# %% 2. Cargar CSV y comprobar su estructura
huellas_csv = {}
def leer_csv(nombre):
    """Lee un archivo o URL pública y registra el hash del contenido exacto."""
    origen = CSV_ENTRADA[nombre]
    if origen.startswith(("https://", "http://")):
        with urlopen(origen, timeout=30) as respuesta:
            contenido = respuesta.read()
    else:
        contenido = Path(origen).read_bytes()
    huellas_csv[nombre] = hashlib.sha256(contenido).hexdigest()
    return pd.read_csv(io.BytesIO(contenido)).rename(columns=COLUMNAS[nombre])

def exigir_columnas(df, columnas, nombre):
    faltan = set(columnas) - set(df.columns)
    if faltan:
        raise ValueError(f"{nombre}: faltan las columnas {sorted(faltan)}")
    if df.empty:
        raise ValueError(f"{nombre}: el CSV no contiene observaciones")

def numericas_finitas(df, columnas, nombre):
    for columna in columnas:
        df[columna] = pd.to_numeric(df[columna], errors="raise")
        if not np.isfinite(df[columna].to_numpy(dtype=float)).all():
            raise ValueError(f"{nombre}: {columna} contiene valores ausentes o no finitos")

def numero_es(valor, decimales=0, signo=False):
    """Formato español para textos ya calculados (separators solo afecta a Plotly)."""
    formato = f"{valor:+,.{decimales}f}" if signo else f"{valor:,.{decimales}f}"
    return formato.translate(str.maketrans({",": ".", ".": ","}))

pie = leer_csv("pie")
velas = leer_csv("candlestick")
pingüinos_originales = leer_csv("beeswarm")
exigir_columnas(pie, ["category", "thousands"], "Pie")
exigir_columnas(velas, ["date", "open", "high", "low", "close"], "Candlestick")
exigir_columnas(pingüinos_originales, ["species", "body_mass_g"], "Beeswarm")

if pie["category"].isna().any() or pie["category"].astype(str).str.strip().eq("").any():
    raise ValueError("Pie: todas las categorías deben tener nombre")
pie["category"] = pie["category"].astype(str)
if pie["category"].duplicated().any():
    raise ValueError("Pie: usar una sola fila por categoría; agregar antes si hay repeticiones")
numericas_finitas(pie, ["thousands"], "Pie")
if (pie["thousands"] < 0).any() or pie["thousands"].sum() <= 0:
    raise ValueError("Pie: hacen falta cantidades no negativas y un total positivo")
# La proporción se calcula de nuevo: no se confía en una columna share previa.
pie["share"] = pie["thousands"] / pie["thousands"].sum()

velas["date"] = pd.to_datetime(velas["date"], errors="raise", format="%Y-%m-%d")
if velas["date"].isna().any() or velas["date"].duplicated().any():
    raise ValueError("Candlestick: cada fecha debe identificar una sola sesión")
numericas_finitas(velas, ["open", "high", "low", "close"], "Candlestick")
velas = velas.sort_values("date", kind="stable").reset_index(drop=True)
if not ((velas["low"] <= velas[["open", "close"]].min(axis=1)) &
        (velas["high"] >= velas[["open", "close"]].max(axis=1))).all():
    raise ValueError("Candlestick: low ≤ apertura/cierre ≤ high debe cumplirse en cada sesión")
velas["date"] = velas["date"].dt.strftime("%Y-%m-%d")
velas["range"] = velas["high"] - velas["low"]
velas["body_change"] = velas["close"] - velas["open"]

# Se conserva la posición de cada registro antes de filtrar. No se unen puntos por masa:
# hay masas repetidas y esa unión confundiría los individuos.
pingüinos_originales["source_row"] = np.arange(len(pingüinos_originales)) + 2
pingüinos_originales["record_id"] = "fila-" + pingüinos_originales["source_row"].astype(str)
pingüinos_originales["body_mass_g"] = pd.to_numeric(
    pingüinos_originales["body_mass_g"], errors="raise")
filas_excluidas = int(pingüinos_originales["body_mass_g"].isna().sum())
swarm = pingüinos_originales.loc[pingüinos_originales["body_mass_g"].notna()].copy()
if swarm.empty:
    raise ValueError("Beeswarm: no hay masas observadas")
if swarm["species"].isna().any() or swarm["species"].astype(str).str.strip().eq("").any():
    raise ValueError("Beeswarm: cada masa observada necesita una categoría")
swarm["species"] = swarm["species"].astype(str)
numericas_finitas(swarm, ["body_mass_g"], "Beeswarm")
especies_presentes = swarm["species"].drop_duplicates().tolist()
orden_especies = [s for s in ORDEN_ESPECIES if s in especies_presentes]
orden_especies += [s for s in especies_presentes if s not in orden_especies]
colores_especies = {s: COLORES[i % len(COLORES)] for i, s in enumerate(orden_especies)}

print("Versiones:", VERSIONES)
print(f"Datos: {len(pie)} categorías; {len(velas)} sesiones; "
      f"{len(swarm)} individuos ({filas_excluidas} masas ausentes excluidas).")


# %% 3. Pie chart: Plotly Express calcula y dibuja los sectores
fig_pie = px.pie(
    pie, names="category", values="thousands", color="category",
    color_discrete_sequence=COLORES, title=TITULOS["pie"],
)
# Plotly Express utiliza arrays internamente. Una asignación nueva como lista
# mantiene el JSON legible (sin codificación binaria bdata de Plotly 6).
fig_pie.data[0].values = None
fig_pie.data[0].values = pie["thousands"].tolist()
fig_pie.update_traces(
    labels=pie["category"].tolist(), values=pie["thousands"].tolist(),
    sort=False, hole=0, direction="clockwise", rotation=0,
    textposition=["outside" if p < 0.10 else "inside" for p in pie["share"]],
    texttemplate="%{label}<br>%{percent:.1%}",
    textfont=dict(size=18), insidetextfont=dict(color="white"), outsidetextfont=dict(color=TEXTO),
    marker=dict(line=dict(color=FONDO, width=2)),
    hovertemplate="<b>%{label}</b><br>%{value:,.1f} " + UNIDAD_PIE +
                  "<br>%{percent:.2%} del total<extra></extra>",
)
fig_pie.update_layout(
    width=ANCHO, height=ALTO, paper_bgcolor=FONDO, plot_bgcolor=FONDO,
    font=dict(family="Arial, sans-serif", color=TEXTO, size=15),
    margin=dict(l=50, r=50, t=85, b=80), separators=",.",
    legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.08,
                itemclick=False, itemdoubleclick=False),
    annotations=[dict(text=f"Total: {numero_es(pie['thousands'].sum(), 1)} {UNIDAD_PIE}",
                      x=0.5, y=-0.04, xref="paper", yref="paper", showarrow=False)],
    meta=dict(tool="plotly.express.pie", denominator="Suma de todas las categorías",
              note="La leyenda no oculta sectores: el denominador permanece estable."),
)
fig_pie


# %% 4. Candlestick: una vela OHLC nativa de Plotly por sesión
fechas = velas["date"].tolist()
texto_velas = [
    f"<b>{fila.date}</b><br>Apertura: {numero_es(fila.open, 2)}<br>Máximo: {numero_es(fila.high, 2)}"
    f"<br>Mínimo: {numero_es(fila.low, 2)}<br>Cierre: {numero_es(fila.close, 2)}"
    f"<br>Rango: {numero_es(fila.range, 2)}<br>Cierre − apertura: {numero_es(fila.body_change, 2, signo=True)}"
    for fila in velas.itertuples(index=False)
]
fig_candlestick = go.Figure(go.Candlestick(
    x=fechas, open=velas["open"].tolist(), high=velas["high"].tolist(),
    low=velas["low"].tolist(), close=velas["close"].tolist(),
    increasing=dict(line=dict(color=COLORES[0], width=1.8), fillcolor=COLORES[0]),
    decreasing=dict(line=dict(color=COLORES[1], width=1.8), fillcolor=COLORES[1]),
    hovertext=texto_velas, hoverinfo="text", name="OHLC", whiskerwidth=0.5,
))
fig_candlestick.update_layout(
    title=TITULOS["candlestick"], width=ANCHO, height=ALTO,
    paper_bgcolor=FONDO, plot_bgcolor=FONDO,
    font=dict(family="Arial, sans-serif", color=TEXTO, size=15),
    margin=dict(l=90, r=40, t=80, b=100), separators=",.", showlegend=False,
    xaxis=dict(type="category", categoryorder="array", categoryarray=fechas,
               rangeslider=dict(visible=False), title="Sesiones, separadas por igual",
               tickmode="array", tickvals=fechas,
               ticktext=[pd.Timestamp(d).strftime("%d/%m") for d in fechas],
               showgrid=False),
    yaxis=dict(title=UNIDAD_VELAS, gridcolor="#D9DFDD", zeroline=False),
    annotations=[dict(x=0.5, y=-0.23, xref="paper", yref="paper", showarrow=False,
                      text="Turquesa: cierre ≥ apertura · Coral: cierre < apertura")],
    meta=dict(tool="plotly.graph_objects.Candlestick",
              session_spacing="Equidistante; no se inventan sesiones ausentes",
              color_rule="Comparación del cierre con la apertura de esa sesión"),
)
fig_candlestick


# %% 5. Beeswarm: Seaborn coloca los puntos; Matplotlib permite leer las posiciones
# No se implementa un algoritmo de colocación. sns.swarmplot resuelve el enjambre.
if RANGO_SWARM == "auto":
    minimo, maximo = float(swarm["body_mass_g"].min()), float(swarm["body_mass_g"].max())
    margen = (maximo - minimo) * 0.08 if maximo > minimo else max(abs(minimo) * 0.08, 1)
    rango_x = (minimo - margen, maximo + margen)
else:
    if len(RANGO_SWARM) != 2 or not np.isfinite(RANGO_SWARM).all() or RANGO_SWARM[0] >= RANGO_SWARM[1]:
        raise ValueError("RANGO_SWARM: usar 'auto' o dos extremos finitos, en orden creciente")
    rango_x = RANGO_SWARM
if swarm["body_mass_g"].min() < rango_x[0] or swarm["body_mass_g"].max() > rango_x[1]:
    raise ValueError("Beeswarm: hay masas fuera del rango. Cambiar RANGO_SWARM a 'auto' o ampliarlo")

dpi = 100
fig_swarm_mpl, ax = plt.subplots(figsize=(ANCHO / dpi, ALTO / dpi), dpi=dpi)
fig_swarm_mpl.subplots_adjust(
    left=MARGEN_SWARM["l"] / ANCHO, right=1 - MARGEN_SWARM["r"] / ANCHO,
    bottom=MARGEN_SWARM["b"] / ALTO, top=1 - MARGEN_SWARM["t"] / ALTO,
)
fig_swarm_mpl.patch.set_facecolor(FONDO)
ax.set_facecolor(FONDO)
ax.set_xlim(*rango_x)
ax.set_ylim(len(orden_especies) - 0.5, -0.5)

with warnings.catch_warnings(record=True) as avisos_swarm:
    warnings.simplefilter("always")
    sns.swarmplot(
        data=swarm, x="body_mass_g", y="species", order=orden_especies,
        orient="h", size=TAMANO_SWARM_PT, color=COLORES[0], linewidth=0,
        warn_thresh=0, ax=ax,
    )
    ax.set_xlim(*rango_x)
    ax.set_ylim(len(orden_especies) - 0.5, -0.5)
    ax.set_xlabel(UNIDAD_SWARM, color=TEXTO)
    ax.set_ylabel("")
    ax.set_title(TITULOS["beeswarm"], loc="left", color=TEXTO, pad=20)
    ax.tick_params(colors=TEXTO)
    sns.despine(ax=ax, left=True)
    ax.grid(axis="x", color="#D9DFDD", linewidth=0.6)
    ax.set_axisbelow(True)
    # Seaborn recalcula las posiciones durante draw; hay que medir después.
    fig_swarm_mpl.canvas.draw()

avisos_colocacion = [str(a.message) for a in avisos_swarm if "cannot be placed" in str(a.message)]
if avisos_colocacion:
    raise ValueError("Beeswarm demasiado denso para este tamaño. Reducir TAMANO_SWARM_PT "
                     "o ampliar ANCHO/ALTO y volver a ejecutar. " + " ".join(avisos_colocacion))

colecciones = [c for c in ax.collections
               if isinstance(c, PathCollection) and len(c.get_offsets()) > 0]
if len(colecciones) != len(orden_especies):
    raise AssertionError("La cantidad de colecciones no coincide con las categorías")

filas_layout, comprobaciones_swarm = [], []
for category_y, (especie, coleccion) in enumerate(zip(orden_especies, colecciones)):
    grupo = swarm.loc[swarm["species"].eq(especie)]
    coordenadas = np.asarray(coleccion.get_offsets(), dtype=float).copy()
    if len(coordenadas) != len(grupo):
        raise AssertionError(f"{especie}: se ha perdido alguna observación")
    # En Seaborn 0.13.2 los offsets vuelven al orden de entrada de cada grupo.
    # Se verifica: no se deduce la identidad a partir de masas que pueden repetirse.
    np.testing.assert_allclose(coordenadas[:, 0], grupo["body_mass_g"].to_numpy(),
                               rtol=0, atol=1e-10,
                               err_msg=f"{especie}: cambió el orden o la masa")
    coleccion.set_facecolor(colores_especies[especie])
    diametro_px = float(np.sqrt(coleccion.get_sizes()[0]) * dpi / 72)
    pantalla = ax.transData.transform(coordenadas)
    if len(pantalla) > 1:
        distancias = np.sqrt(((pantalla[:, None, :] - pantalla[None, :, :]) ** 2).sum(axis=2))
        np.fill_diagonal(distancias, np.inf)
        distancia_minima = float(distancias.min())
        if distancia_minima < diametro_px - 1e-6:
            raise AssertionError(f"{especie}: se detecta solapamiento de marcadores")
    else:
        distancia_minima = None
    comprobaciones_swarm.append(dict(
        species=especie, count=len(grupo), original_order_preserved=True,
        max_x_error=float(np.max(np.abs(coordenadas[:, 0] - grupo["body_mass_g"].to_numpy()))),
        marker_diameter_px=diametro_px, minimum_center_distance_px=distancia_minima,
    ))
    for (_, registro), coordenada in zip(grupo.iterrows(), coordenadas):
        filas_layout.append(dict(
            record_id=registro["record_id"], source_row=int(registro["source_row"]),
            species=especie, body_mass_g=float(registro["body_mass_g"]),
            category_y=category_y, y=float(coordenada[1]),
            y_offset=float(coordenada[1] - category_y), marker_diameter_px=diametro_px,
        ))
    mediana_grupo = float(grupo["body_mass_g"].median())
    ax.vlines(mediana_grupo, category_y - 0.32, category_y + 0.32,
              color=TEXTO, linewidth=1, linestyles="dotted", zorder=0)
    ax.text(mediana_grupo, category_y + 0.42,
            f"Mediana: {numero_es(mediana_grupo, DECIMALES_SWARM)} {SUFIJO_VALOR_SWARM}",
            ha="center", va="center", fontsize=8.6, color=TEXTO,
            bbox=dict(facecolor=FONDO, edgecolor="none", pad=1))

beeswarm_layout = pd.DataFrame(filas_layout)
assert len(beeswarm_layout) == len(swarm)
assert beeswarm_layout["record_id"].is_unique
# Comprobación global: incluye también puntos de categorías vecinas.
pantalla_global = ax.transData.transform(beeswarm_layout[["body_mass_g", "y"]].to_numpy())
if len(pantalla_global) > 1:
    distancias_globales = np.sqrt(((pantalla_global[:, None, :] - pantalla_global[None, :, :]) ** 2).sum(axis=2))
    np.fill_diagonal(distancias_globales, np.inf)
    distancia_minima_global = float(distancias_globales.min())
    if distancia_minima_global < float(beeswarm_layout["marker_diameter_px"].max()) - 1e-6:
        raise AssertionError("Beeswarm: categorías demasiado próximas; aumentar ALTO o reducir los puntos")
else:
    distancia_minima_global = None
fig_swarm_mpl.savefig(OUTPUT_DIR / "beeswarm.svg", format="svg", facecolor=FONDO)
plt.close(fig_swarm_mpl)


# %% 6. Plotly muestra las mismas posiciones y añade información al pasar el cursor
fig_beeswarm = go.Figure()
for category_y, especie in enumerate(orden_especies):
    puntos = beeswarm_layout.loc[beeswarm_layout["species"].eq(especie)]
    detalles = [
        [fila.record_id, int(fila.source_row), fila.species]
        for fila in puntos.itertuples(index=False)
    ]
    fig_beeswarm.add_trace(go.Scatter(
        x=puntos["body_mass_g"].tolist(), y=puntos["y"].tolist(),
        mode="markers", name=f"{especie} · n={len(puntos)}",
        marker=dict(size=float(puntos["marker_diameter_px"].iloc[0]),
                    color=colores_especies[especie], line=dict(width=0), opacity=1),
        customdata=detalles,
        hovertemplate="<b>%{customdata[2]}</b><br>" + ETIQUETA_VALOR_SWARM + ": %{x:,." +
                      str(DECIMALES_SWARM) + "f} " + SUFIJO_VALOR_SWARM +
                      "<br>Registro: %{customdata[0]}<br>Fila de origen: %{customdata[1]}<extra></extra>",
    ))
    mediana = float(puntos["body_mass_g"].median())
    fig_beeswarm.add_shape(
        type="line", x0=mediana, x1=mediana, y0=category_y - 0.32, y1=category_y + 0.32,
        xref="x", yref="y", line=dict(color=TEXTO, width=1.5, dash="dot"), layer="below",
    )
    fig_beeswarm.add_annotation(
        x=mediana, y=category_y + 0.42, xref="x", yref="y", showarrow=False,
        text=f"Mediana: {numero_es(mediana, DECIMALES_SWARM)} {SUFIJO_VALOR_SWARM}",
        font=dict(size=12, color=TEXTO),
        bgcolor=FONDO, borderpad=2,
    )
fig_beeswarm.update_layout(
    title=TITULOS["beeswarm"], width=ANCHO, height=ALTO,
    margin={**MARGEN_SWARM, "autoexpand": False}, paper_bgcolor=FONDO, plot_bgcolor=FONDO,
    font=dict(family="Arial, sans-serif", color=TEXTO, size=15), separators=",.",
    xaxis=dict(range=list(rango_x), fixedrange=True, title=UNIDAD_SWARM,
               gridcolor="#D9DFDD", zeroline=False, automargin=False),
    yaxis=dict(range=[len(orden_especies) - 0.5, -0.5], fixedrange=True,
               tickmode="array", tickvals=list(range(len(orden_especies))),
               ticktext=[f"{s} (n={int(swarm['species'].eq(s).sum())})" for s in orden_especies],
               showgrid=False, zeroline=False, automargin=False),
    showlegend=False, hovermode="closest", dragmode=False,
    meta=dict(tool="seaborn.swarmplot → plotly.graph_objects.Scatter",
              placement="Seaborn 0.13.2; get_offsets después de canvas.draw",
              x_preserved=True, positions_depend_on_size=True,
              note=f"No redimensionar: {ANCHO} × {ALTO} píxeles; ejes fijos; desplazamiento vertical sin unidad"),
)
fig_beeswarm


# %% 7. Exportar HTML interactivo, figuras JSON, CSV y tablas legibles
figuras = {"pie": fig_pie, "candlestick": fig_candlestick, "beeswarm": fig_beeswarm}
config_general = dict(displaylogo=False, responsive=True, scrollZoom=False,
                      toImageButtonOptions=dict(format="svg"))
configuraciones = {
    "pie": {**config_general, "modeBarButtonsToRemove": ["select2d", "lasso2d"]},
    "candlestick": config_general,
    "beeswarm": {**config_general, "responsive": False,
                  "modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d",
                                             "zoomOut2d", "autoScale2d", "resetScale2d"]},
}
for nombre, figura in figuras.items():
    figura.write_json(OUTPUT_DIR / f"{nombre}.json", pretty=True)
    # Incluye Plotly.js: el HTML descargado funciona sin cuenta ni conexión.
    figura.write_html(OUTPUT_DIR / f"{nombre}.html", include_plotlyjs=True,
                      full_html=True, config=configuraciones[nombre],
                      div_id=f"pec2-{nombre}")
(OUTPUT_DIR / "plotly_config.json").write_text(
    json.dumps(configuraciones, ensure_ascii=False, indent=2), encoding="utf-8")

pie[["category", "thousands", "share"]].to_csv(OUTPUT_DIR / "datos_pie.csv", index=False)
velas.to_csv(OUTPUT_DIR / "datos_velas.csv", index=False)
swarm.to_csv(OUTPUT_DIR / "datos_beeswarm.csv", index=False)
beeswarm_layout.to_csv(OUTPUT_DIR / "beeswarm_layout.csv", index=False)
resumen_swarm = swarm.groupby("species", sort=False)["body_mass_g"].agg(
    n="count", minimo="min", mediana="median", maximo="max")
resumen_swarm = resumen_swarm.reindex(orden_especies)
resumen_swarm.to_csv(OUTPUT_DIR / "resumen_beeswarm.csv")

texto_fuentes = ("Datos ficticios creados para comprobar la reutilización. No describen observaciones reales."
                if ROTULO_DEMO else
                "Fuentes y licencias: INE, TWSE y Palmer Penguins; consultar README.md del proyecto.")

tablas_html = f"""<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PEC 2 · Datos y resúmenes</title><style>
body{{font-family:Arial,sans-serif;background:{FONDO};color:{TEXTO};margin:32px;line-height:1.5}}
main{{max-width:1100px;margin:auto}}table{{border-collapse:collapse;width:100%;margin:20px 0}}
td,th{{text-align:left;border-bottom:1px solid #ccd6d5;padding:8px}}a{{color:#007F86}}
.scroll{{overflow-x:auto}}summary{{cursor:pointer;font-weight:bold}}</style><main>
<h1>PEC 2 · Datos y resúmenes</h1><p>{html.escape(ROTULO_DEMO or 'Snapshots de datos abiertos · reproducibles sin cuenta')}</p>
<h2>{html.escape(TITULOS['pie'])}</h2><p>El total es {numero_es(pie['thousands'].sum(),1)} {html.escape(UNIDAD_PIE)}.
<a href="datos_pie.csv">Descargar CSV</a> · <a href="pie.html">Abrir gráfico</a></p>
{pie[['category','thousands','share']].to_html(index=False, border=0)}
<h2>{html.escape(TITULOS['candlestick'])}</h2><p>{len(velas)} sesiones; no se rellenan días ausentes.
<a href="datos_velas.csv">Descargar CSV</a> · <a href="candlestick.html">Abrir gráfico</a></p>
<div class="scroll">{velas.to_html(index=False, border=0)}</div>
<h2>{html.escape(TITULOS['beeswarm'])}</h2><p>{len(swarm)} observaciones; {filas_excluidas} masas ausentes excluidas.
<a href="datos_beeswarm.csv">Descargar observaciones</a> · <a href="beeswarm_layout.csv">Coordenadas Seaborn</a>
 · <a href="beeswarm.html">Abrir gráfico</a></p>
{resumen_swarm.to_html(border=0)}<details><summary>Tabla de todas las observaciones</summary>
<div class="scroll">{swarm.to_html(index=False, border=0, na_rep='—')}</div></details>
<p>{html.escape(texto_fuentes)}
El desplazamiento vertical del beeswarm solo evita superposiciones y no representa otra variable.</p>
</main></html>"""
(OUTPUT_DIR / "tablas.html").write_text(tablas_html, encoding="utf-8")

verificacion = dict(
    versions=VERSIONES, demo_label=ROTULO_DEMO or None, input_sha256=huellas_csv,
    pie=dict(categories=len(pie), total=float(pie["thousands"].sum()),
             shares=pie["share"].tolist(), sum_shares=float(pie["share"].sum()),
             legend_can_hide_slices=False),
    candlestick=dict(sessions=len(velas), first_date=fechas[0], last_date=fechas[-1],
                     session_spacing="category/equidistant", ohlc_valid=True),
    beeswarm=dict(input_rows=len(pingüinos_originales), kept_rows=len(swarm),
                  missing_mass_excluded=filas_excluidas, categories=orden_especies,
                  width_px=ANCHO, height_px=ALTO, margin_px=MARGEN_SWARM,
                  x_range=list(rango_x), y_range=[len(orden_especies)-0.5, -0.5],
                  minimum_center_distance_px=distancia_minima_global,
                  placement_warnings=avisos_colocacion, groups=comprobaciones_swarm,
                  responsive=False, axes_fixed=True),
)
(OUTPUT_DIR / "verificacion.json").write_text(
    json.dumps(verificacion, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Exportación terminada: {OUTPUT_DIR}")
print("pie.html · candlestick.html · beeswarm.html · tablas.html · JSON · CSV")
