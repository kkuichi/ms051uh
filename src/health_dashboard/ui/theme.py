import plotly.graph_objects as go
import plotly.io as pio

STAGE_COLORS = {
    "Core": "#4E79A7",
    "Deep": "#1D3557",
    "REM": "#A23B72",
    "Awake": "#F18F01",
    "InBed": "#C9ADA7",
    "Other": "#999999",
    "Wake/Out-of-sleep": "#E76F51",
}


def register_plotly_template() -> None:
    health_template = go.layout.Template(
        layout=go.Layout(
            colorway=[
                "#4E79A7",
                "#1D3557",
                "#A23B72",
                "#F18F01",
                "#C9ADA7",
            ],
            font=dict(family="Segoe UI, sans-serif", size=12, color="#333333"),
            title=dict(font=dict(size=16, color="#333333"), x=0.5, xanchor="center"),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="#E8E8E8",
                showline=True,
                linewidth=1,
                linecolor="#999999",
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="#E8E8E8",
                showline=True,
                linewidth=1,
                linecolor="#999999",
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=60, r=40, t=60, b=40),
        )
    )

    
    pio.templates["health"] = health_template

    pio.templates.default = "health"
