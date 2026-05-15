import plotly.graph_objects as go
import plotly.offline as opy

class PlotlyService:
    @staticmethod
    def get_player_radar(stats_dict, player_name):
        categories = list(stats_dict.keys())
        values = list(stats_dict.values())

        # Cerrar el radar repitiendo el primer valor
        categories += [categories[0]]
        values += [values[0]]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=player_name,
            line=dict(color='#6366f1', width=2),
            fillcolor='rgba(99, 102, 241, 0.3)',
            marker=dict(size=8, color='#818cf8')
        ))

        fig.update_layout(
            polar=dict(
                bgcolor="rgba(15, 23, 42, 1)",
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor="#334155",
                    linecolor="#334155",
                    tickfont=dict(color="#94a3b8", size=10)
                ),
                angularaxis=dict(
                    gridcolor="#334155",
                    tickfont=dict(color="#f1f5f9", size=12)
                )
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=50, r=50, t=30, b=30),
            height=450,
            autosize=True
        )

        return opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False)