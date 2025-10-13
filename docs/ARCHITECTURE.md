# Documentação de Arquitetura

## Visão Geral
O Agent-Vinna é uma solução baseada em agentes de IA para análise automatizada de código, exposta via API Flask. O sistema é modular, permitindo fácil extensão e manutenção.

## Diagrama de Componentes


+-------------------+
|    Usuário/API    |
+--------+----------+
         |
         v
+--------+----------+
|     Flask API     |
+--------+----------+
         |
         v
+--------+----------+
|  agents/          |
| - agente_revisor  |
+--------+----------+
         |
         v
+--------+----------+
| infrastructure/   |
| - openai_llm_provider.py |
+--------+----------+
         |
         v
+--------+----------+
| tools/            |
| - github_reader.py|
| - prompt/         |
+-------------------+


## Fluxo de Dados
1. O usuário faz uma requisição para a API Flask (`/executar_analise`).
2. O endpoint chama o agente especializado (`agente_revisor`) conforme o tipo de análise.
3. O agente utiliza adaptadores LLM (ex: OpenAI) e ferramentas para leitura de código do GitHub.
4. O resultado é processado e retornado em formato estruturado.

## Descrição dos Módulos
- **agents/**: Contém agentes especialistas para cada tipo de análise (design, segurança, pentest).
- **infrastructure/**: Adaptadores para provedores de LLM e outros serviços externos.
- **tools/**: Utilitários para leitura de repositórios, prompts customizados e ferramentas auxiliares.
- **docs/**: Documentação técnica e de arquitetura.

## Decisões Arquiteturais
- **Flask** foi escolhido pela simplicidade e robustez para APIs Python.
- **Agentes especializados**: Cada tipo de análise é tratado por um agente dedicado, facilitando manutenção e evolução.
- **Modularidade**: Separação clara entre API, lógica de agentes, infraestrutura e ferramentas.
- **Extensibilidade**: Novos agentes ou adaptadores podem ser adicionados facilmente.

## Segurança & Observabilidade
- Variáveis sensíveis são gerenciadas via `.env`.
- Logs de erro são capturados e exibidos no console.
- Recomenda-se integração futura com ferramentas de observabilidade e monitoramento.
