from decouple import config
from tradernet_client import TraderNetAPIClient

PUBLIC_KEY = config("TRADERNET_PUBLIC_KEY")
SECRET_KEY = config("TRADERNET_SECRET_KEY")

api_client = TraderNetAPIClient(SECRET_KEY, PUBLIC_KEY)
print(api_client.get_ticker_info("SBER"))