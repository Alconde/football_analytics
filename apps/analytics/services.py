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
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=player_name,
                line=dict(color='#6366f1', width=2),
                fillcolor='rgba(99, 102, 241, 0.3)',
                marker=dict(size=8, color='#818cf8'),
            )
        )

        fig.update_layout(
            polar=dict(
                bgcolor='rgba(15, 23, 42, 1)',
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor='#334155',
                    linecolor='#334155',
                    tickfont=dict(color='#94a3b8', size=10),
                ),
                angularaxis=dict(
                    gridcolor='#334155',
                    tickfont=dict(color='#f1f5f9', size=12),
                ),
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=50, r=50, t=30, b=30),
            height=450,
            autosize=True,
        )

        return opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False)

    @staticmethod
    def get_match_kpi_trend(labels, xg_values, possession_values, ppda_values, title='Tendencia de KPIs por partido'):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=labels,
                y=xg_values,
                mode='lines+markers',
                name='xG promedio',
                line=dict(color='#38bdf8', width=3),
                marker=dict(size=6),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=labels,
                y=possession_values,
                mode='lines+markers',
                name='Posesión %',
                line=dict(color='#34d399', width=3),
                marker=dict(size=6),
                yaxis='y2',
            )
        )
        fig.add_trace(
            go.Bar(
                x=labels,
                y=ppda_values,
                name='PPDA',
                marker_color='#fbbf24',
                opacity=0.75,
                yaxis='y3',
            )
        )

        fig.update_layout(
            title=dict(text=title, x=0.01, xanchor='left'),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15,23,42,1)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=20, r=20, t=60, b=30),
            xaxis=dict(title='Partidos recientes', showgrid=False),
            yaxis=dict(title='xG promedio', gridcolor='#334155', zerolinecolor='#334155'),
            yaxis2=dict(
                title='Posesión %', overlaying='y', side='right', gridcolor='rgba(0,0,0,0)', zeroline=False
            ),
            yaxis3=dict(
                title='PPDA', anchor='free', overlaying='y', side='right', position=0.95, gridcolor='rgba(0,0,0,0)', zeroline=False
            ),
            height=450,
        )

        return opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False)

    @staticmethod
    def get_kpi_summary_bar(labels, values, title='Resumen KPI promedio'):
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=labels,
                y=values,
                marker_color=['#38bdf8', '#f472b6', '#34d399', '#fbbf24', '#a78bfa'],
                text=[f'{v:.2f}' for v in values],
                textposition='auto',
            )
        )

        fig.update_layout(
            title=dict(text=title, x=0.01, xanchor='left'),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(15,23,42,1)',
            margin=dict(l=20, r=20, t=60, b=30),
            xaxis=dict(title='KPI', tickangle=-45, showgrid=False),
            yaxis=dict(title='Valor promedio', gridcolor='#334155'),
            height=430,
        )

        return opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False)
