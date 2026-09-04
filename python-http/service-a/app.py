from flask import Flask, request, jsonify
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
app = Flask(__name__)

@app.get("/health")
def health():
    start = time.time()
    logging.info(f'service=A endpoint=/health status=200 latency_ms={int((time.time()-start)*1000)}')
    return jsonify(status="ok")

@app.get("/echo")
def echo():
    start = time.time()
    msg = request.args.get("msg", "")
    resp = {"echo": msg}
    logging.info(f'service=A endpoint=/echo status=200 latency_ms={int((time.time()-start)*1000)}')
    return jsonify(resp)

@app.get("/slow")
def slow():
    # Exists so Service B's request timeout can be demonstrated.
    start = time.time()
    try:
        seconds = float(request.args.get("seconds", 2))
    except ValueError:
        logging.info(f'service=A endpoint=/slow status=400 latency_ms={int((time.time()-start)*1000)}')
        return jsonify(error="seconds must be a number"), 400
    seconds = min(max(seconds, 0.0), 10.0)
    time.sleep(seconds)
    logging.info(f'service=A endpoint=/slow status=200 latency_ms={int((time.time()-start)*1000)}')
    return jsonify(slept=seconds)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
