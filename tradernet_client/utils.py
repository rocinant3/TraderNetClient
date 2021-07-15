import hmac
import hashlib


def batch(iterable, n=1):
    size = len(iterable)
    for ndx in range(0, size, n):
        yield iterable[ndx:min(ndx + n, size)]


def create_hashed_sign(message: bytes, key: bytes) -> str:
    digest = hmac.new(key, msg=message, digestmod=hashlib.sha256)
    return digest.hexdigest()


def http_encode(d):
    s = ''
    for i in sorted(d):
        if type(d[i]) == dict:
            for into in d[i]:
                if type(d[i][into]) == dict:
                    for subInto in d[i][into]:
                        if type(d[i][into][subInto]) == dict:
                            s += http_encode(d[i][into][subInto])
                        else:
                            s += i + '[' + into + ']' + '[' + subInto + ']=' + str(d[i][into][subInto]) + '&'
                else:
                    s += i + '[' + into + ']=' + str(d[i][into]) + '&'
        else:
            s += i + '=' + str(d[i]) + '&'
    return s[:-1]


def pre_sign(d):
    s = ''
    for i in sorted(d):
        if type(d[i]) == dict:
            s += i + '=' + pre_sign(d[i]) + '&'
        else:
            s += i + '=' + str(d[i]) + '&'
    return s[:-1]
