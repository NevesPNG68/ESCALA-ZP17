# Escala Pública ZP-17 - 2026

Aplicativo estático e base auditável para consulta exclusiva da Escala de Rodízio Única dos Práticos da ZP-17, com competências de 2026 publicadas pela CPPR. Não há banco externo, autenticação ou backend.

## Fonte e escopo

Fonte oficial: https://www.marinha.mil.br/cppr/praticagem

Inclui somente ZP-17 e competências de 2026. Meses sem documento oficial recebem o status `NAO_LOCALIZADO`. Os PDFs em `ARQUIVOS_CPPR/2026` são preservados sem modificação.

## Estrutura

- `APP`: aplicação HTML/CSS/JavaScript e cópia local do SheetJS.
- `ARQUIVOS_CPPR/2026`: documentos originais por mês.
- `DADOS_PROCESSADOS`: JSON auditável por publicação.
- `PLANILHA`: base mestre com as quatro abas exigidas.
- `SCRIPTS`: download, processamento, atualização e validação.
- `BACKUP`, `LOGS` e `RELATORIOS`: preservação e auditoria.

## Instalação e comandos

Execute os comandos abaixo dentro da pasta `ESCALA_ZP17`:

```powershell
python -m pip install -r requirements.txt
python SCRIPTS/baixar_arquivos_2026.py
python SCRIPTS/processar_escalas_2026.py
python SCRIPTS/validar_dados_2026.py
python SCRIPTS/atualizar_projeto_2026.py
```

O gerador da planilha usa Node.js e `@oai/artifact-tool` do runtime do Codex. No ambiente do Codex, ele foi executado com:

```powershell
node work/build_workbook.mjs
```

## Abrir o aplicativo

Na pasta `ESCALA_ZP17`, execute:

```powershell
python -m http.server 8000
```

Acesse `http://localhost:8000/APP/`. Abrir o HTML diretamente pode bloquear a leitura do Excel pelo navegador.

## Atualização

`atualizar_web.py` preserva as publicações já registradas na planilha, lê os links atuais da CPPR e verifica os nomes oficiais do mês corrente, do mês seguinte e da competência mais recente conhecida. Assim, uma nova escala ou ALT entra sem apagar o histórico quando a página estiver temporariamente indisponível. Arquivos fora de 2026 nunca devem ser adicionados.

`verificar_agendamento.py` aplica a política do monitor em horário de Brasília: consulta diária nos cinco dias anteriores ao fim do mês, consulta a cada três dias até o dia 10 do mês seguinte quando a próxima escala ainda não existe, e intervalo de dez dias no restante do ciclo. A execução manual do workflow sempre força uma consulta.

## GitHub Pages

O projeto usa caminhos relativos e não contém credenciais. O workflow `Atualizar escala ZP-17` reconstrói e publica a base no `main` quando detecta uma nova publicação ou ALT; o GitHub Pages acompanha essa alteração automaticamente.

## Limitações

- Competências sem documento oficial permanecem identificadas como `NAO_LOCALIZADO` na aba `PUBLICACOES`.
- A cadeia TLS da Marinha não foi reconhecida pelo runtime local; o downloader limita domínios e usa hashes para auditoria.
- GitHub Pages pode impor limites de tamanho no futuro; os arquivos atuais são pequenos.
