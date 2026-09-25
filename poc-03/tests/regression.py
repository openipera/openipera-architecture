"""Run historical unit and live HTTP conformance in disposable copies only."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    out=parser.parse_args().out.resolve();out.mkdir(parents=True,exist_ok=False)
    results=[]
    with tempfile.TemporaryDirectory() as folder:
        for name in ('poc-01','poc-02'):
            copy=Path(folder)/name;shutil.copytree(ROOT/name,copy)
            units=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=copy,capture_output=True,text=True)
            (out/(name+'-unit.txt')).write_text(units.stdout+units.stderr)
            if units.returncode:raise RuntimeError(name+' unit regression failed')
            handler=functools.partial(SimpleHTTPRequestHandler,directory=str(copy/'model'))
            model=ThreadingHTTPServer(('127.0.0.1',0),handler)
            thread=threading.Thread(target=model.serve_forever,daemon=True);thread.start()
            with socket.socket() as port_socket:
                port_socket.bind(('127.0.0.1',0));port=port_socket.getsockname()[1]
            env=dict(os.environ,MODEL_URL=f'http://127.0.0.1:{model.server_port}/service-model.json',
                     PORT=str(port),ARTIFACT_DIR=str(copy/'artifacts'),EVIDENCE_DIR=str(copy/'evidence'))
            with (out/(name+'-server.txt')).open('w') as log:
                server=subprocess.Popen([sys.executable,'runtime/server.py'],cwd=copy,env=env,stdout=log,stderr=log)
                try:
                    url=f'http://127.0.0.1:{port}'
                    for attempt in range(100):
                        if server.poll() is not None:raise RuntimeError('Server exited')
                        try:
                            with urlopen(url+'/health',timeout=.5) as response:
                                if response.status==200:break
                        except OSError:time.sleep(.05)
                    else:raise RuntimeError('Server did not become ready')
                    result=subprocess.run([sys.executable,'tests/conformance.py',url],cwd=copy,capture_output=True,text=True,timeout=60)
                    (out/(name+'-http.txt')).write_text(result.stdout+result.stderr)
                    if result.returncode:raise RuntimeError(name+' HTTP conformance failed')
                    report='conformance.json' if name=='poc-01' else 'poc02-conformance.json'
                    shutil.copyfile(copy/'evidence'/report,out/(name+'-conformance.json'))
                    results.append(dict(experiment=name,unit='PASS',live_http='PASS',isolated_copy=True))
                finally:
                    server.terminate();server.wait(timeout=10);model.shutdown();model.server_close();thread.join()
    (out/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PASS: POC-01/02 units and live HTTP conformance in isolated copies')


if __name__=='__main__':main()
