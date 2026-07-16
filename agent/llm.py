from langchain_ollama import OllamaLLM
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, LLM_TEMPERATURE, OLLAMA_NUM_GPU
from utils import get_logger

logger = get_logger(__name__)

def inicializar_llm(testar: bool = True) -> OllamaLLM:
    """ Create LLM Agent """
    logger.info("Conectando ao Ollama em %s (modelo=%s)", OLLAMA_BASE_URL, OLLAMA_MODEL)
    llm = OllamaLLM(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=LLM_TEMPERATURE,
        num_gpu=OLLAMA_NUM_GPU
    )

    if testar:
        try:
            llm.invoke("ok")
        except Exception as e:
            raise ConnectionError(
                f"Não foi possível conectar ao Ollama em {OLLAMA_BASE_URL}. "
                f"Rode 'ollama serve' e confirme que o modelo '{OLLAMA_MODEL}' "
                f"foi baixado (ollama pull {OLLAMA_MODEL}). Detalhe: {e}"
            ) from e

    logger.info("Ollama conectado.")
    return llm