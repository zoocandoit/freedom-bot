from binance.client import Client

api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

client = Client(api_key, api_secret)

def place_order(symbol, side, quantity, price=None):
    if side == 'BUY':
        order = client.order_market_buy(
            symbol=symbol,
            quantity=quantity
        )
    elif side == 'SELL':
        order = client.order_market_sell(
            symbol=symbol,
            quantity=quantity
        )
    return order
