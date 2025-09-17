import dash
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import pandas as pd
from utils.data_loader import load_csv

app = Dash(__name__, suppress_callback_exceptions=True, title='Vibeathon Dash')
server = app.server

app.layout = html.Div(children=[
    html.Div(className='header', children=[
        html.Div([html.A('Vibeathon Dash', href='/', className='brand')]),
        html.Div(className='controls', children=[
            dcc.Link('Home', href='/', className='link'),
            dcc.Link('Explore', href='/explore', className='link'),
            dcc.Link('About', href='/about', className='link'),
        ]),
    ]),
    dcc.Location(id='url'),
    html.Div(id='page-content'),
    html.Div(className='footer', children='© 2025 — Dash scaffold')
])


def serve_layout(pathname: str):
    if pathname == '/explore':
        from pages import explore
        return explore.layout
    if pathname == '/about':
        from pages import about
        return about.layout
    from pages import home
    return home.layout

@callback(Output('page-content','children'), Input('url','pathname'))
def render_page(pathname):
    return serve_layout(pathname)

@callback(
    Output('global-state','data'),
    Input('region-dd','value'),
    Input('category-dd','value'),
    Input('date-range','start_date'),
    Input('date-range','end_date'),
    prevent_initial_call=True
)
def update_state(regions, categories, start, end):
    return {'regions': regions, 'categories': categories, 'start': start, 'end': end}

@callback(
    Output('kpi-total','children'),
    Output('kpi-avg','children'),
    Output('kpi-rows','children'),
    Output('kpi-regions','children'),
    Output('timeseries','figure'),
    Output('bar','figure'),
    Output('scatter','figure'),
    Output('heatmap','figure'),
    Input('global-state','data')
)
def refresh_cards(state):
    df = load_csv('data/sample.csv')
    if state:
        if state.get('regions'):
            df = df[df['region'].isin(state['regions'])]
        if state.get('categories'):
            df = df[df['category'].isin(state['categories'])]
        if state.get('start') and state.get('end'):
            df = df[(df['date'] >= pd.to_datetime(state['start'])) & (df['date'] <= pd.to_datetime(state['end']))]
    total = int(df['value'].sum()) if not df.empty else 0
    avg = round(float(df['score'].mean()),2) if not df.empty else 0
    rows = len(df)
    regions = ', '.join(sorted(df['region'].unique())) if not df.empty else '—'

    ts = px.line(df.groupby('date', as_index=False)['value'].sum(), x='date', y='value', markers=True, title='Value over time')
    bar = px.bar(df.groupby('region', as_index=False)['value'].sum(), x='region', y='value', title='By region')
    scatter = px.scatter(df, x='value', y='score', color='category', hover_data=['region','date'], title='Value vs Score')
    pivot = df.pivot_table(index='region', columns='category', values='value', aggfunc='mean').fillna(0)
    heatmap = px.imshow(pivot, labels=dict(x='Category', y='Region', color='Avg Value'), title='Heatmap: Region x Category')
    for fig in (ts, bar, scatter, heatmap):
        fig.update_layout(template='plotly_dark', height=340, margin=dict(l=20,r=20,t=50,b=30))
    return str(total), str(avg), str(rows), regions, ts, bar, scatter, heatmap

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
