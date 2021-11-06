import pandas
from dash import dcc
from dash import html

import plotly.graph_objects as go

from analysis import Analysis

analysis = Analysis()


def create_layout():
    sections = ['Загрузка данных', 'Предобработка данных и характеристики ряда', 'Предсказание']

    return html.Div([
        html.Div(html.H1(children='Анализ временных рядов'),
                 style={'text-align': 'center'}),
        html.Div(dcc.Markdown(children='Выберите этап анализа:'),
                 style={'width': '18%', 'display': 'inline-block'}),
        html.Div(dcc.Dropdown(
            id='section_name',
            options=[{'label': x, 'value': x} for x in sections],
            value='Загрузка данных'),
            style={'width': '78%', 'display': 'inline-block', 'float': 'right'}),
        html.Div(id='section', style={'margin': '30px'})])


def download():
    return html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Перетащите или ',
                html.A('выберите'),
                ' файл с расширением csv или xls.'
            ]),
            style={
                'width': '98%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=True
        ),
        html.Div(id='output-data-upload'),
    ])


def preprocessing_description():
    interpolations = ['Не заполнять', 'Интерполяция с учетом индекса', 'Линейная интерполяция',
                      'Квадратичная интерполяция']
    return html.Div([
        html.Div([dcc.Markdown('Предобработка',
                               style={'text-align': 'center'}),
                  dcc.Markdown('Заполнение пропусков:'),
                  dcc.Dropdown(id='fill_gaps',
                               options=[{'label': i, 'value': i}
                                        for i in interpolations],
                               value='Не заполнять'),
                  dcc.Markdown('Порядок дифференцирования ряда:'),
                  dcc.Input(
                      id="diff",
                      type="number"
                  ),
                  dcc.Markdown('Логарифмирование:'),
                  dcc.RadioItems(id='log',
                                 options=[{'label': i, 'value': i}
                                          for i in ['Логарифмировать', 'Не логарифмировать']],
                                 value='Не логарифмировать')
                  ], style={'width': '28%', 'display': 'inline-block'}),
        html.Div([dcc.Markdown('Характеристики ряда',
                               style={'text-align': 'center'}),
                  dcc.Markdown('Описательная таблица:'),
                  html.Div(id='description_table'),
                  dcc.Markdown('Тест Дики-Фуллера:'),
                  html.Div(id='dickey_fuller')
                  ], style={'width': '68%', 'display': 'inline-block', 'float': 'right'}),
        dcc.Graph(id='linear_graph')
    ])


def prediction():
    return html.Div([html.Div([dcc.Markdown('Доверительный интервал предсказания',
                                            style={'text-align': 'center'}),
                               dcc.RadioItems(id='interval',
                                              options=[{'label': i, 'value': i}
                                                       for i in ['Показывать', 'Не показывать']],
                                              value='Показывать')],
                              style={'width': '25%', 'display': 'inline-block'}),
                     html.Div([dcc.Markdown('Параметры сезонности',
                                            style={'text-align': 'center', 'margin': '3px'}),
                               dcc.Markdown('Годовой:', style={'display': 'inline-block'}),
                               dcc.Input(
                                   id="year",
                                   type="number",
                                   style={'display': 'inline-block', 'margin': '3px'}),
                               dcc.Markdown('Недельный:',
                                            style={'display': 'inline-block', 'margin': '3px'}),
                               dcc.Input(
                                   id="week",
                                   type="number",
                                   style={'display': 'inline-block', 'margin': '3px'}),
                               dcc.Markdown('Дневной:',
                                            style={'display': 'inline-block', 'margin': '3px'}),
                               dcc.Input(
                                   id="day",
                                   type="number",
                                   style={'display': 'inline-block', 'margin': '3px'})
                               ], style={'width': '73%', 'display': 'inline-block', 'float': 'right'}),
                     dcc.Markdown('Количество дней для предсказания:',
                                  style={'display': 'inline-block', 'margin': '5px'}),
                     dcc.Input(
                         id="prediction_days",
                         type="number",
                         style={'display': 'inline-block', 'margin': '5px'}),
                     dcc.Graph(id='linear_graph_prediction')
                     ])


def create_linear(forecast=None, bounds=True):
    fact_line = go.Scatter(
        x=analysis.preprocessed_data['ds'],
        y=analysis.preprocessed_data['y'],
        marker=dict(color="blue"),
        mode='lines',
    )

    data = [fact_line]

    if forecast is not None:
        forecast_line = go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines',
            line=dict(color='orange'),
        )

        data.append(forecast_line)

        if bounds:
            upper_line = go.Scatter(
                x=forecast['ds'],
                y=forecast['yhat_upper'],
                mode='lines',
                marker=dict(color="orange"),
                line=dict(dash='dash'))

            lower_line = go.Scatter(
                x=forecast['ds'],
                y=forecast['yhat_lower'],
                mode='lines',
                marker=dict(color="orange"),
                line=dict(dash='dash'))

            data.append(upper_line)
            data.append(lower_line)

    legend = go.Layout(
        yaxis=dict(title='Значение временного ряда'),
        xaxis=dict(title='Дата'),
        title='Линейный график',
        showlegend=False)

    fig = go.Figure(data=data, layout=legend)
    return fig


layout = create_layout()
