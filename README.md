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

`atualizar_projeto_2026.py` cria backup sem duplicar hashes, baixa somente publicações conhecidas de 2026, preserva versões anteriores, processa, reconstrói a planilha e valida. O manifesto do downloader é deliberadamente restritivo; novas URLs oficiais devem ser confirmadas na página CPPR e incluídas na lista `KNOWN_OFFICIAL`. Arquivos fora de 2026 nunca devem ser adicionados.

## GitHub Pages

O projeto usa caminhos relativos e não contém credenciais. Para publicação futura, mantenha `APP`, `PLANILHA` e `ARQUIVOS_CPPR` juntos na mesma estrutura. Configure a raiz do repositório como origem do Pages; não houve publicação automática.

## Limitações

- Fevereiro e agosto a dezembro não estavam localizados na fonte na consulta de 17/07/2026.
- A cadeia TLS da Marinha não foi reconhecida pelo runtime local; o downloader limita domínios e usa hashes para auditoria.
- GitHub Pages pode impor limites de tamanho no futuro; os arquivos atuais são pequenos.
