"""Plotly visualization utilities for Zawaj — Pink Wedding Theme."""

import plotly.graph_objects as go
from config import COLORS

# Core palette
ROSE = COLORS["rose"]
BLUSH = COLORS["blush"]
GOLD = COLORS["gold"]
DEEP = COLORS["deep"]
SOFT = COLORS["soft_pink"]
MUTE = COLORS["mute"]
WHITE = COLORS["white"]

# Status colors re-mapped to soft wedding tones
OK = "#6BAF73"       # green
WARN = "#E8A846"     # amber
BAD = "#D4577A"      # rose

BASE_LAYOUT = dict(
    font=dict(family="Poppins, sans-serif", color=DEEP),
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(255,255,255,0)",
    margin=dict(l=40, r=20, t=50, b=40),
)


def _score_color(score):
    return OK if score >= 70 else (WARN if score >= 45 else BAD)


def create_gauge_chart(score, title="Compatibility"):
    color = _score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "%", "font": {"size": 46, "color": DEEP, "family": "Playfair Display"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": MUTE,
                     "tickfont": {"color": MUTE, "size": 10}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": WHITE,
            "borderwidth": 0,
            "steps": [
                {"range": [0, 45], "color": "#FFE8EE"},
                {"range": [45, 70], "color": "#FFF2D6"},
                {"range": [70, 100], "color": "#E4F3E7"},
            ],
            "threshold": {
                "line": {"color": DEEP, "width": 3},
                "thickness": 0.85,
                "value": score,
            },
        },
        title={"text": f"<span style='color:{DEEP};'>{title}</span>",
               "font": {"size": 16, "family": "Playfair Display"}},
    ))
    fig.update_layout(height=260, **BASE_LAYOUT)
    return fig


def create_domain_radar(domain_scores):
    domains = [d.replace("_", " ").title() for d in domain_scores.keys()]
    scores = list(domain_scores.values())
    domains.append(domains[0])
    scores.append(scores[0])

    fig = go.Figure(go.Scatterpolar(
        r=scores,
        theta=domains,
        fill="toself",
        fillcolor="rgba(212, 87, 122, 0.22)",
        line=dict(color=ROSE, width=2.5),
        marker=dict(size=10, color=DEEP, line=dict(color=GOLD, width=1.5)),
        hovertemplate="<b>%{theta}</b><br>%{r}%<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=BLUSH,
                            tickfont=dict(color=MUTE, size=10)),
            angularaxis=dict(gridcolor=BLUSH, tickfont=dict(color=DEEP, size=11)),
            bgcolor=SOFT,
        ),
        title={"text": "Domain Alignment", "font": {"size": 16, "family": "Playfair Display", "color": DEEP}},
        height=420,
        showlegend=False,
        **BASE_LAYOUT,
    )
    return fig


def create_domain_bar_chart(domain_scores):
    domains = [d.replace("_", " ").title() for d in domain_scores.keys()]
    scores = list(domain_scores.values())
    colors = [_score_color(s) for s in scores]

    fig = go.Figure(go.Bar(
        x=scores, y=domains, orientation="h",
        marker=dict(color=colors, line=dict(color=WHITE, width=1)),
        text=[f"{s:.0f}%" for s in scores],
        textposition="outside",
        textfont=dict(color=DEEP, size=12, family="Poppins"),
        hovertemplate="<b>%{y}</b><br>%{x}%<extra></extra>",
    ))
    fig.update_layout(
        title={"text": "Domain Compatibility", "font": {"size": 16, "family": "Playfair Display", "color": DEEP}},
        xaxis=dict(title="", range=[0, 110], gridcolor=BLUSH, zerolinecolor=BLUSH,
                   tickfont=dict(color=MUTE)),
        yaxis=dict(autorange="reversed", gridcolor=BLUSH, tickfont=dict(color=DEEP, size=12)),
        height=380,
        bargap=0.35,
        **BASE_LAYOUT,
    )
    return fig


