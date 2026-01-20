import aiohttp
import asyncio
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler

from settings import settings


class ForecasterLinear:
    def __init__(self, history_days=7):
        self.history_days = history_days
        self.model = None
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        self.feature_cols = [
            'temp_min', 'temp_avg', 'temp_max',
            'humidity_min', 'humidity_avg', 'humidity_max',
            'precipitation',
            'dayofyear'
        ]
        self.target_cols = ['temp_min', 'temp_avg', 'temp_max']
        self.df_history = None

    async def fetch_day_weather(self, session, city, date):
        url = f"http://{settings.WEATHER_HOST}:{settings.WEATHER_PORT}/weather?city={city}&date={date.strftime('%Y-%m-%d')}"
        async with session.get(url) as resp:
            resp_json = await resp.json()
            data = resp_json['weather']
            data['date'] = date.strftime('%Y-%m-%d')
            return data

    async def get_weather_history(self, session, city, start_date, end_date):
        days = pd.date_range(start=start_date, end=end_date)
        tasks = [self.fetch_day_weather(session, city, day) for day in days]
        results = await asyncio.gather(*tasks)
        df = pd.DataFrame(results)
        df['date'] = pd.to_datetime(df['date'])
        df['dayofyear'] = df['date'].dt.dayofyear
        return df

    def make_supervised(self, df):
        df = df.copy()
        df['dayofyear'] = df['date'].dt.dayofyear
        df['temp_min_tgt'] = df['temp_min'].shift(-1)
        df['temp_avg_tgt'] = df['temp_avg'].shift(-1)
        df['temp_max_tgt'] = df['temp_max'].shift(-1)
        df = df.dropna().reset_index(drop=True)
        X = df[self.feature_cols]
        y = df[['temp_min_tgt', 'temp_avg_tgt', 'temp_max_tgt']]
        return X, y

    async def fit(self, city, predict_date):
        today = datetime.utcnow().date()
        max_history_date = today - timedelta(days=2)
        dt_predict = pd.to_datetime(predict_date).date()
        end_date = min(max_history_date, dt_predict - timedelta(days=1))
        start_date = end_date - timedelta(days=self.history_days - 1)

        async with aiohttp.ClientSession() as session:
            df = await self.get_weather_history(session, city, start_date, end_date)
            df = df.dropna().reset_index(drop=True)
            self.df_history = df
            X, y = self.make_supervised(df)
            X_scaled = self.scaler_X.fit_transform(X)
            y_scaled = self.scaler_y.fit_transform(y)
            self.model = MultiOutputRegressor(LinearRegression())
            self.model.fit(X_scaled, y_scaled)

    def predict(self, predict_date):
        if self.model is None or self.df_history is None:
            raise RuntimeError("Model is not trained. Call 'fit' first.")
        # Для прогноза берём последнюю доступную строку (вчера)
        last_row = self.df_history.iloc[[-1]]
        feats = last_row[self.feature_cols].values
        feats_scaled = self.scaler_X.transform(feats)
        preds_scaled = self.model.predict(feats_scaled)
        preds = self.scaler_y.inverse_transform(preds_scaled)
        tmin, tavg, tmax = preds[0]
        forecast = {
            'date': predict_date,
            'temp_min': float(tmin),
            'temp_avg': float(tavg),
            'temp_max': float(tmax)
        }
        return forecast