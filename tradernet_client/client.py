import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Set, Generator
from pydantic import ValidationError
from requests import Request, Session, Response

from .utils import create_hashed_sign, http_encode, pre_sign
from .schemas import Ticker


class BaseClient:
    _session = ...

    def _init_session(self, params: Optional[dict] = None) -> Session:
        raise NotImplementedError()

    def update_session_params(self, params: dict) -> None:
        self._session = self._init_session(params)

    @classmethod
    def _parse_response_body(cls, response: Response) -> dict:
        raw_data = response.content.decode('utf-8')
        if not raw_data:
            return {}
        data = json.loads(raw_data)
        return data


class TraderNetAPIClient(BaseClient):
    _base_url = 'https://tradernet.ru/api'

    def __init__(self, secret_key: str, public_key: str):
        self.secret_key = secret_key
        self.public_key = public_key
        self._session = self._init_session()

    def _init_session(self, params: Optional[dict] = None) -> Session:
        session = Session()
        session.headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        if params:
            session.headers.update(params)
        return session

    def send_request(self, cmd: str, params: dict = None):
        endpoint = f'{self._base_url}/v2/cmd/{cmd}'
        payload = self._build_payload(cmd, params)
        return self._send_request('post', endpoint, data=payload)

    def get_ticker_info(self, ticker_name: str) -> Optional[Ticker]:
        cmd = 'getStockQuotesJson'
        params = {'tickers': ticker_name}
        response = self.send_request(cmd, params)
        raw_data: list = response.get("result", {}).get("q", [])
        if len(raw_data) == 0:
            return None
        try:
            return Ticker(**raw_data[0])
        except ValidationError:
            return None

    def get_ready_list(self):
        cmd = 'getReadyList'
        params = {
            "mkt": None
        }
        return self.send_request(cmd, params)

    def get_stock_code_names(self) -> Set[str]:
        code_names = list()
        tickers_list = self.get_ready_list()
        for section_name, section_data in tickers_list['sections'].items():
            for sector_name, sector_data in section_data['list'].items():
                for stock in sector_data['stocks']:
                    code_names.append(stock)
        return set(code_names)

    def tickers_info_generator(self) -> Generator[Ticker, None, None]:

        stock_code_names = self.get_stock_code_names()
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.get_ticker_info, stock_code_name)
                for stock_code_name in stock_code_names
            }
        for completed_future in as_completed(futures):
            result = completed_future.result()
            if result:
                yield result

    def _build_payload(self, cmd: str, params: dict = None) -> dict:
        return {
            'cmd': cmd,
            'params': params,
            'apiKey': self.public_key,
            'nonce': int(time.time() * 10000)
        }

    def _send_request(self, method: str, url: str, data: dict = None):
        self._update_request_sign(request_data=data)
        request = Request(method, url=url, data=http_encode(data), headers=self._session.headers).prepare()
        response = self._session.send(request)
        return self._parse_response_body(response)

    def _update_request_sign(self, request_data: dict) -> None:
        key = self.secret_key.encode('utf-8')
        message = pre_sign(request_data).encode('utf-8')
        sign = create_hashed_sign(key=key, message=message)
        self._session.headers.update({'X-NtApi-Sig': sign})
