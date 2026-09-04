from flask import Flask, request, jsonify
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
app = Flask(__name__)

SERVICE_A = "http://127.0.0.1:8080"
TIMEOUT_SECONDS = 1.0

def call_service_a(path, params, endpoint):
    """Call Service A with a timeout, logging the outcome either way.

    Returns a (flask response, status code) tuple. Any failure to reach A --
    timeout, connection refused, or an error status -- becomes a 503 here, so
    Service A going down never takes Service B down with it.
    """
    start = time.time()
    try:
        r = requests.get(f"{SERVICE_A}{path}", params=params, timeout=TIMEOUT_SECONDS)
        r.raise_for_status()
        data = r.json()
        logging.info(f'service=B endpoint={endpoint} status=200 latency_ms={int((time.time()-start)*1000)}')
        return jsonify(service_b="ok", service_a=data), 200
    except Exception as e:
        logging.error(f'service=B endpoint={endpoint} status=503 error="{str(e)}" latency_ms={int((time.time()-start)*1000)}')
        return jsonify(service_b="error", service_a="unavailable", error=str(e)), 503

@app.get("/health")
def health():
    return jsonify(status="ok")

@app.get("/call-echo")
def call_echo():
    start = time.time()
    msg = request.args.get("msg", "")
    try:
        r = requests.get(f"{SERVICE_A}/echo", params={"msg": msg}, timeout=1.0)
        r.raise_for_status()
        data = r.json()
        logging.info(f'service=B endpoint=/call-echo status=ok latency_ms={int((time.time()-start)*1000)}')
        return jsonify(service_b="ok", service_a=data)
    except Exception as e:
        logging.info(f'service=B endpoint=/call-echo status=error error="{str(e)}" latency_ms={int((time.time()-start)*1000)}')
        return jsonify(service_b="ok", service_a="unavailable", error=str(e)), 503

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081)
