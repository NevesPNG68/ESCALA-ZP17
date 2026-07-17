from __future__ import annotations
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
def main():
    data=json.loads((BASE/"DADOS_PROCESSADOS"/"consolidado_2026.json").read_text(encoding="utf-8"))
    pubs=data["publicacoes"]; records=[r for p in pubs for r in p["registros"]]; issues=[]
    keys=[(r["competencia"],r["versao"],r["data"],r["situacao"],r["ordem"],r["trigrama"]) for r in records]
    duplicates=[k for k,c in Counter(keys).items() if c>1]
    if duplicates: issues.append(f"Registros duplicados: {len(duplicates)}")
    outside=[r for r in records if not r["competencia"].startswith("2026-") or not r["data"].startswith("2026-")]
    if outside: issues.append(f"Registros fora de 2026: {len(outside)}")
    missing_source=[r for r in records if not r["arquivo_original"] or not r["pagina_original"]]
    if missing_source: issues.append(f"Registros sem origem completa: {len(missing_source)}")
    available=sorted({int(p["competencia"][-2:]) for p in pubs}); absent=[m for m in range(1,13) if m not in available]
    report=["# Validação dos dados de 2026","",f"Consulta: {datetime.now().astimezone().isoformat(timespec='seconds')}","",f"- Publicações: {len(pubs)}",f"- Registros: {len(records)}",f"- Meses disponíveis: {', '.join(f'{m:02d}' for m in available)}",f"- Meses não localizados: {', '.join(f'{m:02d}' for m in absent)}",f"- Duplicidades exatas: {len(duplicates)}",f"- Registros fora de 2026: {len(outside)}",f"- Registros sem arquivo/página: {len(missing_source)}","", "## Resultado", "", "APROVADO COM PENDÊNCIAS" if issues or absent else "APROVADO", ""]
    if issues: report += ["## Achados",""]+[f"- {i}" for i in issues]
    (BASE/"RELATORIOS"/"validacao_2026.md").write_text("\n".join(report),encoding="utf-8")
    print("VALIDACAO", " | ".join(issues) if issues else "sem inconsistencias estruturais", f"| ausentes={absent}")
    return 1 if outside or duplicates or missing_source else 0
if __name__=="__main__": raise SystemExit(main())
