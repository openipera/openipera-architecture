"""Small synchronous HTTP request interface with durable per-request evidence."""
import json
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from engine import realize
from execution import execute


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
        try:
            size = int(self.headers.get('Content-Length', 0))
            if size < 1 or size > 4096:
                raise ValueError('Invalid request size')
            request = json.loads(self.rfile.read(size))
            if set(request) != {'service'} or not isinstance(request['service'], str):
                raise ValueError('Expected {"service": "<entry point>"}')
        except (ValueError, TypeError) as exc:
            return self.reply(400, {'error': str(exc)})
        run_id = uuid.uuid4().hex
        evidence = Path(os.environ.get('EVIDENCE_DIR', 'evidence'))
        evidence.mkdir(parents=True, exist_ok=True)
        events = []
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

            emit('request_started', service=request['service'])
            try:
                realize(os.environ['MODEL_URL'], request['service'],
                        lambda node, binding: execute(os.environ['ARTIFACT_DIR'], node, binding), emit)
                status, code = 'succeeded', 200
                emit('request_finished', status=status)
            except Exception as exc:
                status, code = 'failed', 422
                emit('request_finished', status=status, error=str(exc))
        self.reply(code, {'run_id': run_id, 'status': status, 'events': events})


if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '8080'))), Handler).serve_forever()
