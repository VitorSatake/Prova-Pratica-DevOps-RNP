from prometheus_client import start_http_server, Gauge
import psycopg2
import os
from ping3 import ping
import time


TARGETS = ["google.com", "youtube.com", "rnp.br"]


rtt_g = Gauge('ping_rtt_seconds', 'Ping RTT in seconds', ['target'])
loss_g = Gauge('ping_packet_loss_percent', 'Packet loss percent', ['target'])


INTERVAL = 15


def measure_once(target):
    # realiza 5 pings e calcula perda e média
    attempts = 5
    success = 0
    times = []
    for i in range(attempts):
        try:
            t = ping(target, timeout=2)
        except Exception:
            t = None
        if t is None:
            pass
        else:
            success += 1
            times.append(t)
        time.sleep(0.2)
    loss = 100.0 * (attempts - success) / attempts
    avg = sum(times) / len(times) if times else 0.0
    return avg, loss


# Conexão com banco
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    dbname=os.getenv('DB_NAME')
)
cur = conn.cursor()


if __name__ == '__main__':
    start_http_server(8000)
    while True:
        for target in TARGETS:
            avg, loss = measure_once(target)
            # salva no banco
            cur.execute(
                "INSERT INTO ping_metrics (target, rtt, loss) VALUES (%s, %s, %s)",
                (target, avg, loss),
            )
            conn.commit()

            rtt_g.labels(target=target).set(avg)
            loss_g.labels(target=target).set(loss)
        time.sleep(INTERVAL)