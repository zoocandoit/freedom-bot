def place_order(client, symbol, side, quantity, price=None, stop_loss=None, take_profit=None):
    try:
        if side == 'BUY':
            order = client.order_market_buy(
                symbol=symbol,
                quantity=quantity
            )
            if stop_loss:
                stop_price = price * (1 - stop_loss)
                client.order_oco_sell(
                    symbol=symbol,
                    quantity=quantity,
                    price=take_profit,
                    stopPrice=stop_price,
                    stopLimitPrice=stop_price,
                    stopLimitTimeInForce='GTC'
                )
        elif side == 'SELL':
            order = client.order_market_sell(
                symbol=symbol,
                quantity=quantity
            )
            if stop_loss:
                stop_price = price * (1 + stop_loss)
                client.order_oco_buy(
                    symbol=symbol,
                    quantity=quantity,
                    price=take_profit,
                    stopPrice=stop_price,
                    stopLimitPrice=stop_price,
                    stopLimitTimeInForce='GTC'
                )
        return order
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
