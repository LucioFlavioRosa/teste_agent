from tools.revisor_geral import executar_analise_llm

def strategy_design(tipo_analise, codigo, instrucoes_extras, model_name, max_token_out):
    return executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )

def strategy_pentest(tipo_analise, codigo, instrucoes_extras, model_name, max_token_out):
    return executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )

def strategy_seguranca(tipo_analise, codigo, instrucoes_extras, model_name, max_token_out):
    return executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )

def strategy_terraform(tipo_analise, codigo, instrucoes_extras, model_name, max_token_out):
    return executar_analise_llm(
        tipo_analise=tipo_analise,
        codigo=str(codigo),
        analise_extra=instrucoes_extras,
        model_name=model_name,
        max_token_out=max_token_out
    )

ANALISE_STRATEGIES = {
    "design": strategy_design,
    "pentest": strategy_pentest,
    "seguranca": strategy_seguranca,
    "terraform": strategy_terraform,
}
