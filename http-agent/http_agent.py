import time
import requests
from prometheus_client import start_http_server, Gauge, Counter


TARGETS = [
    {"target": "google.com", "path": "/"},
    {"target": "youtube.com", "path": "/"},
    {"target": "rnp.br", "path": "/"},
]


resp_time = Gauge('http_response_time_seconds', 'HTTP response time', ['target', 'path'])
up_g = Gauge('http_up', 'HTTP up (1) or down (0)', ['target', 'path'])
status_cnt = Counter('http_response_code', 'HTTP response codes', ['target', 'path', 'code'])


INTERVAL = 15


if __name__ == '__main__':
    start_http_server(8001)
    while True:
        for t in TARGETS:
            url = f"https://{t['target']}{t['path']}"
            try:
                ts = time.time()
                r = requests.get(url, timeout=10)
                elapsed = time.time() - ts
                resp_time.labels(target=t['target'], path=t['path']).set(elapsed)
                up_g.labels(target=t['target'], path=t['path']).set(1)
                status_cnt.labels(target=t['target'], path=t['path'], code=str(r.status_code)).inc()
            except Exception:
                # marca como down
                resp_time.labels(target=t['target'], path=t['path']).set(0)
                up_g.labels(target=t['target'], path=t['path']).set(0)
                status_cnt.labels(target=t['target'], path=t['path'], code='0').inc()
        time.sleep(INTERVAL)