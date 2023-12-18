import json
import random
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi import APIRouter
from config_db import projetoPAA
from fastapi.middleware.cors import CORSMiddleware
import anytree
from anytree import Node
app = FastAPI()

# Origens do frontend permitidas
origins = ["http://localhost:3000"]

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def geraPerg(sintoma = str):
    if sintoma == "impulso":
        return "Melhorar seu impulso é uma prioridade?"
    elif sintoma == "agilidade":
        return "Ficar mais ágil é uma prioridade?"
    elif sintoma == "forca":
        return "Ficar mais forte é uma prioridade?"
    elif sintoma == "resistencia":
        return "Melhorar sua resistencia é uma prioridade?"
    elif sintoma == "ritmo":
        return "Melhorar seu ritmo é uma prioridade?"
    elif sintoma == "tecnica":
        return "Realizar uma atividade que envolve tecnica é uma prioridade?"
    elif sintoma == "reflexo":
        return "Você procura uma atividade para melhorar seus reflexos?"
    elif sintoma == "boa_condicao_financeira":
        return "Você está disposto a pagar uma quantidade significativa de dinheiro?"
    elif sintoma == "flexibilidade":
        return "Ficar mais flexível é uma prioridade?"
    elif sintoma == "capacidade_pulmonar":
        return "Você procura uma atividade para melhorar sua capacidade pulmonar?"
    elif sintoma == "equilibrio":
        return "Você procura uma atividade para melhorar seu equilíbrio?"
    elif sintoma == "ganhar_massa":
        return "Ganhar massa magra, músculos, é uma prioridade?"
    elif sintoma == "definicao_corporal":
        return "Você procura ter um corpo definido?"
    elif sintoma == "perca_massa":
        return "Você prioriza perder massa gorda?"
    elif sintoma == "utilizar_melhoradores_de_perf_atletica":
        return "Você se dispõe a utilizar melhoradores de performance atlética, com acompanhamento médico?"

def getPerguntados(pai = Node):
    perguntados = ''
    if pai.name != 'Origem':
        if pai.name != 'Sim' and pai.name != 'Nao' and pai.name != 'Nao_Sei':
            perguntados = pai.name + ' '
            return getPerguntados(pai.parent) + perguntados
        else:
            return getPerguntados(pai.parent)
    else:
        return perguntados

def getRespostas(pai):
    respostas = ''
    if pai.name != 'Origem':
        if pai.name == 'Sim' or pai.name == 'Nao' or pai.name == 'Nao_Sei':
            respostas = pai.name + ' '
            return getRespostas(pai.parent) + respostas
        else:
            return getRespostas(pai.parent)
    else:
        return respostas

def getNegados(perguntados, respostas):
    negados = []
    if respostas:
        for i in range(len(perguntados)):
            if respostas[i] == 'Nao':
                negados.append(perguntados[i])
    return negados

def getAfirmados(perguntados, respostas):
    afirmados = []
    if respostas:
        for i in range(len(perguntados)):
            if respostas[i] == 'Sim':
                afirmados.append(perguntados[i])
    return afirmados



def probabilidades(afirmads, negads, dictRegraCausas):
    res = []
    probs = []
    for item in dictRegraCausas:
        aProb = dictRegraCausas[item].prob
        for af in afirmads:
            if af in dictRegraCausas[item].sintYes1:
                aProb+= 0.2
            elif af in dictRegraCausas[item].sintYes2:
                aProb+= 0.1
            elif af in dictRegraCausas[item].sintYes3:
                aProb+= 0.05
        for neg in negads:
            if neg in dictRegraCausas[item].sintNot1:
                aProb+= 0.2
            elif neg in dictRegraCausas[item].sintNot2:
                aProb+= 0.1
            elif neg in dictRegraCausas[item].sintNot3:
                aProb+= 0.05
        if aProb >= 0.7:
            res.append(item)
            probs.append(aProb)
    if res:
        j = 0
        t = ''
        reps = 0
        for i in range(len(res)):
            if probs[i] > j:
                j = probs[i]
                t = res[i]
            elif probs[i] == j:
                reps+=1
        if reps == len(res):
            rand = random.randint(0, len(res)-1)
            return res[rand]
        else:
            return t
    else:
        return 0


