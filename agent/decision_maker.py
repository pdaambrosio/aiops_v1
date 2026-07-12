import re
from typing import Optional

ROLES: list[tuple[list[str], str]] = [
    (["nginx"], "status_nginx"),
    (["apache"], "status_apache"),
    (["docker", "container", "containers"], "docker_ps"),
    (["memória", "memoria", " ram", "swap"], "top_memoria"),
    (["cpu", "processador", "processamento"], "top_cpu"),
    (["processo", "processos"], "top_cpu"),
    (["disco", "espaço", "espaco", "storage", "armazenamento"], "espaco_disco"),
    (["log", "logs", "erro", "erros", "error"], "logs_app_error"),
    (["porta", "portas", "conexão", "conexao", "conexões", "rede", "listen"], "conexoes_ativas"),
    (["ping", "conectividade"], "ping"),
    (["pacote", "pacotes", "atualiz", "update", "upgrade"], "pacotes_atualizaveis"),
    (["uptime", "quanto tempo", "ligado", "load"], "uptime"),
    (["kernel", "versão do sistema", "versao do sistema", "uname"], "uname"),
    (["serviço", "servico", "serviços", "servicos", "status geral"], "listar_servicos"),
]

DEFAULT_COMMAND = "listar_servicos"

class DecisionMaker:
    """Map the question"""
    def decidir(self, pergunta: str) -> tuple[str, str]:
        texto = f" {pergunta.lower()} "
        for palavras, comando in ROLES:
            for kw in palavras:
                if kw in texto:
                    return comando, f"palavra-chave '{kw.strip()}'"
        return DEFAULT_COMMAND, "nenhuma palavra-chave específica; diagnóstico padrão"

    def extrair_parametro(self, pergunta: str, chave: str) -> Optional[str]:
        texto = pergunta.strip()

        if chave == "url":
            m = re.search(r"https?://[^\s,]+", texto)
            return m.group(0) if m else None

        if chave == "host":
            m = re.search(r"\b(?:\d{1,3}(?:\.\d{1,3}){3}|[a-z0-9.-]+\.[a-z]{2,})\b",
                          texto, re.IGNORECASE)
            return m.group(0) if m else None

        if chave == "container":
            m = re.search(r"(?:container|docker)\s+(?:do\s+|de\s+|the\s+)?([a-zA-Z0-9_.-]+)",
                          texto, re.IGNORECASE)
            return m.group(1) if m else None

        return None
