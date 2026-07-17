from __future__ import annotations
import hashlib, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
def backup():
    source=BASE/"PLANILHA"/"Escala_ZP17_2026.xlsx"
    if not source.exists(): return None
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    for item in (BASE/"BACKUP").glob("*.xlsx"):
        if hashlib.sha256(item.read_bytes()).hexdigest()==digest: return item
    target=BASE/"BACKUP"/f"Escala_ZP17_2026_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    shutil.copy2(source,target); return target
def run(command): subprocess.run(command,cwd=BASE,check=True)
def publish_visible_copy():
    source=BASE/"PLANILHA"/"Escala_ZP17_2026.xlsx"
    target=BASE/"Escala_ZP17_2026.xlsx"
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()!=hashlib.sha256(source.read_bytes()).hexdigest():
        previous=BASE/"BACKUP"/f"Escala_ZP17_2026_RAIZ_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        shutil.copy2(target,previous)
    shutil.copy2(source,target)
def main():
    log=BASE/"LOGS"/f"atualizacao_{datetime.now():%Y%m%d_%H%M%S}.log"
    try:
        saved=backup(); run([sys.executable,"SCRIPTS/baixar_arquivos_2026.py"]); run([sys.executable,"SCRIPTS/processar_escalas_2026.py"])
        node=shutil.which("node")
        if not node: raise RuntimeError("Node.js nao localizado. Consulte o README para usar o runtime do Codex ou instale Node.js.")
        run([node,"work/build_workbook.mjs"]); publish_visible_copy(); run([sys.executable,"SCRIPTS/validar_dados_2026.py"])
        message=f"ATUALIZACAO CONCLUIDA | backup={saved or 'nao necessario'}"
    except Exception as exc: message=f"ATUALIZACAO COM ERRO | {exc}"; log.write_text(message,encoding="utf-8"); raise
    log.write_text(message,encoding="utf-8"); print(message)
if __name__=="__main__": main()