def retornaListaFilhos(branch=Node):
    children = []
    if branch.is_leaf == False:
        for child in branch.children:
            if child.is_leaf == False:
                children.append(child.name)
                children.append(retornaListaFilhos(child))
            else:
                children.append(child.name)
    else:
        children = branch.name
    return children


def refazArvore(lista, node):
    if type(lista) == list:
        if node != '':
            if lista:
                if len(lista[0]) > 2:
                    for item in lista:
                        branch = Node(item, parent=node)
                elif len(lista[0]) == 1:
                    branch = Node(lista[0], parent=node)
                else:
                    branch = Node(lista[0], parent=node)
                    return refazArvore(lista[1],branch)
        else:
            if lista:
                root = Node(lista[0][0])
                return refazArvore(lista[1],root)


def getRota(node):
    if node.name != 'Origem':
        respostas = ' '+node.name
        return getRota(node.parent) + respostas
    else:
        return node.name


class RegraCausa:
    causa: str  # Nome da causa
    YY: list  # Lista de tuplas
    YN: list  # Lista de tuplas
    NN: list  # Lista de tuplas
    sintYes1: list  # Lista de sintomas que ao serem verdadeiros aumentam chance da causa
    sintYes2: list
    sintYes3: list
    sintNot1: list  # Lista de sintomas que ao serem falsos aumentam chance da causa
    sintNot2: list
    sintNot3: list
    prob = 0


class RegraSintoma:
        sintoma: str  # Nome do sintoma
        sintYes: list  # Lista de sintomas que ao serem verdadeiros aumentam chance da causa
        sintNot: list  # Lista de sintomas que ao serem falsos aumentam chance da causa
        ocorrencias: int

class texto(BaseModel):
    txt: str


@app.get("/Regras")
async def get_Regras():
    """
    Retorna todas a base de dados como um dicionario.
    """
    regras = projetoPAA.reference("/Regras").get()
    for item in regras:
        regras = regras[item]
        break
    return regras

@app.get("/Regras/Arvore/display")
async def get_Arvore():
    """
    Retorna a Arvore como uma lista.
    """
    arvore = projetoPAA.reference("/Regras/Arvore").get()
    for item in arvore:
        arvore = arvore[item]
        break
    return arvore

@app.get("/Regras/Questionario/get-pergunta")
async def get_Pergunta():
    """
    Retorna uma pergunta sobre um sintoma.
    Utilize post-resposta para responder a pergunta.
    """
    sints = projetoPAA.reference("/Regras/Sintomas").get()
    rota = projetoPAA.reference("/Regras/Rota").get()
    if not rota:
        listSint = []
        for item in sints:
            listSint.append(sints[item]["sintoma"])
        rand = random.randint(0,len(listSint)-1)
        res = listSint[rand]
        r = geraPerg(res)
        rota = []
        rota.append(res)
        projetoPAA.reference("/Regras/Rota").delete()
        projetoPAA.reference("/Regras/Rota").push(rota)
        return r
    else:
        for it in rota:
            rota = rota[it]
            break
        listSint = []
        for item in sints:
            if sints[item]["sintoma"] not in rota:
                listSint.append(sints[item]["sintoma"])
        if len(rota)/2 < len(listSint):
            rand = random.randint(0,len(listSint)-1)
            res = listSint[rand]
            r = geraPerg(res)
            rota.append(res)
            projetoPAA.reference("/Regras/Rota").delete()
            projetoPAA.reference("/Regras/Rota").push(rota)
            return r
        else:
            return "RESPOSTA INCONCLUSIVA."


