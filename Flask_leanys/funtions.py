import random
import json
import markdown

def obter_questao(materia):
    numero_aleatorio = random.randint(1, 15)
    # Abre o arquivo JSON
    with open(f'database/{materia}/{numero_aleatorio}/details.json', 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    if 'context' in dados:
        dados["context"] = markdown.markdown(dados["context"])
    
    return dados


def obter_questao_n(materia):
    numero_aleatorio = random.randint(1, 45)
    # Abre o arquivo JSON
    with open(f'database/{materia}/{numero_aleatorio}/details.json', 'r', encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    if 'context' in dados:
        dados["context"] = markdown.markdown(dados["context"])
    
    return dados


