# config.py

# Binance API 설정
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'

# 텔레그램 봇 설정
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'

# 거래 설정
SYMBOL = 'BTCUSDT'  # 거래할 암호화폐 심볼
ASSET = 'USDT'  # 거래에 사용할 자산
INTERVAL = '1m'  # 데이터 수집 간격 (1분)
SHORT_WINDOW = 3  # 단기 이동 평균 창
LONG_WINDOW = 7  # 장기 이동 평균 창
PERCENTAGE = 0.01  # 자산의 몇 퍼센트를 거래할지 (1%)
SIGNAL_THRESHOLD = 3  # 신호 발생 횟수 임계값

# 피보나치 수열 기반 손절매 및 이익 실현 비율
STOP_LOSS_PERCENTAGE = 0.02  # 손절매 비율 (2%)
TAKE_PROFIT_PERCENTAGE = 0.05  # 이익 실현 비율 (5%)
