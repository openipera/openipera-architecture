"""Request interface; external model, separately bound execution, durable evidence."""
import json
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from engine import ResolutionError, derive, digest, execute_dag
from evidence import render
from execution import execute


def realize(request, emit, snapshot_path):
    url = os.environ['MODEL_URL']
    with urlopen(url, timeout=10) as response:
        raw = response.read()
    snapshot_path.write_bytes(raw)
    emit('model_snapshot', source=url, model_sha256=digest(raw),
         model_text=raw.decode('utf-8', errors='replace'))
    try:
        dag = derive(json.loads(raw), request['entry_point'])
    except ResolutionError as exc:
        emit('resolution_failed', error=str(exc), **exc.details)
        raise
    except (ValueError, TypeError) as exc:
        emit('resolution_failed', valid=False, error=str(exc),
             dependencies_resolved=None, cycle_detected=None)
        raise
    emit('resolution_succeeded', dag=dag)
    binding_path = Path(os.environ['ARTIFACT_DIR']) / 'binding.json'
    binding_bytes = binding_path.read_bytes()
    binding = json.loads(binding_bytes)
    if not isinstance(binding, dict) or set(binding) != {'artifact', 'sha256'}:
        raise ValueError('Execution binding must specify artifact and sha256')
    emit('binding_resolved', binding=binding, binding_sha256=digest(binding_bytes))
    execute_dag(dag, binding,
                lambda node, ref: execute(os.environ['ARTIFACT_DIR'], node, ref), emit)
    return dag


class Handler(BaseHTTPRequestHandler):
    def reply(self, code, value):
        data = json.dumps(value).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.reply(200 if self.path == '/health' else 404,
                   {'status': 'ready'} if self.path == '/health' else {'error': 'not found'})

    def do_POST(self):
        if self.path != '/requests':
            return self.reply(404, {'error': 'not found'})
        run_id = uuid.uuid4().hex
        evidence = Path(os.environ.get('EVIDENCE_DIR', 'evidence'))
        evidence.mkdir(parents=True, exist_ok=True)
        events, dag = [], None
        lock = threading.Lock()
        with (evidence / (run_id + '.jsonl')).open('w', encoding='utf-8') as stream:
            def emit(event, **fields):
                with lock:
                    record = dict(run_id=run_id, sequence=len(events), time_ns=time.time_ns(),
                                  event=event, **fields)
                    events.append(record)
                    stream.write(json.dumps(record) + '\n')
                    stream.flush()
                    os.fsync(stream.fileno())
                    print(json.dumps(record), flush=True)

            code = 400
            try:
                size = int(self.headers.get('Content-Length', 0))
                if size < 1 or size > 4096:
                    raise ValueError('Invalid request size')
                raw_request = self.rfile.read(size).decode('utf-8')
                emit('request_started', request=raw_request)
                request = json.loads(raw_request)
                if not isinstance(request, dict) or set(request) != {'entry_point'} or not isinstance(request['entry_point'], str):
                    raise ValueError('Expected {"entry_point": "<Service>.AN-<Node>"}')
                code = 422
                dag = realize(request, emit, evidence / (run_id + '-model.json'))
                status, code = 'succeeded', 200
                emit('request_finished', status=status)
            except Exception as exc:
                status = 'failed'
                emit('request_finished', status=status, error=str(exc))
        report = run_id + '-execution-dag.md'
        (evidence / report).write_text(render(run_id, events), encoding='utf-8')
        self.reply(code, {'run_id': run_id, 'status': status, 'dag': dag,
                          'evidence': report, 'events': events})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '8080'))), Handler).serve_forever()
