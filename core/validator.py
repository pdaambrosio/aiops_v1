from typing import Optional
from config import COMANDOS_PERMITIDOS

CARACTERES_PROIBIDOS = [";", "&", "|", "`", "$", ">", "<", "\n", "\\"]


class ResultadoValidacao:
    """Retorno estruturando/schema"""
    def __init__(self, valido: bool, erro: Optional[str] = None, config: Optional[dict] = None):
        self.valido = valido
        self.erro = erro
        self.config = config

    # metodo bool para retorno boleano direto em uma condicional
    def __bool__(self) -> bool:
        return self.valido


class ValidadorComando:
    """Valida o comando e os parâmetros utilizados"""
    def __init__(self) -> None:
        self.historico: list[dict] = []

    # valida se o comando utilizado está na whitelist
    def validar(self, nome_comando: str, parametros: Optional[dict[str, str]] = None) -> ResultadoValidacao:
        config = COMANDOS_PERMITIDOS.get(nome_comando)
        if config is None:
            exemplos = ", ".join(list(COMANDOS_PERMITIDOS)[:5])
            erro = (
                f"Comando '{nome_comando}' não está na whitelist. "
                f"Exemplos válidos: {exemplos}..."
            )
            self._registrar(nome_comando, False, "fora da whitelist")
            return ResultadoValidacao(False, erro)

        param_esperado = config.get("requer_parametro")
        if param_esperado:
            if not parametros or param_esperado not in parametros:
                erro = f"Comando '{nome_comando}' exige o parâmetro '{param_esperado}'."
                self._registrar(nome_comando, False, "parâmetro ausente")
                return ResultadoValidacao(False, erro)

            valor = parametros[param_esperado]
            erro_param = self._validar_valor_parametro(param_esperado, valor)
            if erro_param:
                self._registrar(nome_comando, False, "parâmetro inseguro")
                return ResultadoValidacao(False, erro_param)

        self._registrar(nome_comando, True, "ok")
        return ResultadoValidacao(True, None, config)

    # valida se o comando utilizado requer parametro e se o mesmo contém caracteres proibidos
    def _validar_valor_parametro(self, nome: str, valor: str) -> Optional[str]:
        if not valor or not valor.strip():
            return f"Parâmetro '{nome}' está vazio."

        for c in CARACTERES_PROIBIDOS:
            if c in valor:
                return (
                    f"Parâmetro '{nome}' contém caractere proibido "
                    f"({c!r}). Bloqueado por segurança."
                )
        return None

    # inclui o comando no historico para auditoria
    def _registrar(self, nome_comando: str, valido: bool, motivo: str) -> None:
        self.historico.append(
            {"comando": nome_comando, "valido": valido, "motivo": motivo}
        )

    # lista os comandos da whitelist
    def listar_comandos_validos(self) -> list[str]:
        return list(COMANDOS_PERMITIDOS)

    # obten informações do comando utilizando via whitelist
    def obter_info(self, nome_comando: str) -> Optional[dict]:
        return COMANDOS_PERMITIDOS.get(nome_comando)
