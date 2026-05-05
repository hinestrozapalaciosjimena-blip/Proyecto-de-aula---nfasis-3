import sys
print(sys.executable)


import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# ── Cargar y limpiar datos ─────────────────────────────────────────────────────
df = pd.read_csv("pension_dataset.csv", sep=";")

# Limpiar columna Pension_Price (eliminar puntos de miles)
df["Pension_Price"] = (
    df["Pension_Price"].astype(str).str.replace(".", "", regex=False).astype(float)
)

# Crear columna de fecha real
month_map = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4,
    "may": 5, "jun": 6, "jul": 7, "ago": 8,
    "sep": 9, "oct": 10, "nov": 11, "dic": 12
}

df["Month"] = df["Month"].str.lower().str.strip()
df["Month_num"] = df["Month"].map(month_map)
df["Date_dt"] = pd.to_datetime(
    {"year": df["Year"], "month": df["Month_num"], "day": 1}
)
df["YearMonth"] = df["Date_dt"].dt.to_period("M").astype(str)

# Agregaciones mensuales para gráfico de líneas
monthly = (
    df.groupby("YearMonth")
    .agg(
        avg_return=("Fund_Return_Rate", "mean"),
        avg_interest=("Interest_Rate", "mean"),
        avg_inflation=("Inflation_Rate", "mean"),
        avg_stock=("Stock_Index", "mean"),
        count=("Pension_Price", "count"),
        avg_pension=("Pension_Price", "mean"),
    )
    .reset_index()
)
monthly["Date_dt"] = pd.to_datetime(monthly["YearMonth"])
monthly = monthly.sort_values("Date_dt")

categories = df["Pension_Category"].unique().tolist()
risk_levels = df["Risk_Tolerance"].unique().tolist()
emp_status = df["Employment_Status"].unique().tolist()
years = sorted(df["Year"].unique())

# ── Paleta y estilos ───────────────────────────────────────────────────────────
BG_DARK   = "#0d1117"
BG_CARD   = "#161b22"
BG_CARD2  = "#1c2230"
BORDER    = "#30363d"
TEXT_PRI  = "#e6edf3"
TEXT_SEC  = "#8b949e"
ACCENT1   = "#58a6ff"   # azul
ACCENT2   = "#3fb950"   # verde
ACCENT3   = "#f78166"   # rojo
ACCENT4   = "#d2a8ff"   # violeta
ACCENT5   = "#ffa657"   # naranja

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD2,
        font=dict(family="IBM Plex Mono, monospace", color=TEXT_PRI, size=11),
        title=dict(font=dict(family="IBM Plex Mono, monospace", color=TEXT_PRI, size=13)),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_SEC)),
        margin=dict(t=50, b=40, l=50, r=20),
        colorway=[ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5],
    )
)

CARD_STYLE = {
    "background": BG_CARD,
    "border": f"1px solid {BORDER}",
    "borderRadius": "10px",
    "padding": "16px",
    "height": "100%",
    "boxSizing": "border-box",
}

LABEL_STYLE = {
    "color": TEXT_SEC,
    "fontFamily": "IBM Plex Mono, monospace",
    "fontSize": "11px",
    "marginBottom": "4px",
    "display": "block",
    "letterSpacing": "0.05em",
    "textTransform": "uppercase",
}

DROPDOWN_STYLE = {
    "backgroundColor": BG_CARD2,
    "border": f"1px solid {BORDER}",
    "borderRadius": "6px",
    "color": TEXT_PRI,
    "fontFamily": "IBM Plex Mono, monospace",
    "fontSize": "12px",
}

# ── App ────────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "Global Pension Performance Dashboard"

