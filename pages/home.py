from dash import html, dcc
import plotly.express as px
from utils.data_loader import load_csv
from components.kpi_card import KPI

df = load_csv('data/sample.csv')

layout = html.Div(className='container', children=[
    html.Div(className='grid', children=[
        html.Div(className='card', children=[
            html.Div('Quick Filters', className='label'),
            html.Div(className='controls', children=[
                dcc.Dropdown(id='region-dd', options=[{'label':r,'value':r} for r in sorted(df['region'].unique())],
                             value=sorted(df['region'].unique()), multi=True, placeholder='Region'),
                dcc.Dropdown(id='category-dd', options=[{'label':c,'value':c} for c in sorted(df['category'].unique())],
                             value=sorted(df['category'].unique()), multi=True, placeholder='Category'),
                dcc.DatePickerRange(id='date-range', start_date=df['date'].min(), end_date=df['date'].max()),
            ]),
            dcc.Store(id='global-state')
        ], style={'gridColumn':'span 12'}),

        html.Div(className='card', children=[
            html.Div('KPI Strip', className='label'),
            html.Div(className='grid', children=[
                html.Div(KPI('Total Value', '—', id='kpi-total'), style={'gridColumn':'span 3'}),
                html.Div(KPI('Avg Score', '—', id='kpi-avg'), style={'gridColumn':'span 3'}),
                html.Div(KPI('Records', '—', id='kpi-rows'), style={'gridColumn':'span 3'}),
                html.Div(KPI('Selected Regions', '—', id='kpi-regions'), style={'gridColumn':'span 3'}),
            ])
        ], style={'gridColumn':'span 12'}),

        html.Div(className='card', children=[
            dcc.Graph(id='timeseries')
        ], style={'gridColumn':'span 8'}),

        html.Div(className='card', children=[
            dcc.Graph(id='bar')
        ], style={'gridColumn':'span 4'}),

        html.Div(className='card', children=[
            dcc.Graph(id='scatter')
        ], style={'gridColumn':'span 6'}),

        html.Div(className='card', children=[
            dcc.Graph(id='heatmap')
        ], style={'gridColumn':'span 6'}),
    ])
])
