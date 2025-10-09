class AnaliseOrchestratorService:
    def __init__(self, prompt_loader_service, llm_client):
        self.prompt_loader_service = prompt_loader_service
        self.llm_client = llm_client

    def executar_analise(self, analise_request):
        prompt_sistema = self.prompt_loader_service.load_prompt(analise_request.tipo_analise)
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": analise_request.codigo},
            {"role": "user", "content": analise_request.analise_extra if analise_request.analise_extra.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        conteudo_resposta = self.llm_client.chat_completion(
            messages=mensagens,
            model=analise_request.model_name,
            temperature=analise_request.temperature,
            max_tokens=analise_request.max_token_out
        )
        return conteudo_resposta