app.layout = html.Div(
    style={
        "backgroundColor": BG_DARK,
        "minHeight": "100vh",
        "fontFamily": "IBM Plex Mono, monospace",
        "color": TEXT_PRI,
        "padding": "20px 28px",
    },
    children=[
        # ── Header ────────────────────────────────────────────────────────────
        html.Div(
            style={"marginBottom": "24px"},
            children=[
                html.Div(
                    style={"display": "flex", "alignItems": "center", "gap": "12px", "marginBottom": "6px"},
                    children=[
                        html.Span("◈", style={"color": ACCENT1, "fontSize": "24px"}),
                        html.H1(
                            "Global Pension Performance Dashboard",
                            style={
                                "margin": "0",
                                "fontSize": "22px",
                                "fontWeight": "700",
                                "letterSpacing": "-0.02em",
                                "color": TEXT_PRI,
                            },
                        ),
                    ],
                ),
                html.P(
                    "Indicadores económicos y desempeño de fondos de pensión · 2005–2024",
                    style={"color": TEXT_SEC, "margin": "0", "fontSize": "12px", "letterSpacing": "0.04em"},
                ),
            ],
        ),

        # ── Controles globales ─────────────────────────────────────────────────
        html.Div(
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "12px",
                "marginBottom": "20px",
                "background": BG_CARD,
                "border": f"1px solid {BORDER}",
                "borderRadius": "10px",
                "padding": "16px",
            },
            children=[
                # Rango de años
                html.Div([
                    html.Label("RANGO DE AÑOS", style=LABEL_STYLE),
                    dcc.RangeSlider(
                        id="year-range",
                        min=min(years), max=max(years),
                        value=[2015, 2024],
                        marks={y: {"label": str(y), "style": {"color": TEXT_SEC, "fontSize": "10px"}}
                               for y in [2005, 2010, 2015, 2020, 2024]},
                        step=1,
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                ]),
                # Categoría
                html.Div([
                    html.Label("CATEGORÍA DE PENSIÓN", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="category-filter",
                        options=[{"label": "Todas", "value": "ALL"}]
                                + [{"label": c, "value": c} for c in sorted(categories)],
                        value="ALL",
                        clearable=False,
                        style=DROPDOWN_STYLE,
                    ),
                ]),
                # Tolerancia al riesgo
                html.Div([
                    html.Label("TOLERANCIA AL RIESGO", style=LABEL_STYLE),
                    dcc.Dropdown(
                        id="risk-filter",
                        options=[{"label": "Todas", "value": "ALL"}]
                                + [{"label": r, "value": r} for r in sorted(risk_levels)],
                        value="ALL",
                        clearable=False,
                        style=DROPDOWN_STYLE,
                    ),
                ]),
                # Estado laboral
                html.Div([
                    html.Label("ESTADO LABORAL", style=LABEL_STYLE),
                    dcc.Checklist(
                        id="employment-filter",
                        options=[{"label": f"  {e}", "value": e} for e in sorted(emp_status)],
                        value=emp_status,
                        inline=True,
                        style={"color": TEXT_SEC, "fontSize": "12px", "marginTop": "6px"},
                        inputStyle={"marginRight": "4px", "accentColor": ACCENT1},
                    ),
                ]),
            ],
        ),

        # ── Gráficos – Fila 1 ─────────────────────────────────────────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"},
            children=[
                # Gráfico 1: Línea con range-slider
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "10px"},
                            children=[
                                html.Div([
                                    html.Span("01", style={"color": ACCENT1, "fontSize": "10px", "marginRight": "8px"}),
                                    html.Span("Evolución Temporal de Indicadores Económicos",
                                              style={"fontSize": "12px", "fontWeight": "600"}),
                                ]),
                                html.Div([
                                    html.Label("MÉTRICA", style={**LABEL_STYLE, "display": "inline", "marginRight": "6px"}),
                                    dcc.Dropdown(
                                        id="line-metric",
                                        options=[
                                            {"label": "Retorno del Fondo (%)", "value": "avg_return"},
                                            {"label": "Tasa de Interés (%)", "value": "avg_interest"},
                                            {"label": "Inflación (%)", "value": "avg_inflation"},
                                            {"label": "Índice Bursátil", "value": "avg_stock"},
                                        ],
                                        value="avg_return",
                                        clearable=False,
                                        style={**DROPDOWN_STYLE, "width": "200px"},
                                    ),
                                ], style={"display": "flex", "alignItems": "center", "gap": "6px"}),
                            ],
                        ),
                        html.Div([
                            html.Label("SELECTOR DE RANGO", style=LABEL_STYLE),
                            dcc.RadioItems(
                                id="range-selector",
                                options=[
                                    {"label": " Mes", "value": "month"},
                                    {"label": " Semestre", "value": "semester"},
                                    {"label": " Año", "value": "year"},
                                ],
                                value="year",
                                inline=True,
                                style={"color": TEXT_SEC, "fontSize": "11px", "marginBottom": "8px"},
                                inputStyle={"marginRight": "4px", "marginLeft": "8px", "accentColor": ACCENT1},
                            ),
                        ]),
                        dcc.Graph(id="line-chart", style={"height": "300px"}, config={"displayModeBar": False}),
                    ],
                ),

                # Gráfico 2: Barras / Boxplot / Violin con botón de cambio
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "10px"},
                            children=[
                                html.Div([
                                    html.Span("02", style={"color": ACCENT2, "fontSize": "10px", "marginRight": "8px"}),
                                    html.Span("Distribución del Precio de Pensión",
                                              style={"fontSize": "12px", "fontWeight": "600"}),
                                ]),
                                html.Div([
                                    html.Label("TIPO DE GRÁFICO", style={**LABEL_STYLE, "display": "inline", "marginRight": "6px"}),
                                    dcc.Dropdown(
                                        id="chart-type-selector",
                                        options=[
                                            {"label": "Caja (Box)", "value": "box"},
                                            {"label": "Violín", "value": "violin"},
                                            {"label": "Barras", "value": "bar"},
                                        ],
                                        value="box",
                                        clearable=False,
                                        style={**DROPDOWN_STYLE, "width": "150px"},
                                    ),
                                ], style={"display": "flex", "alignItems": "center", "gap": "6px"}),
                            ],
                        ),
                        html.Div([
                            html.Label("FONDO DEL GRÁFICO", style=LABEL_STYLE),
                            dcc.RadioItems(
                                id="bg-selector",
                                options=[
                                    {"label": " Oscuro", "value": "dark"},
                                    {"label": " Neutro", "value": "neutral"},
                                    {"label": " Claro", "value": "light"},
                                ],
                                value="dark",
                                inline=True,
                                style={"color": TEXT_SEC, "fontSize": "11px", "marginBottom": "8px"},
                                inputStyle={"marginRight": "4px", "marginLeft": "8px", "accentColor": ACCENT2},
                            ),
                        ]),
                        dcc.Graph(id="dist-chart", style={"height": "300px"}, config={"displayModeBar": False}),
                    ],
                ),
            ],
        ),

        # ── Gráficos – Fila 2 ─────────────────────────────────────────────────
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"},
            children=[
                # Gráfico 3: Scatter
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "10px"},
                            children=[
                                html.Div([
                                    html.Span("03", style={"color": ACCENT3, "fontSize": "10px", "marginRight": "8px"}),
                                    html.Span("Relación Inflación vs. Retorno del Fondo",
                                              style={"fontSize": "12px", "fontWeight": "600"}),
                                ]),
                                html.Div([
                                    html.Label("COLOR POR", style={**LABEL_STYLE, "display": "inline", "marginRight": "6px"}),
                                    dcc.Dropdown(
                                        id="scatter-color",
                                        options=[
                                            {"label": "Categoría", "value": "Pension_Category"},
                                            {"label": "Riesgo", "value": "Risk_Tolerance"},
                                            {"label": "Empleo", "value": "Employment_Status"},
                                        ],
                                        value="Pension_Category",
                                        clearable=False,
                                        style={**DROPDOWN_STYLE, "width": "150px"},
                                    ),
                                ], style={"display": "flex", "alignItems": "center", "gap": "6px"}),
                            ],
                        ),
                        dcc.Graph(id="scatter-chart", style={"height": "330px"}, config={"displayModeBar": False}),
                    ],
                ),

                # Gráfico 4: Mapa de calor / Heatmap anual
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.Div(
                            style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "10px"},
                            children=[
                                html.Div([
                                    html.Span("04", style={"color": ACCENT4, "fontSize": "10px", "marginRight": "8px"}),
                                    html.Span("Mapa de Calor: Retorno Promedio Año-Mes",
                                              style={"fontSize": "12px", "fontWeight": "600"}),
                                ]),
                                html.Div([
                                    html.Label("MÉTRICA HEATMAP", style={**LABEL_STYLE, "display": "inline", "marginRight": "6px"}),
                                    dcc.Dropdown(
                                        id="heatmap-metric",
                                        options=[
                                            {"label": "Retorno (%)", "value": "Fund_Return_Rate"},
                                            {"label": "Inflación (%)", "value": "Inflation_Rate"},
                                            {"label": "Tasa Interés (%)", "value": "Interest_Rate"},
                                            {"label": "Volatilidad", "value": "Market_Volatility"},
                                        ],
                                        value="Fund_Return_Rate",
                                        clearable=False,
                                        style={**DROPDOWN_STYLE, "width": "180px"},
                                    ),
                                ], style={"display": "flex", "alignItems": "center", "gap": "6px"}),
                            ],
                        ),
                        dcc.Graph(id="heatmap-chart", style={"height": "330px"}, config={"displayModeBar": False}),
                    ],
                ),
            ],
        ),

        # ── Footer ────────────────────────────────────────────────────────────
        html.Div(
            style={"marginTop": "20px", "textAlign": "center", "color": TEXT_SEC, "fontSize": "10px"},
            children=[
                html.Span("Global Pension Performance & Economic Indicators · Kaggle Dataset · 2005–2024"),
            ],
        ),
    ],
)


