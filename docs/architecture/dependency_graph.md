# Grafo de Dependências da Arquitetura


[Presentation]
    |
    v
[AnalysisOrchestrator] <--- [ErrorHandlerChain]
    |
    v
[CodeFetcherService] <--- [ICodeRepository]
    |
    v
[GitHubRepository] <--- [IConfigProvider]
    |
    v
[ColabConfigProvider / EnvConfigProvider]

[AnalysisOrchestrator] <--- [ILLMProvider]
    |
    v
[OpenAIProvider] <--- [IConfigProvider]

[AnalysisOrchestrator] <--- [PromptLoader]

[AnalysisStrategyRegistry] <--- [AnalysisStrategy]

[AnalysisRequestValidator]


- Cada camada depende apenas de abstrações, nunca de implementações concretas.
- Para adicionar um novo tipo de análise, basta registrar uma nova estratégia e prompt.
- Para trocar o provedor de LLM ou fonte de código, basta registrar uma nova implementação no container.
