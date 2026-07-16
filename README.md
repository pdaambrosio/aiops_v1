# aiops_v1

Agente de diagnóstico de infraestrutura Linux que roda **100% local**. Você faz uma
pergunta em português (ex.: *"como está o uso de disco?"*), o agente escolhe um comando
seguro de uma **whitelist**, executa, e usa um LLM local (via [Ollama](https://ollama.com))
para interpretar a saída e sugerir ações.

Nenhum comando arbitrário é executado: só o que está pré-cadastrado em
`config/commands.py` pode rodar.

---

## Como funciona

O fluxo de uma pergunta (`AIopsV1.processar` em `main.py`):

```
pergunta do usuário
      │
      ▼
DecisionMaker.decidir()          → escolhe um comando da whitelist por palavra-chave
      │
      ▼
DecisionMaker.extrair_parametro()→ extrai host/url/container quando o comando exige
      │
      ▼
ExecutorComando.executar()       → ValidadorComando valida (whitelist + caracteres)
      │                            → shlex.quote nos parâmetros → subprocess
      ▼
ParserResultado.gerar_sumario()  → resume a saída e detecta alertas (disco, cpu, etc.)
      │
      ▼
LLM (Ollama) via PROMPT_ANALISE  → interpreta e recomenda ações
```

### Componentes

| Módulo | Responsabilidade |
|--------|------------------|
| `config/commands.py` | Whitelist de comandos permitidos (`COMANDOS_PERMITIDOS`) e categorias. |
| `config/settings.py` | Configuração via variáveis de ambiente + checagem de conexão com o Ollama. |
| `agent/decision_maker.py` | Mapeia a pergunta para um comando e extrai parâmetros (`host`, `url`, `container`). |
| `agent/llm.py` | Inicializa o cliente `OllamaLLM`. |
| `agent/prompts.py` | Prompt de sistema e template de análise. |
| `core/validator.py` | Valida whitelist e bloqueia caracteres perigosos em parâmetros. |
| `core/executor.py` | Executa o comando com timeout, limites de saída e histórico. |
| `core/parser.py` | Resume a saída e detecta alertas por regra de negócio. |
| `utils/logger.py` | Logger compartilhado do pacote. |
| `main.py` | Loop interativo (REPL) e orquestração. |

---

## Requisitos

- **Python >= 3.13**
- **[Ollama](https://ollama.com)** rodando localmente
- Modelo baixado (padrão `llama3.2:latest`)
- Comandos de sistema Linux disponíveis (`systemctl`, `docker`, `df`, `ping`, etc.) —
  alguns comandos só fazem sentido em ambientes que tenham o serviço correspondente.

---

## Instalação

Este projeto usa [uv](https://github.com/astral-sh/uv).

```bash
# 1. instalar dependências
uv sync

# 2. subir o Ollama e baixar o modelo (em outro terminal)
ollama serve
ollama pull llama3.2:latest
```

---

## Uso

```bash
uv run python main.py
```

No prompt interativo:

```
Você: como está o uso de disco?
Você: mostre os logs do container nginx
Você: faça ping em google.com
Você: comandos          # lista todos os comandos disponíveis
Você: sair              # encerra
```

---

## Configuração

Tudo é configurável por variáveis de ambiente (ver `config/settings.py`):

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL do servidor Ollama. |
| `OLLAMA_MODEL` | `llama3.2:latest` | Modelo usado para a análise. |
| `LLM_TEMPERATURE` | `0.3` | Temperatura do modelo. |
| `OLLAMA_NUM_GPU` | `8` | Nº de camadas na GPU. |
| `COMMAND_TIMEOUT` | `30` | Timeout padrão (s) por comando. |
| `MAX_OUTPUT_LENGTH` | `5000` | Máx. de caracteres de stdout capturados. |
| `MAX_ERROR_LENGTH` | `1000` | Máx. de caracteres de stderr capturados. |
| `LOG_LEVEL` | `INFO` | Nível de log. |
| `DEBUG` | `false` | Modo debug. |

Exemplo:

```bash
OLLAMA_MODEL=llama3.1:8b COMMAND_TIMEOUT=15 uv run python main.py
```

---

## Comandos disponíveis

Definidos em `config/commands.py`, agrupados por categoria:

- **serviços** — `status_nginx`, `status_apache`, `listar_servicos`
- **docker** — `docker_ps`, `docker_stats`, `docker_logs` *(requer `container`)*
- **logs** — `logs_nginx`, `logs_apache`, `logs_app_error`
- **disco** — `espaco_disco`, `tamanho_diretorios`, `tamanho_logs`
- **rede** — `conexoes_ativas`, `conexoes_abertas`, `ping` *(requer `host`)*, `curl_test` *(requer `url`)*
- **processos** — `top_cpu`, `top_memoria`
- **pacotes** — `pacotes_atualizaveis`
- **sistema** — `uptime`, `uname`, `memoria_livre`

Digite `comandos` no prompt para ver a lista completa com descrições.

---

## Segurança

- **Whitelist**: só comandos de `COMANDOS_PERMITIDOS` podem rodar.
- **Parâmetros**: `shlex.quote()` é aplicado antes de montar o comando (`core/executor.py`).
- **Blocklist de caracteres**: `core/validator.py` recusa `;`, `&`, `|`, `` ` ``, `$`, `>`, `<`, etc.
  em parâmetros.

---

## Testes

```bash
uv run pytest
```

Os testes cobrem a validação em `tests/test_validator.py`.

---

## Estrutura do projeto

```
aiops_v1/
├── main.py                 # REPL e orquestração
├── agent/
│   ├── decision_maker.py   # pergunta → comando + extração de parâmetros
│   ├── llm.py              # cliente Ollama
│   └── prompts.py          # prompts do LLM
├── config/
│   ├── commands.py         # whitelist de comandos
│   └── settings.py         # configuração + checagem do Ollama
├── core/
│   ├── validator.py        # validação (whitelist + caracteres)
│   ├── executor.py         # execução com timeout e limites
│   └── parser.py           # resumo e detecção de alertas
├── utils/
│   └── logger.py           # logger do pacote
└── tests/
    └── test_validator.py
```