# ── Helpers ────────────────────────────────────────────────────────────────────
def filter_df(year_range, category, risk, employment):
    dff = df[df["Year"].between(year_range[0], year_range[1])]
    if category != "ALL":
        dff = dff[dff["Pension_Category"] == category]
    if risk != "ALL":
        dff = dff[dff["Risk_Tolerance"] == risk]
    if employment:
        dff = dff[dff["Employment_Status"].isin(employment)]
    return dff


def apply_template(fig, bg="dark"):
    bg_map = {"dark": BG_CARD2, "neutral": "#1e2a3a", "light": "#e8edf3"}
    paper_map = {"dark": BG_CARD, "neutral": "#16202e", "light": "#f0f4f8"}
    font_map = {"dark": TEXT_PRI, "neutral": TEXT_PRI, "light": "#1a2332"}
    fig.update_layout(
        paper_bgcolor=paper_map.get(bg, BG_CARD),
        plot_bgcolor=bg_map.get(bg, BG_CARD2),
        font=dict(family="IBM Plex Mono, monospace", color=font_map.get(bg, TEXT_PRI), size=10),
        xaxis=dict(gridcolor=BORDER, linecolor=BORDER),
        yaxis=dict(gridcolor=BORDER, linecolor=BORDER),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
        margin=dict(t=30, b=40, l=50, r=20),
        colorway=[ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5],
    )
    return fig


