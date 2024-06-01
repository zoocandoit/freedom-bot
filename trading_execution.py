def place_order(client, symbol, side, quantity, price=None):
    try:
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
    except Exception as e:
        print(f"An error occurred: {e}")
        return None