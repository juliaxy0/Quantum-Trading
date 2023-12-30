from lumibot.strategies import Strategy
from lumibot.entities import Asset


class QTStrategy(Strategy):

    def initialize(self):
        self.set_market('24/7')

    def on_trading_iteration(self):
        if self.first_iteration:
            order = self.create_order(
                        Asset(symbol='BTC', asset_type='crypto'),
                        .50,
                        'buy',
                        quote=Asset(symbol='USD', asset_type='crypto'),
                    )
            self.submit_order(order)



            

class MACDStrategy(Strategy):

    def initialize(self):
        self.set_market('24/7')

    def on_trading_iteration(self):
        if self.first_iteration:
            order = self.create_order(
                        Asset(symbol='BTC', asset_type='crypto'),
                        .10,
                        'buy',
                        quote=Asset(symbol='USD', asset_type='crypto'),
                    )
            self.submit_order(order)