# ── Callback 1: Gráfico de líneas ─────────────────────────────────────────────
@app.callback(
    Output("line-chart", "figure"),
    Input("year-range", "value"),
    Input("line-metric", "value"),
    Input("range-selector", "value"),
    Input("category-filter", "value"),
    Input("risk-filter", "value"),
    Input("employment-filter", "value"),
)
def update_line(year_range, metric, range_sel, category, risk, employment):
    dff = filter_df(year_range, category, risk, employment)
    metric_labels = {
        "avg_return": "Retorno del Fondo (%)",
        "avg_interest": "Tasa de Interés (%)",
        "avg_inflation": "Inflación (%)",
        "avg_stock": "Índice Bursátil",
    }

    if range_sel == "month":
        grp = dff.groupby("YearMonth").agg(**{metric: (metric.replace("avg_", ""), "mean")}).reset_index()
        grp["Date_dt"] = pd.to_datetime(grp["YearMonth"])
        grp = grp.sort_values("Date_dt")
        x_col, y_col = "YearMonth", metric
    elif range_sel == "semester":
        dff2 = dff.copy()
        dff2["Semester"] = dff2["Year"].astype(str) + "-S" + ((dff2["Month_num"] > 6).astype(int) + 1).astype(str)
        raw_col = metric.replace("avg_", "")
        raw_map = {
            "avg_return": "Fund_Return_Rate",
            "avg_interest": "Interest_Rate",
            "avg_inflation": "Inflation_Rate",
            "avg_stock": "Stock_Index",
        }
        actual_col = raw_map[metric]
        grp = dff2.groupby("Semester")[actual_col].mean().reset_index()
        grp.columns = ["Semester", metric]
        grp = grp.sort_values("Semester")
        x_col, y_col = "Semester", metric
    else:  # year
        raw_map = {
            "avg_return": "Fund_Return_Rate",
            "avg_interest": "Interest_Rate",
            "avg_inflation": "Inflation_Rate",
            "avg_stock": "Stock_Index",
        }
        actual_col = raw_map[metric]
        grp = dff.groupby("Year")[actual_col].mean().reset_index()
        grp.columns = ["Year", metric]
        grp = grp.sort_values("Year")
        x_col, y_col = "Year", metric

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=grp[x_col], y=grp[y_col],
        mode="lines+markers",
        line=dict(color=ACCENT1, width=2),
        marker=dict(size=4, color=ACCENT1),
        fill="tozeroy",
        fillcolor=f"rgba(88,166,255,0.08)",
        name=metric_labels.get(metric, metric),
    ))

    if range_sel == "month":
        fig.update_xaxes(
            rangeslider=dict(visible=True, bgcolor=BG_CARD, thickness=0.08),
            type="category",
        )

    fig.update_layout(
        xaxis_title="",
        yaxis_title=metric_labels.get(metric, metric),
        showlegend=False,
    )
    return apply_template(fig)


