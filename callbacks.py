from dash.dependencies import Input, Output
import base64
import pandas as pd
import io
from dash import dcc
from dash import html
from dash import dash_table

from app import app
from visualisation import download, preprocessing_description, \
    prediction, analysis, create_linear


@app.callback(
    Output('section', 'children'),
    Input('section_name', 'value'))
def choose_section(section_name):
    if section_name == 'Загрузка данных':
        return download()
    elif section_name == 'Предобработка данных и характеристики ряда':
        return preprocessing_description()
    elif section_name == 'Предсказание':
        return prediction()


# download
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' == filename.split('.')[1]:
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), index_col=0)
        elif 'xls' in filename.split('.')[1]:
            df = pd.read_excel(io.BytesIO(decoded), index_col=0)
        analysis.initial_data = df
        analysis.initial_data.columns = ['ds', 'y']
        analysis.update_preprocessed_data()
    except Exception as e:
        return html.Div([
            'Произошла ошибка при загрузке. Проверьте, что расширение csv или xls и кодировка utf-8.'
        ])
    return html.Div([
        html.H5('Загружен файл ' + filename),
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        )
    ])


@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),
              prevent_initial_call=True)
def update_download_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n) for c, n in
            zip(list_of_contents, list_of_names)]
        return children


# preprocessing and description
@app.callback(Output('description_table', 'children'),
              Output('dickey_fuller', 'children'),
              Output('linear_graph', 'figure'),
              Input('fill_gaps', 'value'),
              Input('diff', 'value'),
              Input('log', 'value'))
def update_description(fill_gaps, diff, log):
    analysis.fill_gaps_method = fill_gaps
    analysis.diff = diff
    analysis.log = log
    analysis.update_preprocessed_data()
    table = analysis.description_table()
    adf, p_value = analysis.dickey_fuller()
    description_table = dash_table.DataTable(data=[table.to_dict()],
                                             columns=[{"name": i, "id": i} for i in table.index])
    dickey_fuller = dcc.Textarea(value=
                                 f'Значение статистики теста = {adf}\n p-значение = {p_value}',
                                 style={'width': '50%'})
    linear_graph = create_linear()
    return description_table, dickey_fuller, linear_graph


# prediction
@app.callback(Output('linear_graph_prediction', 'figure'),
              Input('interval', 'value'),
              Input('year', 'value'),
              Input('week', 'value'),
              Input('day', 'value'),
              Input('prediction_days', 'value'))
def update_prediction(interval, year, week, day, prediction_days):
    if year is not None:
        analysis.yearly_seasonality = year
    else:
        analysis.yearly_seasonality = 'auto'
    if week is not None:
        analysis.weekly_seasonality = week
    else:
        analysis.weekly_seasonality = 'auto'
    if day is not None:
        analysis.daily_seasonality = day
    else:
        analysis.daily_seasonality = 'auto'
    if prediction_days is not None:
        forecast = analysis.make_prediction(prediction_days)
    else:
        forecast = analysis.make_prediction(30)
    bounds = (interval == 'Показывать')
    return create_linear(forecast, bounds)
