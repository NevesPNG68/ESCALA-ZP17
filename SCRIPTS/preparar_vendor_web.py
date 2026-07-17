from __future__ import annotations

import base64
import hashlib
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "APP" / "vendor" / "xlsx.full.min.js"
OUTPUT = BASE / "APP" / "vendor" / "xlsx.parts"
CHUNK_SIZE = 48_000


def main() -> int:
    data = SOURCE.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parts = [encoded[index:index + CHUNK_SIZE] for index in range(0, len(encoded), CHUNK_SIZE)]
    for old in OUTPUT.glob("part-*.txt"):
        old.unlink()
    for index, part in enumerate(parts):
        (OUTPUT / f"part-{index:03d}.txt").write_text(part, encoding="ascii")
    digest = hashlib.sha256(data).hexdigest()
    (OUTPUT / "manifest.txt").write_text(f"{len(parts)}\n{digest}\n", encoding="ascii")
    print(f"VENDOR WEB PREPARADO: {len(parts)} partes | sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
