from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/flujo_voz/<path:subpath>', methods=['GET','POST'])
def flujo_voz(subpath):
    # Responde 200 para cualquier petición de métrica de flujo_voz
    return jsonify({"status": "ok", "endpoint": f"/flujo_voz/{subpath}"}), 200

@app.route('/flujo_texto/<path:subpath>', methods=['GET','POST'])
def flujo_texto(subpath):
    return jsonify({"status": "ok", "endpoint": f"/flujo_texto/{subpath}"}), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "metrics_stub", "info": "Responderá 200 a /flujo_voz/* y /flujo_texto/*"}), 200

if __name__ == '__main__':
    # Escuchar sólo en localhost:5005
    app.run(host='127.0.0.1', port=5005)
