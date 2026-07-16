import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from langchain_core.output_parsers import StrOutputParser  # noqa: E402

from config import (  # noqa: E402
    COMANDOS_PERMITIDOS,
    CATEGORIAS_COMANDOS,
    exibir_configuracoes,
    validar_configuracoes,
)

from core import ExecutorComando, ParserResultado  # noqa: E402
from agent import inicializar_llm, DecisionMaker, PROMPT_ANALISE  # noqa: E402
from utils import get_logger  # noqa: E402

logger = get_logger(__name__)


class AIopsV1:
    def __init__(self) -> None:
        print("\n" + "=" * 60)
        print("Agente AIopsV1")
        print("=" * 60)
        exibir_configuracoes()

        if not validar_configuracoes():
            print("Ollama não respondeu. Rode 'ollama serve' antes de continuar.")

        self.executor = ExecutorComando()
        self.decisor = DecisionMaker()
        self.llm = inicializar_llm()

        self.cadeia_analise = PROMPT_ANALISE | self.llm | StrOutputParser()
        logger.info("Agente pronto.")

    def processar(self, pergunta: str) -> str:
        # decidir
        nome_comando, razao = self.decisor.decidir(pergunta)
        config = COMANDOS_PERMITIDOS[nome_comando]
        print(f"\nComando escolhido: {nome_comando}  ({razao})")

        # parâmetro, se o comando exigir
        parametros = None
        param_esperado = config.get("requer_parametro")
        if param_esperado:
            valor = self.decisor.extrair_parametro(pergunta, param_esperado)
            if not valor:
                return (
                    f"O comando '{nome_comando}' precisa do parâmetro "
                    f"'{param_esperado}', mas não consegui extraí-lo da pergunta. "
                    f"Ex.: 'logs do container nginx' ou 'ping em google.com'."
                )
            parametros = {param_esperado: valor}
            print(f"   parâmetro: {param_esperado}={valor}")

        print("⚙️  Executando...")
        resultado = self.executor.executar(nome_comando, parametros)

        print("\n" + ParserResultado.gerar_sumario(resultado))

        print("\n📊 Analisando com IA...\n")
        try:
            analise = self.cadeia_analise.invoke(
                {
                    "pergunta": pergunta,
                    "nome_comando": nome_comando,
                    "descricao": config["descricao"],
                    "sucesso": resultado["sucesso"],
                    "output": resultado["output"] or "(vazio)",
                    "erro": resultado["erro"] or "(nenhum)",
                }
            )
        except Exception as e:  # noqa: BLE001
            logger.error("Falha ao analisar com o LLM", exc_info=True)
            return f"Comando executado, mas a análise via LLM falhou: {e}"

        return analise

    def listar_comandos(self) -> None:
        print("\nCOMANDOS DISPONÍVEIS")
        for categoria in sorted(CATEGORIAS_COMANDOS):
            print(f"\n  [{categoria}]")
            for nome in CATEGORIAS_COMANDOS[categoria]:
                print(f"    • {nome:22} {COMANDOS_PERMITIDOS[nome]['descricao']}")


def main() -> None:
    try:
        agente = AIopsV1()
    except ConnectionError as e:
        print(f"\n{e}")
        sys.exit(1)

    print("\nDigite uma pergunta, 'comandos' para listar, ou 'sair'.\n")
    while True:
        try:
            entrada = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break

        if not entrada:
            continue
        if entrada.lower() in {"sair", "exit", "quit"}:
            print("Até logo!")
            break
        if entrada.lower() in {"comandos", "listar"}:
            agente.listar_comandos()
            continue

        try:
            resposta = agente.processar(entrada)
            print(f"\nAgente:\n{resposta}\n")
        except Exception as e:  # noqa: BLE001
            logger.error("Erro ao processar pergunta", exc_info=True)
            print(f"\nErro: {e}\n")


if __name__ == "__main__":
    main()
