from dash import html, dcc

layout = html.Div(className='container', children=[
    html.Div(className='card', children=[
        html.H3('About this app'),
        dcc.Markdown('''Built with **Dash** + **Plotly**, optimized for dark mode and keyboard accessibility.''')
    ])
])
