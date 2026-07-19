from __future__ import annotations

import csv
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

import pdfplumber

BASE = Path(__file__).resolve().parents[1]
MONTH_ABBR = {1:"JAN",2:"FEV",3:"MAR",4:"ABR",5:"MAI",6:"JUN",7:"JUL",8:"AGO",9:"SET",10:"OUT",11:"NOV",12:"DEZ"}
WEEKDAYS = {"SEG":"SEGUNDA-FEIRA","TER":"TERCA-FEIRA","QUA":"QUARTA-FEIRA","QUI":"QUINTA-FEIRA","SEX":"SEXTA-FEIRA","SAB":"SABADO","DOM":"DOMINGO"}

def normalized_code(value: str) -> str:
    return "".join(character for character in unicodedata.normalize("NFD", value) if unicodedata.category(character) != "Mn").upper()

def legend(page_text: str) -> dict[str, str]:
    result = {}
    for code, name in re.findall(r"\b([A-Z]{3})\s*-\s*([^\n]+?)(?=\b[A-Z]{3}\s*-|Legenda|$)", page_text.replace("\n", " ")):
        name = re.split(r"\b(?:segunda|terca|terça|quarta|quinta|sexta|sabado|sábado|domingo)-feira,|\bpagina\s+\d+\s+de\s+\d+|\bpágina\s+\d+\s+de\s+\d+", name, maxsplit=1, flags=re.IGNORECASE)[0]
        result[code] = " ".join(name.split()).strip()
    return result

def extract_publication(path: Path, month: int, version: str, source_url: str, imported: str, year: int = 2026) -> dict:
    records, pending = [], []
    with pdfplumber.open(path) as pdf:
        page_texts = [page.extract_text() or "" for page in pdf.pages]
        names = legend(page_texts[-1]) if page_texts else {}
        published = ""
        match = re.search(r"(\d{1,2}) de ([A-Za-zÀ-ÿ]+) de (202[0-9])\s*-\s*(\d{2}:\d{2})", "\n".join(page_texts))
        if match:
            months_pt = {"janeiro":1,"fevereiro":2,"marco":3,"abril":4,"maio":5,"junho":6,"julho":7,"agosto":8,"setembro":9,"outubro":10,"novembro":11,"dezembro":12}
            pm = months_pt.get(normalized_code(match.group(2)).lower())
            if pm: published = f"{match.group(3)}-{pm:02d}-{int(match.group(1)):02d} {match.group(4)}"
        for page_no, page in enumerate(pdf.pages[:2], start=1):
            tables = page.extract_tables()
            candidates = [t for t in tables if t and len(t) >= 2 and len(t[0]) >= 20 and t[0][0] and re.match(r"\d{2}/", t[0][0])]
            if not candidates:
                pending.append({"pagina":page_no,"trecho_original":(page_texts[page_no-1][:500]),"campo_afetado":"TABELA","motivo":"Tabela principal nao identificada com seguranca","sugestao_de_revisao":"Revisar visualmente o PDF"})
                continue
            table = candidates[0]
            situation = "PRATICO_EM_SERVICO" if page_no == 1 else "PRATICO_EM_PRONTIDAO"
            headers = table[0]
            for col, header in enumerate(headers):
                hm = re.match(r"(\d{2})/([A-ZÀ-Ü]{3})\s*\n?\s*([A-ZÀ-Ü]{3})", (header or "").upper())
                if not hm: continue
                day, weekday = int(hm.group(1)), normalized_code(hm.group(3))
                date = f"{year}-{month:02d}-{day:02d}"
                for order, row in enumerate(table[1:], start=1):
                    raw = (row[col] or "").strip().replace("\n", " ") if col < len(row) else ""
                    if not raw: continue
                    codes = re.findall(r"[A-Z]{3}", raw.upper())
                    if not codes:
                        pending.append({"pagina":page_no,"trecho_original":raw,"campo_afetado":"TRIGRAMA","motivo":"Celula sem trigrama reconhecivel","sugestao_de_revisao":"Conferir visualmente"})
                    for offset, code in enumerate(codes):
                        try:
                            local_path = path.relative_to(BASE).as_posix()
                        except ValueError:
                            local_path = source_url
                        records.append({"competencia":f"{year}-{month:02d}","versao":version,"data":date,"dia_semana":WEEKDAYS.get(weekday,weekday),"ordem":order+offset,
                            "trigrama":code,"nome":names.get(code,""),"situacao":situation,"observacao":"","arquivo_original":path.name,
                            "caminho_arquivo":local_path,"pagina_original":page_no,"trecho_original":f"{header} | {raw}"})
    return {"competencia":f"{year}-{month:02d}","versao":version,"arquivo":path.name,"url_origem":source_url,"data_publicacao":published,"paginas":len(page_texts),"texto_pesquisavel":all(bool(t.strip()) for t in page_texts),"data_importacao":imported,"registros":records,"pendencias":pending}

def main() -> int:
    imported = datetime.now().astimezone().isoformat(timespec="seconds")
    with (BASE/"LOGS"/"downloads_2026.csv").open(encoding="utf-8-sig", newline="") as fh: downloads=list(csv.DictReader(fh))
    publications=[]
    for row in downloads:
        month=int(row["MES"]); path=BASE/"ARQUIVOS_CPPR"/"2026"/next(p.name for p in (BASE/"ARQUIVOS_CPPR"/"2026").iterdir() if p.name.startswith(f"{month:02d}_"))/row["NOME_SALVO"]
        data=extract_publication(path,month,row["VERSAO"],row["URL_ORIGEM"],imported)
        out=BASE/"DADOS_PROCESSADOS"/f"2026-{month:02d}_{row['VERSAO']}.json"
        out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        publications.append(data); print(f"PROCESSADO {out.name}: {len(data['registros'])} registros")
    master={"gerado_em":imported,"publicacoes":publications}
    (BASE/"DADOS_PROCESSADOS"/"consolidado_2026.json").write_text(json.dumps(master,ensure_ascii=False,indent=2),encoding="utf-8")
    return 0

if __name__ == "__main__": raise SystemExit(main())
