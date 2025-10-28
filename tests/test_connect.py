import urllib3
import socket
from urllib3.exceptions import MaxRetryError, ConnectTimeoutError
import time

server_ip = "47.109.185.70"
server_port = 5000
url = f"http://{server_ip}:{server_port}"

def test_connection(retries=5, delay=2):
    for attempt in range(retries):
        try:
            response = urllib3.poolmanager.PoolManager(cert_reqs='CERT_NONE').request('GET', url, timeout=5)
            print(f"Connection successful: {response.status}")
            print(response.data.decode('utf-8'))
            return True
        except (MaxRetryError, ConnectTimeoutError, socket.timeout) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay) 

if __name__ == "__main__":
    test_connection()