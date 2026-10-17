
import os
import time
import shutil
import subprocess
import urllib.request
import tarfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
BIN_DIR = BASE / "bin"
SSHX = BIN_DIR / "sshx"
URL = "https://s3.amazonaws.com/sshx/sshx-x86_64-unknown-linux-musl.tar.gz"

def setup():
    BIN_DIR.mkdir(exist_ok=True)

    if not SSHX.exists():
        archive = BASE / "sshx.tar.gz"
        urllib.request.urlretrieve(URL, archive)

        with tarfile.open(archive, "r:gz") as tar:
            item = next(
                (m for m in tar.getmembers()
                 if m.isfile() and Path(m.name).name == "sshx"),
                None
            )
            if item is None:
                raise RuntimeError("sshx binary missing in archive")

            src = tar.extractfile(item)
            with src, open(SSHX, "wb") as dst:
                shutil.copyfileobj(src, dst)

        archive.unlink(missing_ok=True)
        SSHX.chmod(0o755)

def main():
    setup()

    while True:
        print("[app.py] Starting SSHX session...", flush=True)

        try:
            proc = subprocess.Popen(
                [str(SSHX)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in proc.stdout:
                print(line, end="", flush=True)

            code = proc.wait()
            print(f"[app.py] SSHX exited: {code}", flush=True)

        except Exception as e:
            print(f"[app.py] Error: {e}", flush=True)

        print("[app.py] Retrying in 5 seconds...", flush=True)
        time.sleep(5)

if __name__ == "__main__":
    main()
