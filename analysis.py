from prophet import Prophet
import pandas
import numpy as np
from statsmodels.tsa.stattools import adfuller


class Analysis:
    def __init__(self):
        self.initial_data = None
        self.fill_gaps_method = None
        self.log = None
        self.diff = None
        self.preprocessed_data = None
        self.yearly_seasonality = 'auto'
        self.weekly_seasonality = 'auto'
        self.daily_seasonality = 'auto'

    def fill_gaps(self):
        if self.fill_gaps_method == 'Интерполяция с учетом индекса':
            df_time_index = self.initial_data.copy()
            df_time_index.index = df_time_index['ds']
            self.preprocessed_data['y'] = df_time_index['y'].interpolate('time').values
        elif self.fill_gaps_method == 'Линейная интерполяция':
            self.preprocessed_data['y'] = self.initial_data['y'].interpolate('linear')
        elif self.fill_gaps_method == 'Квадратичная интерполяция':
            self.preprocessed_data['y'] = self.initial_data['y'].interpolate('quadratic')
        elif self.fill_gaps_method == 'Не заполнять':
            self.preprocessed_data['y'] = self.initial_data['y']

    def update_preprocessed_data(self):
        self.preprocessed_data = self.initial_data.copy()
        self.fill_gaps()
        if self.diff is not None:
            self.preprocessed_data['y'] = self.preprocessed_data['y'].diff(periods=self.diff)
        if self.log == 'Логарифмировать':
            self.preprocessed_data['y'] = np.log(self.preprocessed_data['y'])

    def description_table(self):
        return self.preprocessed_data['y'].describe()

    def dickey_fuller(self):
        data = self.preprocessed_data['y'].dropna()
        return adfuller(data)[0], adfuller(data)[1]

    def make_prediction(self, n):
        m = Prophet(yearly_seasonality=self.yearly_seasonality,
                    weekly_seasonality=self.weekly_seasonality,
                    daily_seasonality=self.daily_seasonality)
        m.fit(self.preprocessed_data[:-n])
        future = m.make_future_dataframe(periods=n)
        forecast = m.predict(future)
        return forecast[-n:]