# ── Callback 2: Gráfico de distribución ───────────────────────────────────────
@app.callback(
    Output("dist-chart", "figure"),
    Input("year-range", "value"),
    Input("chart-type-selector", "value"),
    Input("bg-selector", "value"),
    Input("category-filter", "value"),
    Input("risk-filter", "value"),
    Input("employment-filter", "value"),
)
def update_dist(year_range, chart_type, bg, category, risk, employment):
    dff = filter_df(year_range, category, risk, employment)
    cats = sorted(dff["Pension_Category"].unique())
    colors = [ACCENT1, ACCENT2, ACCENT3, ACCENT4, ACCENT5]

    fig = go.Figure()

    if chart_type == "box":
        for i, cat in enumerate(cats):
            sub = dff[dff["Pension_Category"] == cat]["Pension_Price"] / 1e9
            fig.add_trace(go.Box(
                y=sub, name=cat,
                marker_color=colors[i % len(colors)],
                line=dict(width=1.5),
                boxmean=True,
            ))
        fig.update_layout(yaxis_title="Precio de Pensión (Miles de Millones)")

    elif chart_type == "violin":
        for i, cat in enumerate(cats):
            sub = dff[dff["Pension_Category"] == cat]["Pension_Price"] / 1e9
            fig.add_trace(go.Violin(
                y=sub, name=cat,
                fillcolor=colors[i % len(colors)],
                line_color=colors[i % len(colors)],
                opacity=0.7,
                box_visible=True,
                meanline_visible=True,
            ))
        fig.update_layout(yaxis_title="Precio de Pensión (Miles de Millones)")

    else:  # bar
        avg = dff.groupby("Pension_Category")["Pension_Price"].mean() / 1e9
        avg = avg.sort_values(ascending=False)
        for i, (cat, val) in enumerate(avg.items()):
            fig.add_trace(go.Bar(
                x=[cat], y=[val],
                name=cat,
                marker_color=colors[i % len(colors)],
                marker_line_width=0,
            ))
        fig.update_layout(yaxis_title="Precio Promedio (Miles de Millones)", showlegend=False)

    return apply_template(fig, bg)


