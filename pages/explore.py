from dash import html, dcc

layout = html.Div(className='container', children=[
    html.Div(className='grid', children=[
        html.Div(className='card', children=[
            html.H3('Explore'),
            html.P('Sandbox page for ad-hoc comparisons and what-if toggles.'),
            dcc.Markdown('''**Ideas**\n- Cohort picker with retention heatmap\n- Small-multiples by region\n- A vs B comparison\n- Explain-this-card drawer''')
        ], style={'gridColumn':'span 12'})
    ])
])