#           CREATE
@app.post("/inserirBaseDeDados")
async def inserir_base_de_dados():
    """
    Formata e insere o arquivo de regras no FireBase.
    NAO EXECUTAR CASO JA EXISTAM AS REGRAS NA BASE DE DADOS.

    """
    f = open("regras.txt", "r")
    # Declara dicts
    dictRegraCausas = {}
    dictRegraSintomas = {}

    # Declara listas
    listCausas = []

    # Loop principal para cada linha x no arquivo f
    for x in f:
            # Corta a string x e guarda na variavel linha
            linha = x.split(',')
            if len(linha) > 1:  # Se o tamanho da variavel for maior que 1
                if linha[0][1] == 'C':  # Se eh uma causa
                    nomeCausa = linha[0][3:-1]  # Salva nome da causa
                    if nomeCausa not in dictRegraCausas:  # Se a causa nao existe cria ela
                        dictRegraCausas[nomeCausa] = RegraCausa()
                        dictRegraCausas[nomeCausa].causa = nomeCausa
                        dictRegraCausas[nomeCausa].YY = []
                        dictRegraCausas[nomeCausa].YN = []
                        dictRegraCausas[nomeCausa].NN = []
                        dictRegraCausas[nomeCausa].sintYes1 = []
                        dictRegraCausas[nomeCausa].sintYes2 = []
                        dictRegraCausas[nomeCausa].sintYes3 = []
                        dictRegraCausas[nomeCausa].sintNot1 = []
                        dictRegraCausas[nomeCausa].sintNot2 = []
                        dictRegraCausas[nomeCausa].sintNot3 = []
                        dictRegraCausas[nomeCausa].prob = 0

                    if nomeCausa not in listCausas:
                        listCausas.append(nomeCausa)

                    # Declara uma lista com os sintomas
                    sintomas = linha[1].split(';')
                    # Declara uma variavel para NOT de fora dos sintomas
                    isNOT = False
                    # Checa se tem NOT fora dos sintomas
                    if sintomas[0][0:3] == "NOT":
                        isNOT = True
                        # Retira o NOT de fora dos sintomas
                        sintomas[0] = sintomas[0][3:]

                    # Declara variaveis
                    sint1 = ''
                    sint2 = ''
                    # Variaveis para NOT no sintoma 1 e no sintoma 2
                    isNOTsint1 = False
                    isNOTsint2 = False

                    # Se sintoma 1 for NOT
                    if sintomas[0][1:4] == "NOT":
                        sint1 = sintomas[0][7:-1]
                        isNOTsint1 = True
                    # Se sintoma 1 nao eh NOT
                    else:
                        sint1 = sintomas[0][4:-1]
                    # Se sintoma 2 for NOT
                    if sintomas[1][0:3] == "NOT":
                        sint2 = sintomas[1][7:-2]
                        isNOTsint2 = True
                    # Se sintoma 2 nao eh NOT
                    else:
                        sint2 = sintomas[1][3:-2]

                    if sint1 not in dictRegraSintomas:
                        dictRegraSintomas[sint1] = RegraSintoma()
                        dictRegraSintomas[sint1].sintoma = sint1
                        dictRegraSintomas[sint1].sintYes = []
                        dictRegraSintomas[sint1].sintNot = []
                        dictRegraSintomas[sint1].ocorrencias = 1
                    else:
                        if sint1 not in dictRegraCausas[nomeCausa].sintNot1 and sint1 not in dictRegraCausas[
                            nomeCausa].sintYes1:
                            dictRegraSintomas[sint1].ocorrencias += 1

                    if sint2 not in dictRegraSintomas:
                        dictRegraSintomas[sint2] = RegraSintoma()
                        dictRegraSintomas[sint2].sintoma = sint2
                        dictRegraSintomas[sint2].sintYes = []
                        dictRegraSintomas[sint2].sintNot = []
                        dictRegraSintomas[sint2].ocorrencias = 1
                    else:
                        if sint2 not in dictRegraCausas[nomeCausa].sintNot1 and sint2 not in dictRegraCausas[
                            nomeCausa].sintYes1:
                            dictRegraSintomas[sint2].ocorrencias += 1

                    # Analisa os dois sintomas e guarda no dict
                    # formato ?(?;?) cada interrogacao lida com um possivel NOT
                    # Y(?;?)
                    if isNOT == False:
                        # Y(Y;?)
                        if isNOTsint1 == False:
                            # Y(Y;Y)
                            if isNOTsint2 == False:
                                dictRegraCausas[nomeCausa].YY.append([sint1, sint2])
                                if float(linha[2]) == 0.5:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes1:
                                        dictRegraCausas[nomeCausa].sintYes1.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes1:
                                        dictRegraCausas[nomeCausa].sintYes1.append(sint2)
                                elif float(linha[2]) == 0.3:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes2:
                                        dictRegraCausas[nomeCausa].sintYes2.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes2:
                                        dictRegraCausas[nomeCausa].sintYes2.append(sint2)
                                elif float(linha[2]) == 0.15:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes3:
                                        dictRegraCausas[nomeCausa].sintYes3.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes3:
                                        dictRegraCausas[nomeCausa].sintYes3.append(sint2)
                            # Y(Y;N)
                            else:
                                dictRegraCausas[nomeCausa].YN.append([sint1, sint2])
                                if float(linha[2]) == 0.5:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes1:
                                        dictRegraCausas[nomeCausa].sintYes1.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot1:
                                        dictRegraCausas[nomeCausa].sintNot1.append(sint2)
                                elif float(linha[2]) == 0.3:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes2:
                                        dictRegraCausas[nomeCausa].sintYes2.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot2:
                                        dictRegraCausas[nomeCausa].sintNot2.append(sint2)
                                elif float(linha[2]) == 0.15:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes3:
                                        dictRegraCausas[nomeCausa].sintYes3.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot3:
                                        dictRegraCausas[nomeCausa].sintNot3.append(sint2)
                        # Y(N;?)
                        else:
                            # Y(N;Y)
                            if isNOTsint2 == False:
                                dictRegraCausas[nomeCausa].YN.append([sint2, sint1])
                                if float(linha[2]) == 0.5:
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes1:
                                        dictRegraCausas[nomeCausa].sintYes1.append(sint2)
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot1:
                                        dictRegraCausas[nomeCausa].sintNot1.append(sint1)
                                elif float(linha[2]) == 0.3:
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes2:
                                        dictRegraCausas[nomeCausa].sintYes2.append(sint2)
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot2:
                                        dictRegraCausas[nomeCausa].sintNot2.append(sint1)
                                elif float(linha[2]) == 0.5:
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes3:
                                        dictRegraCausas[nomeCausa].sintYes3.append(sint2)
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot3:
                                        dictRegraCausas[nomeCausa].sintNot3.append(sint1)
                            # Y(N;N)
                            else:
                                dictRegraCausas[nomeCausa].NN.append([sint1, sint2])
                                if float(linha[2]) == 0.5:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot1:
                                        dictRegraCausas[nomeCausa].sintNot1.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot1:
                                        dictRegraCausas[nomeCausa].sintNot1.append(sint2)
                                elif float(linha[2]) == 0.3:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot2:
                                        dictRegraCausas[nomeCausa].sintNot2.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot2:
                                        dictRegraCausas[nomeCausa].sintNot2.append(sint2)
                                elif float(linha[2]) == 0.15:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot3:
                                        dictRegraCausas[nomeCausa].sintNot3.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot3:
                                        dictRegraCausas[nomeCausa].sintNot3.append(sint2)
                    # N(?;?)
                    else:
                        # N(Y;?)
                        if isNOTsint1 == False:
                            # N(Y;Y)
                            if isNOTsint2 == False:
                                dictRegraCausas[nomeCausa].NN.append([sint1, sint2])
                                if float(linha[2]) == 0.5:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot1:
                                        dictRegraCausas[nomeCausa].sintNot1.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot1:
                                        dictRegraCausas[nomeCausa].sintNot1.append(sint2)
                                elif float(linha[2]) == 0.3:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot2:
                                        dictRegraCausas[nomeCausa].sintNot2.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot2:
                                        dictRegraCausas[nomeCausa].sintNot2.append(sint2)
                                elif float(linha[2]) == 0.15:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot3:
                                        dictRegraCausas[nomeCausa].sintNot3.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot3:
                                        dictRegraCausas[nomeCausa].sintNot3.append(sint2)
                            # N(Y;N)
                            else:
                                dictRegraCausas[nomeCausa].YN.append([sint2, sint1])
                                if float(linha[2]) == 0.5:
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes1:
                                        dictRegraCausas[nomeCausa].sintYes1.append(sint2)
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot1:
                                        dictRegraCausas[nomeCausa].sintNot1.append(sint1)
                                elif float(linha[2]) == 0.3:
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes2:
                                        dictRegraCausas[nomeCausa].sintYes2.append(sint2)
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot2:
                                        dictRegraCausas[nomeCausa].sintNot2.append(sint1)
                                elif float(linha[2]) == 0.15:
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes3:
                                        dictRegraCausas[nomeCausa].sintYes3.append(sint2)
                                    if sint1 not in dictRegraCausas[nomeCausa].sintNot3:
                                        dictRegraCausas[nomeCausa].sintNot3.append(sint1)
                        # N(N;?)
                        else:
                            # N(N;Y)
                            if isNOTsint2 == False:
                                dictRegraCausas[nomeCausa].YN.append([sint1, sint2])
                                if float(linha[2]) == 0.5:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes1:
                                        dictRegraCausas[nomeCausa].sintYes1.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot1:
                                        dictRegraCausas[nomeCausa].sintNot1.append(sint2)
                                elif float(linha[2]) == 0.3:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes2:
                                        dictRegraCausas[nomeCausa].sintYes2.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot2:
                                        dictRegraCausas[nomeCausa].sintNot2.append(sint2)
                                elif float(linha[2]) == 0.15:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes3:
                                        dictRegraCausas[nomeCausa].sintYes3.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintNot3:
                                        dictRegraCausas[nomeCausa].sintNot3.append(sint2)
                            # N(N;N)
                            else:
                                dictRegraCausas[nomeCausa].YY.append([sint1, sint2])
                                if float(linha[2]) == 0.5:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes1:
                                        dictRegraCausas[nomeCausa].sintYes1.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes1:
                                        dictRegraCausas[nomeCausa].sintYes1.append(sint2)
                                elif float(linha[2]) == 0.3:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes2:
                                        dictRegraCausas[nomeCausa].sintYes2.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes2:
                                        dictRegraCausas[nomeCausa].sintYes2.append(sint2)
                                elif float(linha[2]) == 0.15:
                                    if sint1 not in dictRegraCausas[nomeCausa].sintYes3:
                                        dictRegraCausas[nomeCausa].sintYes3.append(sint1)
                                    if sint2 not in dictRegraCausas[nomeCausa].sintYes3:
                                        dictRegraCausas[nomeCausa].sintYes3.append(sint2)
                    # SINTOMAS
                    # Y(?;?)
                    if isNOT == False:
                        # Y(Y;?)
                        if isNOTsint1 == False:
                            # Y(Y;Y)
                            if isNOTsint2 == False:
                                if sint1 not in dictRegraSintomas[sint2].sintYes:
                                    dictRegraSintomas[sint2].sintYes.append(sint1)
                                if sint2 not in dictRegraSintomas[sint1].sintYes:
                                    dictRegraSintomas[sint1].sintYes.append(sint2)
                            # Y(Y;N)
                            else:
                                if sint1 not in dictRegraSintomas[sint2].sintNot:
                                    dictRegraSintomas[sint2].sintNot.append(sint1)
                                if sint2 not in dictRegraSintomas[sint1].sintNot:
                                    dictRegraSintomas[sint1].sintNot.append(sint2)
                        # Y(N;?)
                        else:
                            # Y(N;Y)
                            if isNOTsint2 == False:
                                if sint1 not in dictRegraSintomas[sint2].sintNot:
                                    dictRegraSintomas[sint2].sintNot.append(sint1)
                                if sint2 not in dictRegraSintomas[sint1].sintNot:
                                    dictRegraSintomas[sint1].sintNot.append(sint2)
                            # Y(N;N)
                            else:
                                if sint1 not in dictRegraSintomas[sint2].sintYes:
                                    dictRegraSintomas[sint2].sintYes.append(sint1)
                                if sint2 not in dictRegraSintomas[sint1].sintYes:
                                    dictRegraSintomas[sint1].sintYes.append(sint2)
                    # N(?;?)
                    else:
                        # N(Y;?)
                        if isNOTsint1 == False:
                            # N(Y;Y)
                            if isNOTsint2 == False:
                                if sint1 not in dictRegraSintomas[sint2].sintYes:
                                    dictRegraSintomas[sint2].sintYes.append(sint1)
                                if sint2 not in dictRegraSintomas[sint1].sintYes:
                                    dictRegraSintomas[sint1].sintYes.append(sint2)
                            # N(Y;N)
                            else:
                                if sint1 not in dictRegraSintomas[sint2].sintNot:
                                    dictRegraSintomas[sint2].sintNot.append(sint1)
                                if sint2 not in dictRegraSintomas[sint1].sintNot:
                                    dictRegraSintomas[sint1].sintNot.append(sint2)
                        # N(N;?)
                        else:
                            # N(N;Y)
                            if isNOTsint2 == False:
                                if sint1 not in dictRegraSintomas[sint2].sintNot:
                                    dictRegraSintomas[sint2].sintNot.append(sint1)
                                if sint2 not in dictRegraSintomas[sint1].sintNot:
                                    dictRegraSintomas[sint1].sintNot.append(sint2)
                            # N(N;N)
                            else:
                                if sint1 not in dictRegraSintomas[sint2].sintYes:
                                    dictRegraSintomas[sint2].sintYes.append(sint1)
                                if sint2 not in dictRegraSintomas[sint1].sintYes:
                                    dictRegraSintomas[sint1].sintYes.append(sint2)

    for item in dictRegraCausas:
            newCausa = {
                "causa": dictRegraCausas[item].causa,
                "YY": dictRegraCausas[item].YY,
                "YN": dictRegraCausas[item].YN,
                "NN": dictRegraCausas[item].NN,
                "sintYes1": dictRegraCausas[item].sintYes1,
                "sintYes2": dictRegraCausas[item].sintYes2,
                "sintYes3": dictRegraCausas[item].sintYes3,
                "sintNot1": dictRegraCausas[item].sintNot1,
                "sintNot2": dictRegraCausas[item].sintNot2,
                "sintNot3": dictRegraCausas[item].sintNot3,
                "prob": dictRegraCausas[item].prob
            }
            body = json.dumps(newCausa)
            body1 = json.loads(body)
            projetoPAA.reference("/Regras/Causas").push(body1)
    for item in dictRegraSintomas:
            newSint = {
                "sintoma": dictRegraSintomas[item].sintoma,
                "sintYes": dictRegraSintomas[item].sintYes,
                "sintNot": dictRegraSintomas[item].sintNot,
                "ocorrencias": dictRegraSintomas[item].ocorrencias
            }
            body = json.dumps(newSint)
            body1 = json.loads(body)
            projetoPAA.reference("/Regras/Sintomas").push(body1)
    return "Sucesso"


