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
    start = time.time()
    logging.info(f'service=B endpoint=/health status=200 latency_ms={int((time.time()-start)*1000)}')
    return jsonify(status="ok")

@app.get("/call-echo")
def call_echo():
    msg = request.args.get("msg", "")
    return call_service_a("/echo", {"msg": msg}, "/call-echo")

@app.get("/call-slow")
def call_slow():
    # Calls A's deliberately slow endpoint so the timeout above can be observed.
    seconds = request.args.get("seconds", "2")
    return call_service_a("/slow", {"seconds": seconds}, "/call-slow")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081)