def create_ensemble_breakdown(breakdown):
    labels = list(breakdown.keys())
    contributions = [v["contribution"] for v in breakdown.values()]
    weights = [v["weight"] for v in breakdown.values()]
    palette = [ROSE, GOLD, DEEP]

    fig = go.Figure()
    for i, (label, contrib) in enumerate(zip(labels, contributions)):
        fig.add_trace(go.Bar(
            name=f"{label} ({weights[i]:.0%})",
            x=[contrib], y=["Final"],
            orientation="h",
            marker=dict(color=palette[i % len(palette)], line=dict(color=WHITE, width=2)),
            text=f"{contrib:.1f}",
            textposition="inside",
            textfont=dict(color=WHITE, size=13, family="Poppins"),
            hovertemplate=f"<b>{label}</b><br>Contribution: %{{x}}<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack",
        title={"text": "Score Breakdown", "font": {"size": 16, "family": "Playfair Display", "color": DEEP}},
        xaxis=dict(range=[0, 100], gridcolor=BLUSH, tickfont=dict(color=MUTE)),
        yaxis=dict(showticklabels=False),
        height=190,
        legend=dict(orientation="h", yanchor="bottom", y=1.15, x=0,
                    font=dict(color=DEEP, size=11, family="Poppins"),
                    bgcolor="rgba(255,255,255,0)"),
        **BASE_LAYOUT,
    )
    return fig


def create_conflict_chart(conflicts):
    if not conflicts:
        fig = go.Figure()
        fig.add_annotation(text="No major conflicts detected", showarrow=False,
                           font=dict(size=16, color=DEEP, family="Playfair Display"))
        fig.update_layout(height=200, **BASE_LAYOUT)
        return fig

    titles = [c["title"] for c in conflicts]
    severities = [c["distance"] * 100 for c in conflicts]
    resolutions = [c["resolution_probability"] for c in conflicts]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Conflict Severity", x=titles, y=severities,
        marker=dict(color=ROSE, line=dict(color=WHITE, width=1.5)),
        text=[f"{s:.0f}%" for s in severities], textposition="outside",
        textfont=dict(color=DEEP, size=11),
    ))
    fig.add_trace(go.Bar(
        name="Resolution Probability", x=titles, y=resolutions,
        marker=dict(color=GOLD, line=dict(color=WHITE, width=1.5)),
        text=[f"{s:.0f}%" for s in resolutions], textposition="outside",
        textfont=dict(color=DEEP, size=11),
    ))
    fig.update_layout(
        barmode="group",
        title={"text": "Conflict Analysis", "font": {"size": 16, "family": "Playfair Display", "color": DEEP}},
        yaxis=dict(title="%", range=[0, 115], gridcolor=BLUSH, tickfont=dict(color=MUTE)),
        xaxis=dict(tickangle=-25, tickfont=dict(color=DEEP, size=11)),
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.05,
                    font=dict(color=DEEP, family="Poppins")),
        **BASE_LAYOUT,
    )
    return fig


def create_personality_chart(personality_scores):
    traits = [t.title() for t in personality_scores.keys()]
    scores = list(personality_scores.values())
    colors = [_score_color(s) for s in scores]

    fig = go.Figure(go.Bar(
        x=traits, y=scores,
        marker=dict(color=colors, line=dict(color=WHITE, width=1.5)),
        text=[f"{s:.0f}%" for s in scores],
        textposition="outside",
        textfont=dict(color=DEEP, size=12, family="Poppins"),
    ))
    fig.update_layout(
        title={"text": "Personality Compatibility", "font": {"size": 16, "family": "Playfair Display", "color": DEEP}},
        yaxis=dict(range=[0, 115], gridcolor=BLUSH, tickfont=dict(color=MUTE)),
        xaxis=dict(tickfont=dict(color=DEEP, size=11)),
        height=320,
        bargap=0.4,
        **BASE_LAYOUT,
    )
    return fig


def create_triangle_chart(inlaw_score, contradictions_count, total_items=7):
    """Donut chart showing alignment vs friction in the triangle."""
    alignment = inlaw_score
    friction = max(0, 100 - alignment)

    fig = go.Figure(go.Pie(
        labels=["Aligned", "Friction Risk"],
        values=[alignment, friction],
        hole=0.68,
        marker=dict(colors=[ROSE, BLUSH], line=dict(color=WHITE, width=3)),
        textinfo="percent",
        textfont=dict(family="Poppins", size=13, color=WHITE),
        hovertemplate="<b>%{label}</b>: %{value:.1f}%<extra></extra>",
    ))
    fig.add_annotation(
        text=f"<b>{alignment:.0f}%</b><br><span style='font-size:11px;color:{MUTE};'>Alignment</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(family="Playfair Display", size=28, color=DEEP),
    )
    fig.update_layout(
        title={"text": "Family Triangle Alignment",
               "font": {"size": 16, "family": "Playfair Display", "color": DEEP}},
        height=320,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15,
                    font=dict(color=DEEP, family="Poppins")),
        **BASE_LAYOUT,
    )
    return fig