@app.post("/Regras/Arvore/CriarArvore")
async def cria_Arvore():
    """
    Cria a Arvore
    :return:
    """
    sints = projetoPAA.reference("/Regras/Sintomas").get()
    listSint = []

    for item in sints:
        listSint.append(sints[item]["sintoma"])

    root = Node('Origem')
    for i in listSint:
        branch = Node(i, parent=root)


    body = ['Origem',retornaListaFilhos(root)]
    projetoPAA.reference("/Regras/Arvore").push(body)
    return body


@app.post("/Regras/Questionario/post-resposta")
async def post_Resposta(resposta: texto):
    """
    Retorna um resultado ou 'Continua'.
    Se retornar 'Continua', faca outro get pergunta.
    :param resposta:
    :return:
    """
    rota = projetoPAA.reference("/Regras/Rota").get()
    for it in rota:
        rota = rota[it]
        break
    res = resposta.txt
    rota.append(res)
    sints = projetoPAA.reference("/Regras/Sintomas").get()
    caus = projetoPAA.reference("/Regras/Causas").get()
    listSintWithCausas = []
    listSint = []
    listCausas = []
    dictRegraCausas = {}
    dictRegraSintomas = {}
    for item in sints:
        listSint.append(sints[item]["sintoma"])
        dictRegraSintomas[sints[item]["sintoma"]] = RegraSintoma()
        dictRegraSintomas[sints[item]["sintoma"]].sintoma = sints[item]["sintoma"]
        if "sintYes" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].sintYes = sints[item]["sintYes"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].sintYes = []
        if "sintNot" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].sintNot = sints[item]["sintNot"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].sintNot = []
        if "ocorrencias" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].ocorrencias = sints[item]["ocorrencias"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].ocorrencias = 0

    for item in caus:
        listCausas.append(caus[item]["causa"])
        dictRegraCausas[caus[item]["causa"]] = RegraCausa()
        dictRegraCausas[caus[item]["causa"]].causa = caus[item]["causa"]
        if "YY" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].YY = caus[item]["YY"]
        else:
            dictRegraCausas[caus[item]["causa"]].YY = []
        if "YN" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].YN = caus[item]["YN"]
        else:
            dictRegraCausas[caus[item]["causa"]].YN = []
        if "NN" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].NN = caus[item]["NN"]
        else:
            dictRegraCausas[caus[item]["causa"]].NN = []
        if "sintYes1" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].sintYes1 = caus[item]["sintYes1"]
        else:
            dictRegraCausas[caus[item]["causa"]].sintYes1 = []
        if "sintYes2" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].sintYes2 = caus[item]["sintYes2"]
        else:
            dictRegraCausas[caus[item]["causa"]].sintYes2 = []
        if "sintYes3" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].sintYes3 = caus[item]["sintYes3"]
        else:
            dictRegraCausas[caus[item]["causa"]].sintYes3 = []
        if "sintNot1" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].sintNot1 = caus[item]["sintNot1"]
        else:
            dictRegraCausas[caus[item]["causa"]].sintNot1 = []
        if "sintNot2" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].sintNot2 = caus[item]["sintNot2"]
        else:
            dictRegraCausas[caus[item]["causa"]].sintNot2 = []
        if "sintNot3" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].sintNot3 = caus[item]["sintNot3"]
        else:
            dictRegraCausas[caus[item]["causa"]].sintNot3 = []
    negs = []
    afirms = []
    z = 0
    while z < len(rota):
        if rota[z+1] == 'Sim':
            afirms.append(rota[z])
        elif rota[z+1] == 'Nao':
            negs.append(rota[z])
        z+=2
    resultado = probabilidades(afirms,negs,dictRegraCausas)
    if resultado == 0:
        if len(listSint) > len(rota)/2:
            projetoPAA.reference("/Regras/Rota").delete()
            projetoPAA.reference("/Regras/Rota").push(rota)
            return "Continua"
        else:
            projetoPAA.reference("/Regras/Rota").delete()
            return "Respostas Inconclusivas."
    else:
        projetoPAA.reference("/Regras/Rota").delete()
        return "Você poderia tentar "+resultado+'.'

@app.delete("/Regras/Questionario")
async def deleta_Questionario():
    """
    Deleta todas as rotas.
    :return:
    """
    projetoPAA.reference("/Regras/Rota").delete()
    return "Deletado"

@app.delete("/Regras/Arvore")
async def delete_Arvore():
    """
    Deleta a Arvore
    :return:
    """
    projetoPAA.reference("/Regras/Arvore").delete()
    return "Deletado"

