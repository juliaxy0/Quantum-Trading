# from prophet.forecaster import Prophet
import yfinance as yf
import datetime
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
# from sklearn.metrics import mean_absolute_percentage_error

class Stock:
    """
    This class enables data loading, plotting and statistical analysis of a given stock,
     upon initialization load a sample of data to check if stock exists. 
        
    """
    params={
    'changepoint_prior_scale':0.0018298282889708827,
    'holidays_prior_scale':0.00011949782374119523,
    'seasonality_mode':'additive',
    'seasonality_prior_scale':4.240162804451275
        }

    def __init__(_self, symbol):
       
        _self.end = datetime.datetime.today().date()
        _self.start = (_self.end - datetime.timedelta(days=500))
        _self.symbol = symbol
        _self.data = _self.load_data(_self.symbol,_self.start, _self.end)

    @st.cache_data(show_spinner=False)
    def load_data(_self, symbol, start, end, inplace=False):
        """
        takes a start and end dates, download data do some processing and returns dataframe
        """
        _self.symbol = symbol
        data = yf.download(_self.symbol, start, end + datetime.timedelta(days=1))
        try:
            assert len(data) > 0
        except AssertionError:
            print("Cannot fetch data, check spelling or time window")
        data.reset_index(inplace=True)
        data.rename(columns={"Date": "datetime"}, inplace=True)
        data["date"] = data.apply(lambda raw: raw["datetime"].date(), axis=1)

        data = data[["date", 'Close']]
        if inplace:
            _self.data = data
            _self.start = start
            _self.end = end
            return True
        return data
    

    def plot_raw_data(_self, fig):
        """
        Plot time-serie line chart of closing price on a given plotly.graph_objects.Figure object
        """
        fig = fig.add_trace(
            go.Scatter(
                x=_self.data.date,
                y=_self.data['Close'],
                mode="lines",
                name=_self.symbol,
            )
        )
        return fig

    @staticmethod
    def nearest_business_day(DATE: datetime.date):
        """
        Takes a date and transform it to the nearest business day, 
        static because we would like to use it without a stock object.
        """
        if DATE.weekday() == 5:
            DATE = DATE - datetime.timedelta(days=1)

        if DATE.weekday() == 6:
            DATE = DATE + datetime.timedelta(days=1)
        return DATE

    def show_delta(_self):
        """
        Visualize a summary of the stock change over the specified time period
        """

        epsilon = 1e-6
        i = _self.start
        j = (_self.end- datetime.timedelta(days=10))
        s = _self.data.query("date==@i")['Close'].values[0]
        e = _self.data.query("date==@j")['Close'].values[0]

        difference = round(e - s, 2)
        change = round(difference / (s + epsilon) * 100, 2)
        e = round(e, 2)
        cols = st.columns(2)
        (color, marker) = ("green", "+") if difference >= 0 else ("red", "-")

        cols[0].markdown(
            f"""<p style="font-size: 90%;margin-left:5px">{_self.symbol} \t {e}</p>""",
            unsafe_allow_html=True,
        )
        cols[1].markdown(
            f"""<p style="color:{color};font-size:90%;margin-right:5px">{marker} \t {difference} {marker} {change} % </p>""",
            unsafe_allow_html=True
        ) 


    @staticmethod
    def for_prophet(df: pd.DataFrame, date_column="date", y_column="Close") -> pd.DataFrame:
        return df.rename(columns={date_column: "ds", y_column: "y"})

    def load_train_test_data(_self, TEST_INTERVAL_LENGTH, TRAIN_INTERVAL_LENGTH):
        
        """Returns two dataframes for testing and training"""
        TODAY = Stock.nearest_business_day(datetime.date.today())
        TEST_END = Stock.nearest_business_day(TODAY)
        TEST_START = Stock.nearest_business_day(
            TEST_END - datetime.timedelta(days=TEST_INTERVAL_LENGTH)
        )

        TRAIN_END = Stock.nearest_business_day(TEST_START - datetime.timedelta(days=1))
        TRAIN_START = Stock.nearest_business_day(
            TRAIN_END - datetime.timedelta(days=TRAIN_INTERVAL_LENGTH)
        )

        train_data = _self.load_data(_self.symbol, TRAIN_START, TRAIN_END)
        test_data = _self.load_data(_self.symbol, TEST_START, TEST_END)

        train_data = Stock.for_prophet(train_data)
        test_data = Stock.for_prophet(test_data)

        _self.train_data = train_data
        _self.test_data = test_data

    def train_prophet(_self): 

        m = Prophet(**_self.params)
        m.fit(_self.train_data)
        _self.model = m
        forecasts = m.predict(_self.test_data)
        _self.test_data = _self.test_data.join(
            forecasts[["yhat_lower", "yhat", "yhat_upper"]]
        )
        _self.test_mape = mean_absolute_percentage_error(
            _self.test_data["y"], _self.test_data["yhat"]
        )


    def plot_test(_self):

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=_self.test_data["ds"],
                y=_self.test_data["y"],
                mode="lines",
                name="True Closing price",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=_self.test_data["ds"],
                y=_self.test_data["yhat"],
                mode="lines",
                name="Predicted CLosing price",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=_self.test_data["ds"],
                y=_self.test_data["yhat_upper"],
                fill=None,
                mode="lines",
                name="CI+",
                line_color="orange",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=_self.test_data["ds"],
                y=_self.test_data["yhat_lower"],
                fill="tonexty",
                fillcolor='rgba(100,69,0,0.2)',
                mode="lines",
                line_color="orange",
                name="CI-",
            )
        )
        fig.update_layout(
            width=1100,
            margin=dict(l=0, r=0, t=0, b=0, pad=0),
            legend=dict(
                x=0,
                y=0.99,
                traceorder="normal",
                font=dict(size=12),
            ),
            autosize=False,
            template="plotly_dark",
        )

        return fig


    def plot_inference(_self) -> go.Figure:
        """
        Generate forecasts for the given horizon and plots them, returns a plotly.graph_objects.Figure
        """
        all_df=pd.concat([_self.train_data,_self.test_data[['ds','y']]])
        m=Prophet(**_self.params)
        m.fit(all_df)
        _self.model=m
        future=_self.model.make_future_dataframe(periods=st.session_state.HORIZON,include_history=False)
        forecasts=_self.model.predict(future)

        fig=go.Figure()
        fig.add_trace(
        go.Scatter(
            x=forecasts["ds"],
            y=forecasts["yhat"],
            mode="lines",
            name="Predicted CLosing price",
        )
        )

        fig.add_trace(
        go.Scatter(
            x=forecasts["ds"],
            y=forecasts["yhat_upper"],
            fill=None,
            mode="lines",
            name="CI+",
            line_color="orange",
        )
        )

        fig.add_trace(
        go.Scatter(
            x=forecasts["ds"],
            y=forecasts["yhat_lower"],
            fill="tonexty",
            fillcolor='rgba(100,69,0,0.2)',
            mode="lines",
            line_color="orange",
            name="CI-",
        )
        )
        fig.update_layout(
        width=1100,
        margin=dict(l=0, r=0, t=0, b=0, pad=0),
        legend=dict(
            x=0,
            y=0.99,
            traceorder="normal",
            font=dict(size=12),
        ),
        autosize=False,
        template="plotly_dark",
        )
        return fig
        
    # def save_forecasts(_self,path):
    #     _self.forecasts.to_csv(path)
