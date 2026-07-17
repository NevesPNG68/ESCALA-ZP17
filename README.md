# Escala PÃºblica ZP-17 - 2026

Aplicativo estÃ¡tico e base auditÃ¡vel para consulta exclusiva da Escala de RodÃ­zio Ãšnica dos PrÃ¡ticos da ZP-17, com competÃªncias de 2026 publicadas pela CPPR. NÃ£o hÃ¡ banco externo, autenticaÃ§Ã£o ou backend.

## Fonte e escopo

Fonte oficial: https://www.marinha.mil.br/cppr/praticagem

Inclui somente ZP-17 e competÃªncias de 2026. Meses sem documento oficial recebem o status `NAO_LOCALIZADO`. Os PDFs em `ARQUIVOS_CPPR/2026` sÃ£o preservados sem modificaÃ§Ã£o.

## Estrutura

- `APP`: aplicaÃ§Ã£o HTML/CSS/JavaScript e cÃ³pia local do SheetJS.
- `ARQUIVOS_CPPR/2026`: documentos originais por mÃªs.
- `DADOS_PROCESSADOS`: JSON auditÃ¡vel por publicaÃ§Ã£o.
- `PLANILHA`: base mestre com as quatro abas exigidas.
- `SCRIPTS`: download, processamento, atualizaÃ§Ã£o e validaÃ§Ã£o.
- `BACKUP`, `LOGS` e `RELATORIOS`: preservaÃ§Ã£o e auditoria.

## InstalaÃ§Ã£o e comandos

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

## AtualizaÃ§Ã£o

`atualizar_projeto_2026.py` cria backup sem duplicar hashes, baixa somente publicaÃ§Ãµes conhecidas de 2026, preserva versÃµes anteriores, processa, reconstrÃ³i a planilha e valida. O manifesto do downloader Ã© deliberadamente restritivo; novas URLs oficiais devem ser confirmadas na pÃ¡gina CPPR e incluÃ­das na lista `KNOWN_OFFICIAL`. Arquivos fora de 2026 nunca devem ser adicionados.

## GitHub Pages

O projeto usa caminhos relativos e nÃ£o contÃ©m credenciais. Para publicaÃ§Ã£o futura, mantenha `APP`, `PLANILHA` e `ARQUIVOS_CPPR` juntos na mesma estrutura. Configure a raiz do repositÃ³rio como origem do Pages; nÃ£o houve publicaÃ§Ã£o automÃ¡tica.

## LimitaÃ§Ãµes

- Fevereiro e agosto a dezembro nÃ£o estavam localizados na fonte na consulta de 17/07/2026.
- A cadeia TLS da Marinha nÃ£o foi reconhecida pelo runtime local; o downloader limita domÃ­nios e usa hashes para auditoria.
- GitHub Pages pode impor limites de tamanho no futuro; os arquivos atuais sÃ£o pequenos.

