def place_order(client, symbol, side, quantity, price=None, stop_loss=None, take_profit=None, position_side=None):
    try:
        if side == 'BUY':
            order = client.futures_create_order(
                symbol=symbol,
                side='BUY',
                type='MARKET',
                quantity=quantity,
                positionSide=position_side  # 롱 포지션
            )
            if stop_loss:
                stop_price = price * (1 - stop_loss)
                client.futures_create_order(
                    symbol=symbol,
                    side='SELL',
                    type='STOP_MARKET',
                    stopPrice=stop_price,
                    closePosition=True
                )
            if take_profit:
                take_profit_price = price * (1 + take_profit)
                client.futures_create_order(
                    symbol=symbol,
                    side='SELL',
                    type='TAKE_PROFIT_MARKET',
                    stopPrice=take_profit_price,
                    closePosition=True
                )
        elif side == 'SELL':
            order = client.futures_create_order(
                symbol=symbol,
                side='SELL',
                type='MARKET',
                quantity=quantity,
                positionSide=position_side  # 숏 포지션
            )
            if stop_loss:
                stop_price = price * (1 + stop_loss)
                client.futures_create_order(
                    symbol=symbol,
                    side='BUY',
                    type='STOP_MARKET',
                    stopPrice=stop_price,
                    closePosition=True
                )
            if take_profit:
                take_profit_price = price * (1 - take_profit)
                client.futures_create_order(
                    symbol=symbol,
                    side='BUY',
                    type='TAKE_PROFIT_MARKET',
                    stopPrice=take_profit_price,
                    closePosition=True
                )
        return order
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