# ── Callback 3: Scatter ────────────────────────────────────────────────────────
@app.callback(
    Output("scatter-chart", "figure"),
    Input("year-range", "value"),
    Input("scatter-color", "value"),
    Input("category-filter", "value"),
    Input("risk-filter", "value"),
    Input("employment-filter", "value"),
)
def update_scatter(year_range, color_col, category, risk, employment):
    dff = filter_df(year_range, category, risk, employment)
    sample = dff.sample(min(2000, len(dff)), random_state=42)

    color_map = {
        "Low_Value": ACCENT3, "Moderate_Value": ACCENT1, "High_Value": ACCENT2,
        "Low": ACCENT3, "Medium": ACCENT1, "High": ACCENT2,
        "Employed": ACCENT2, "Unemployed": ACCENT3,
    }

    fig = go.Figure()
    for val in sorted(sample[color_col].unique()):
        sub = sample[sample[color_col] == val]
        fig.add_trace(go.Scatter(
            x=sub["Inflation_Rate"], y=sub["Fund_Return_Rate"],
            mode="markers",
            marker=dict(
                size=5,
                color=color_map.get(val, ACCENT1),
                opacity=0.55,
                line=dict(width=0),
            ),
            name=val,
        ))

    fig.update_layout(
        xaxis_title="Tasa de Inflación (%)",
        yaxis_title="Retorno del Fondo (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return apply_template(fig)


# ── Callback 4: Heatmap ────────────────────────────────────────────────────────
@app.callback(
    Output("heatmap-chart", "figure"),
    Input("year-range", "value"),
    Input("heatmap-metric", "value"),
    Input("category-filter", "value"),
    Input("risk-filter", "value"),
    Input("employment-filter", "value"),
)
def update_heatmap(year_range, metric, category, risk, employment):
    dff = filter_df(year_range, category, risk, employment)
    pivot = dff.groupby(["Year", "Month_num"])[metric].mean().reset_index()
    pivot_table = pivot.pivot(index="Month_num", columns="Year", values=metric)

    month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                   "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    y_labels = [month_names[int(m) - 1] for m in pivot_table.index]

    metric_labels = {
        "Fund_Return_Rate": "Retorno del Fondo (%)",
        "Inflation_Rate": "Inflación (%)",
        "Interest_Rate": "Tasa de Interés (%)",
        "Market_Volatility": "Volatilidad de Mercado",
    }

    fig = go.Figure(go.Heatmap(
        z=pivot_table.values,
        x=[str(y) for y in pivot_table.columns],
        y=y_labels,
        colorscale=[
            [0.0, "#0d1117"],
            [0.25, "#1f4e8c"],
            [0.5, "#58a6ff"],
            [0.75, "#3fb950"],
            [1.0, "#ffa657"],
        ],
        hoverongaps=False,
        colorbar=dict(
            thickness=12,
            len=0.9,
            tickfont=dict(size=9, color=TEXT_SEC),
            outlinewidth=0,
        ),
    ))

    fig.update_layout(
        xaxis_title="Año",
        yaxis_title="Mes",
        xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
        yaxis=dict(tickfont=dict(size=9)),
    )
    return apply_template(fig)

if __name__ == "__main__":
    app.run(debug=True)