from typing import Any
from domain/models.analysis_request import AnalysisRequest
from domain/models.analysis_result import AnalysisResult

class CodeAnalysisService:
    def __init__(self, llm_client, prompt_loader):
        self.llm_client = llm_client
        self.prompt_loader = prompt_loader

    def analyze_code(self, request: AnalysisRequest) -> AnalysisResult:
        prompt_sistema = self.prompt_loader.load_prompt(request.tipo_analise)
        mensagens = self._build_messages(prompt_sistema, request)
        try:
            resposta = self.llm_client.chat_completion(
                messages=mensagens,
                model=request.config.model_name,
                temperature=request.config.temperature,
                max_tokens=request.config.max_tokens
            )
            conteudo = resposta.get('content', '')
            usage = resposta.get('usage', {})
            tokens_usados = usage.get('total_tokens') if usage else None
            modelo_utilizado = resposta.get('model', request.config.model_name)
            return AnalysisResult(
                conteudo=conteudo,
                tokens_usados=tokens_usados,
                modelo_utilizado=modelo_utilizado,
                tempo_execucao_ms=None,
                sucesso=True,
                erro=None
            )
        except Exception as e:
            return AnalysisResult(
                conteudo='',
                tokens_usados=None,
                modelo_utilizado=request.config.model_name,
                tempo_execucao_ms=None,
                sucesso=False,
                erro=str(e)
            )

    def _build_messages(self, prompt_sistema: str, request: AnalysisRequest):
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": request.codigo}
        ]
        if request.instrucoes_extras and request.instrucoes_extras.strip():
            mensagens.append({"role": "user", "content": f'Instruções extras do usuário a serem consideradas na análise: {request.instrucoes_extras}'})
        else:
            mensagens.append({"role": "user", "content": 'Nenhuma instrução extra fornecida pelo usuário.'})
        return mensagens
