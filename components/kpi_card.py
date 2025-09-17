from dash import html

def KPI(label: str, value, id=None, help_text=None):
    return html.Div(className='card kpi', children=[
        html.Div(label, className='label'),
        html.Div(str(value), className='value', id=id) if id else html.Div(str(value), className='value'),
        html.Div(help_text, className='help') if help_text else None
    ])
