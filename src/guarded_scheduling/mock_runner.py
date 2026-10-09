"""Own a supplied reference server process; restarting resets synthetic state only."""
from pathlib import Path
import socket
import subprocess
import sys
import time
from .http_adapter import HttpAdapter
from .ports import SchedulingUnavailable

class MockRunner:
    def __init__(self, python_executable=sys.executable, port=0):
        if type(port) is not int or not 0 <= port < 65536:
            raise ValueError('Invalid local mock port.')
        self.python_executable = str(python_executable)
        self.port = port
        self.base_url = None
        self.process = None

    def __enter__(self):
        if self.process is not None:
            raise RuntimeError('Mock runner is already started.')
        try:
            result = subprocess.run([self.python_executable,'-c','import sys; print(str(sys.version_info.major)+"."+str(sys.version_info.minor))'],capture_output=True,text=True,timeout=5,check=True)
            major,minor = (int(v) for v in result.stdout.strip().split('.'))
            if (major,minor) < (3,11): raise ValueError
        except Exception:
            raise RuntimeError('Mock server requires an explicit Python 3.11+ executable.') from None
        try:
            # Check before binding; never stop an existing occupant. Port0 avoids fixed test ports.
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as probe:
                probe.bind(('127.0.0.1',self.port))
                self.port = probe.getsockname()[1]
        except OSError:
            raise RuntimeError('Requested mock port is unavailable.') from None
        source = Path(__file__).resolve().parents[2] / 'vendor/reference/mock-api/server.py'
        self.base_url = 'http://127.0.0.1:' + str(self.port)
        try:
            self.process = subprocess.Popen([self.python_executable,str(source),'--port',str(self.port)],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            adapter=HttpAdapter(self.base_url,timeout=.2)
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                if self.process.poll() is not None:
                    raise RuntimeError('Reference mock exited before readiness.')
                try:
                    response=adapter.request('GET','/providers')
                    if response.status==200 and isinstance(response.data.get('providers'),list) and self.process.poll() is None:
                        return self
                except SchedulingUnavailable:
                    pass
                time.sleep(.03)
            raise RuntimeError('Reference mock did not become ready.')
        except Exception:
            self.stop()
            raise RuntimeError('Reference mock startup failed.') from None

    def stop(self):
        """Stop only the process this runner launched; never reconcile uncertain bookings."""
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try: self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)

    def __exit__(self,*exc):
        self.stop()

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description='Owned synthetic scheduling reference process; raw audit output suppressed')
    parser.add_argument('--port',type=int,default=4011)
    args=parser.parse_args(argv)
    try:
        with MockRunner(port=args.port) as runner:
            print('Synthetic reference ready at '+runner.base_url+'. Ctrl-C stops this owned process. Reset is not transaction reconciliation.',flush=True)
            while runner.process.poll() is None:
                time.sleep(.2)
    except KeyboardInterrupt:return 0
    except RuntimeError:
        print('Reference startup failed; check interpreter and free port. No unrelated process was stopped.',file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':raise SystemExit(main())
