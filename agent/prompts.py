from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """Você é um engenheiro DevOps sênior assistindo no diagnóstico \
de infraestrutura Linux. Recebe a saída real de comandos do sistema e deve \
interpretá-la com precisão.

Regras:
- Baseie-se apenas nos dados fornecidos; não invente números.
- Seja direto e técnico, mas explique o raciocínio.
- Se detectar um problema, aponte a causa provável e a ação recomendada.
- Se estiver tudo normal, diga isso claramente.
- Responda em português.
"""

PROMPT_ANALISE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Pergunta do usuário:\n{pergunta}\n\n"
            "Comando executado: {nome_comando}\n"
            "Descrição: {descricao}\n"
            "Sucesso: {sucesso}\n\n"
            "Saída do comando:\n"
            "```\n{output}\n```\n\n"
            "stderr (se houver):\n{erro}\n\n"
            "Forneça:\n"
            "1. Interpretação dos dados\n"
            "2. Problema detectado (ou 'nenhum')\n"
            "3. Recomendação prática\n"
            "4. Próximo passo sugerido",
        ),
    ]
)