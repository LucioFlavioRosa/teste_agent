# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from agents import agente_revisor
import traceback
import uuid
import threading
import queue

app = Flask(__name__)

# ============================
# Infra de fila simples em memória
# ============================

job_queue = queue.Queue()
job_results = {}
lock = threading.Lock()


def worker_loop():
    while True:
        job_id, payload = job_queue.get()
        try:
            with lock:
                job_results[job_id] = {"status": "running"}

            resultado = agente_revisor.executar_analise(
                tipo_analise=payload.get('tipo_analise'),
                repositorio=payload.get('repositorio'),
                codigo=payload.get('codigo'),
                instrucoes_extras=payload.get('instrucoes_extras', ''),
                ref=payload.get('ref')
            )

            with lock:
                job_results[job_id] = {"status": "completed", "result": resultado}
        except Exception as e:
            traceback.print_exc()
            with lock:
                job_results[job_id] = {"status": "failed", "error": str(e)}
        finally:
            job_queue.task_done()


# Inicializa um worker em background
threading.Thread(target=worker_loop, daemon=True).start()


@app.route('/executar_analise', methods=['POST'])
def rodar_analise():
    print("INFO: Requisição recebida no endpoint /executar_analise")

    dados = request.get_json()

    if not dados:
        return jsonify({"erro": "Corpo da requisição inválido ou não é um JSON."}), 400

    tipo_analise = dados.get('tipo_analise')
    repositorio = dados.get('repositorio')
    codigo = dados.get('codigo')
    instrucoes_extras = dados.get('instrucoes_extras', '')
    ref = dados.get('ref')

    if not tipo_analise:
        return jsonify({"erro": "O parâmetro 'tipo_analise' é obrigatório."}), 400
    if not repositorio and not codigo:
        return jsonify({"erro": "É obrigatório fornecer pelo menos um dos parâmetros: 'repositorio' ou 'codigo'."}), 400

    job_id = str(uuid.uuid4())
    payload = {
        'tipo_analise': tipo_analise,
        'repositorio': repositorio,
        'codigo': codigo,
        'instrucoes_extras': instrucoes_extras,
        'ref': ref,
    }

    with lock:
        job_results[job_id] = {"status": "queued"}

    job_queue.put((job_id, payload))

    print(f"INFO: Job {job_id} enfileirado para análise '{tipo_analise}'.")
    return jsonify({"job_id": job_id, "status": "accepted"}), 202


@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    with lock:
        info = job_results.get(job_id)
    if not info:
        return jsonify({"erro": "job_id não encontrado"}), 404
    return jsonify(info), 200


@app.route("/")
def index():
    return "<h1>Servidor de Agentes de IA está no ar!</h1><p>Use o endpoint <b>/executar_analise</b> via POST para rodar uma análise e consulte <b>/status/&lt;job_id&gt;</b> para obter o resultado.</p>"


if __name__ == '__main__':
    # Em produção, use um servidor WSGI/ASGI (gunicorn, uvicorn) e múltiplos workers
    app.run(host='0.0.0.0', port=5000, debug=True)
