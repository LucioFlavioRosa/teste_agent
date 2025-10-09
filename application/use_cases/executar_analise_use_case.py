from domain/interfaces/code_source_interface import ICodeSource
from domain/interfaces/llm_interface import ILLMProvider
from domain/services/validation_service import ValidationService
from domain/services/code_formatter_service import CodeFormatterService
from domain/value_objects/tipo_analise import TipoAnalise

class ExecutarAnaliseUseCase:
    def __init__(self, code_source: ICodeSource, llm_provider: ILLMProvider):
        self.code_source = code_source
        self.llm_provider = llm_provider

    def executar(self, tipo_analise, repositorio=None, codigo_entrada=None, instrucoes_extras="", model_name="gpt-4.1", max_token_out=3000):
        TipoAnalise.validar(tipo_analise)
        ValidationService.validar_entrada_codigo(repositorio_nome=repositorio, codigo_entrada=codigo_entrada)
        if codigo_entrada is not None:
            codigo_para_analise = codigo_entrada
        else:
            codigo_para_analise = self.code_source.obter_codigo(repositorio, tipo_analise)
        if not codigo_para_analise:
            return {"tipo_analise": tipo_analise, "resultado": 'Não foi fornecido nenhum código para análise'}
        codigo_final = CodeFormatterService.montar_codigo_para_llm(codigo_para_analise)
        prompt_sistema = None  # O prompt do sistema deve ser carregado externamente
        mensagens = [
            {"role": "system", "content": prompt_sistema},
            {'role': 'user', 'content': codigo_final},
            {'role': 'user', 'content': f'Instruções extras do usuário a serem consideradas na análise: {instrucoes_extras}' if instrucoes_extras.strip() else 'Nenhuma instrução extra fornecida pelo usuário.'}
        ]
        resultado = self.llm_provider.executar_analise(prompt_sistema, mensagens, model_name, max_token_out)
        return {"tipo_analise": tipo_analise, "resultado": resultado}