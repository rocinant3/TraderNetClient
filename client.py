import time
import json
from typing import Optional
from requests import Request, Session, Response

from utils import create_hashed_sign, http_encode, pre_sign


class BaseClient:
    _session = ...

    def _init_session(self, params: Optional[dict] = None) -> Session:
        raise NotImplementedError()

    def update_session_params(self, params: dict) -> None:
        """update session
        Args:
            params (dict): like {'IF-MODIFIED-SINCE': <datetime>}
        """
        self._session = self._init_session(params)

    @classmethod
    def _parse_response_body(cls, response: Response) -> dict:
        raw_data = response.content.decode('utf-8')
        if not raw_data:
            return {}
        data = json.loads(raw_data)
        return data


class TraderAPIClient(BaseClient):
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

    def get_ticker_info(self, ticker_name: str):
        cmd = 'getSecurityInfo'
        params = {'ticker': ticker_name, 'sup': True}
        return self.send_request(cmd, params)

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
