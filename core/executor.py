import shlex
import subprocess
from datetime import datetime
from typing import Optional

from config import COMMAND_TIMEOUT, MAX_OUTPUT_LENGTH, MAX_ERROR_LENGTH
from utils import get_logger
from validator import ValidadorComando

logger = get_logger(__name__)


class ExecutorComando:
    """Executa comandos da whitelist com validação, timeout e limites."""
    def __init__(self, timeout_padrao: int = COMMAND_TIMEOUT) -> None:
        self.timeout_padrao = timeout_padrao
        self.validador = ValidadorComando()
        self.historico: list[dict] = []

    def executar(self, nome_comando: str, parametros: Optional[dict[str, str]] = None,) -> dict:
        inicio = datetime.now()

        # validação (whitelist + parâmetros)
        validacao = self.validador.validar(nome_comando, parametros)
        if not validacao:
            return self._falha(nome_comando, validacao.erro, inicio, "validação")

        config = validacao.config
        comando = config["comando"]
        timeout = config.get("timeout", self.timeout_padrao)

        # substituição segura de parâmetros
        if "{" in comando:
            try:
                seguros = {k: shlex.quote(v) for k, v in (parametros or {}).items()}
                comando = comando.format(**seguros)
            except KeyError as e:
                return self._falha(
                    nome_comando, f"Parâmetro ausente: {e}", inicio, "formatação"
                )

        # execução
        logger.info("Executando '%s': %s", nome_comando, comando)
        try:
            proc = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            resultado = {
                "nome_comando": nome_comando,
                "sucesso": proc.returncode == 0,
                "output": proc.stdout[:MAX_OUTPUT_LENGTH],
                "erro": (proc.stderr or "")[:MAX_ERROR_LENGTH],
                "codigo_retorno": proc.returncode,
                "tempo_execucao": self._segundos(inicio),
                "timestamp": datetime.now().isoformat(),
                "motivo_falha": None if proc.returncode == 0 else f"returncode={proc.returncode}",
            }
        except subprocess.TimeoutExpired:
            resultado = self._falha(
                nome_comando, f"Excedeu timeout de {timeout}s", inicio, "timeout"
            )
        except Exception as e:  # noqa: BLE001
            resultado = self._falha(nome_comando, str(e), inicio, "exceção")

        self.historico.append(resultado)
        return resultado

    def _falha(self, nome_comando: str, erro: str, inicio: datetime, motivo: str) -> dict:
        logger.warning("Falha em '%s' (%s): %s", nome_comando, motivo, erro)
        resultado = {
            "nome_comando": nome_comando,
            "sucesso": False,
            "output": "",
            "erro": erro,
            "codigo_retorno": -1,
            "tempo_execucao": self._segundos(inicio),
            "timestamp": datetime.now().isoformat(),
            "motivo_falha": motivo,
        }
        self.historico.append(resultado)
        return resultado

    @staticmethod
    def _segundos(inicio: datetime) -> float:
        return round((datetime.now() - inicio).total_seconds(), 2)

    def listar_comandos(self, categoria: Optional[str] = None) -> list[str]:
        if categoria is None:
            return self.validador.listar_comandos_validos()
        from config import COMANDOS_PERMITIDOS
        return [n for n, c in COMANDOS_PERMITIDOS.items()
                if c.get("categoria") == categoria]

    def obter_historico(self) -> list[dict]:
        return self.historico

    def limpar_historico(self) -> None:
        self.historico.clear()

# local test
if __name__ == "__main__":
    executor = ExecutorComando()

    resultado_true = executor.executar("uptime")
    print(resultado_true)
    print()

    resultado_false = executor.executar("ping", {"host": "google.com; rm -rf /"})
    print(resultado_false)