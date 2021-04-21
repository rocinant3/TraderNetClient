from client import TraderAPIClient

pub_ = 'e5fae7a42b0c910b23d35f43d4402485'
sec_ = 'cf4a2e8a0142e03e551221978cef17eab2ac497e'

api_client = TraderAPIClient(secret_key=sec_, public_key=pub_)
ticker_info = api_client.get_ticker_info('SBER')
print(ticker_info)
