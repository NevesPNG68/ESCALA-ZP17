from __future__ import annotations

import csv
import hashlib
import html
import re
import ssl
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://www.marinha.mil.br/cppr/praticagem"
ARCHIVE_URL = "https://www.marinha.mil.br/cppr/praticagem_arquivo"
MONTHS = {
    1: "01_JANEIRO", 2: "02_FEVEREIRO", 3: "03_MARCO", 4: "04_ABRIL",
    5: "05_MAIO", 6: "06_JUNHO", 7: "07_JULHO", 8: "08_AGOSTO",
    9: "09_SETEMBRO", 10: "10_OUTUBRO", 11: "11_NOVEMBRO", 12: "12_DEZEMBRO",
}
KNOWN_OFFICIAL = [
    (1, "ORIGINAL", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/2026-03/EscalaDeRodizio_ZP17_1-2026.pdf"),
    (3, "ORIGINAL", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_3-2026.pdf"),
    (3, "ALT-02", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_3-2026%20ALT%202.pdf"),
    (4, "ORIGINAL", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_4-2026.pdf"),
    (4, "ALT-01", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_4-2026%20ALT_01.pdf"),
    (5, "ORIGINAL", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_5-2026.pdf"),
    (5, "ALT-01", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_5-2026%20-%20ALT_1.pdf"),
    (5, "ALT-02", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_5-2026%20-%20ALT_2.pdf"),
    (6, "ORIGINAL", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_6-2026.pdf"),
    (6, "ALT-01", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_6-2026%20-%20ALT_1.pdf"),
    (7, "ORIGINAL", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_7-2026.pdf"),
    (7, "ALT-01", "https://www.marinha.mil.br/cppr/sites/www.marinha.mil.br.cppr/files/EscalaDeRodizio_ZP17_7-2026%20-%20ALT_1.pdf"),
]

def fetch(url: str) -> bytes:
    if urllib.parse.urlparse(url).hostname not in {"www.marinha.mil.br", "assets.marinha.mil.br"}:
        raise ValueError("Dominio fora da fonte oficial permitida")
    req = urllib.request.Request(url, headers={"User-Agent": "Escala-ZP17-2026/1.0"})
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=60, context=context) as response:
        return response.read()

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def safe_target(folder: Path, original: str, data_hash: str) -> Path:
    target = folder / original
    if not target.exists():
        return target
    if hashlib.sha256(target.read_bytes()).hexdigest() == data_hash:
        return target
    return folder / f"{target.stem}_{data_hash[:10]}{target.suffix}"

def main() -> int:
    log_path = BASE / "LOGS" / "downloads_2026.csv"
    headers = ["ANO","MES","COMPETENCIA","VERSAO","NOME_ORIGINAL","NOME_SALVO","URL_ORIGEM","DATA_HORA_DOWNLOAD","TAMANHO_BYTES","HASH_SHA256","STATUS","OBSERVACAO"]
    previous = []
    if log_path.exists():
        with log_path.open("r", encoding="utf-8-sig", newline="") as fh:
            previous = list(csv.DictReader(fh))
    by_hash = {row.get("HASH_SHA256"): row for row in previous if row.get("HASH_SHA256")}
    rows = list(previous)
    for month, version, url in KNOWN_OFFICIAL:
        original = urllib.parse.unquote(Path(urllib.parse.urlparse(url).path).name)
        try:
            data = fetch(url)
            digest = sha256(data)
            folder = BASE / "ARQUIVOS_CPPR" / "2026" / MONTHS[month]
            target = safe_target(folder, original, digest)
            if digest not in by_hash:
                target.write_bytes(data)
                row = {"ANO":"2026","MES":str(month),"COMPETENCIA":f"2026-{month:02d}","VERSAO":version,
                       "NOME_ORIGINAL":original,"NOME_SALVO":target.name,"URL_ORIGEM":url,
                       "DATA_HORA_DOWNLOAD":datetime.now().astimezone().isoformat(timespec="seconds"),
                       "TAMANHO_BYTES":str(len(data)),"HASH_SHA256":digest,"STATUS":"BAIXADO","OBSERVACAO":"Documento oficial preservado sem modificacao."}
                rows.append(row); by_hash[digest] = row
                print(f"BAIXADO {row['COMPETENCIA']} {version}: {target.name}")
            else:
                print(f"JA REGISTRADO {month:02d} {version}: {original}")
        except Exception as exc:
            print(f"ERRO {month:02d} {version}: {exc}", file=sys.stderr)
    with log_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers); writer.writeheader(); writer.writerows(rows)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
