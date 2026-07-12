
import re
from typing import Any


class ParserResultado:
    """Limita o número de linhas retornadas na execução do comando."""
    @staticmethod
    def resumir_output(output: str, max_linhas: int = 15) -> str:
        if not output:
            return "(sem output)"

        linhas = output.splitlines()
        if len(linhas) <= max_linhas:
            return output.strip()

        visiveis = linhas[:max_linhas]
        restantes = len(linhas) - max_linhas
        visiveis.append(f"... ({restantes} linhas omitidas)")
        return "\n".join(visiveis)

    # converte valores com % para int
    @staticmethod
    def _maior_percentual(texto: str) -> int:
        valores = [int(x) for x in re.findall(r"(\d{1,3})%", texto)]
        return max(valores) if valores else 0

    # valida se o comando foi executado com sucesso
    @staticmethod
    def detectar_alerta(nome_comando: str, output: str, sucesso: bool) -> str:
        if not sucesso:
            return "O comando falhou — veja o erro."

        texto = output.lower()
        nome = nome_comando.lower()

        # regras de negócio
        if any(k in nome for k in ("disco", "disk", "espaco")):
            pct = ParserResultado._maior_percentual(output)
            if pct >= 95:
                return f"CRÍTICO: disco em {pct}%."
            if pct >= 85:
                return f"ATENÇÃO: disco em {pct}%."

        if "cpu" in nome:
            pct = ParserResultado._maior_percentual(output)
            if pct >= 90:
                return f"CPU alta detectada ({pct}%)."

        if any(k in nome for k in ("memoria", "memory", "mem")):
            pct = ParserResultado._maior_percentual(output)
            if pct >= 90:
                return f"Memória alta detectada ({pct}%)."

        if "connection refused" in texto or "refused" in texto:
            return "Conexão recusada — serviço pode estar inativo."
        if "timeout" in texto:
            return "Timeout detectado."
        if re.search(r"\b(error|failed|fatal)\b", texto):
            return "Erros presentes no output."

        return ""

    @staticmethod
    def gerar_sumario(resultado: dict[str, Any]) -> str:
        status = "Sucesso" if resultado["sucesso"] else "Falha"
        alerta = ParserResultado.detectar_alerta(
            resultado["nome_comando"], resultado["output"], resultado["sucesso"]
        )
        linhas = [
            "─" * 50,
            f"Comando : {resultado['nome_comando']}",
            f"Status  : {status}  ({resultado['tempo_execucao']}s)",
            "─" * 50,
            ParserResultado.resumir_output(resultado["output"]),
            "─" * 50,
            f"Alerta  : {alerta or 'nenhum'}",
        ]
        if resultado.get("erro"):
            linhas += ["", "stderr:", resultado["erro"]]
        return "\n".join(linhas)
