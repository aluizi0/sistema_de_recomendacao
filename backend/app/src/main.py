import json
from fastapi import FastAPI
from fastapi import APIRouter
from config_db import projetoPAA
from fastapi.middleware.cors import CORSMiddleware
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


def criaFilho1(pai = Node, nome = str, dictRegras = dict):
    # Cria um no
    branch = Node(nome, parent=pai)
    # Chama a funcao criafilho2
    criaFilho2(branch, nome, dictRegras)

def criaFilho2(pai = Node, nome = str, dictRegras = dict):
    # Cria uma folha com a causa
    # Caso nao haja causa para a combinacao de sintomas cria uma folha com Goback
    nomePai = pai.parent.name
    nome = pai.name
    dictRegraCausas = dictRegras
    istrue = False
    for item in dictRegraCausas:
        if [nomePai, nome] in dictRegraCausas[item].YY or [nome, nomePai] in dictRegraCausas[item].YY:
            istrue = True
            branch = Node(dictRegraCausas[item].causa, parent= pai)
        elif [nomePai, nome] in dictRegraCausas[item].YN or [nome, nomePai] in dictRegraCausas[item].YN:
            istrue = True
            branch = Node(dictRegraCausas[item].causa, parent=pai)
        elif [nomePai, nome] in dictRegraCausas[item].NN or [nome, nomePai] in dictRegraCausas[item].NN:
            istrue = True
            branch = Node(dictRegraCausas[item].causa, parent=pai)
    if istrue == False:
        branch = Node("GoBack "+nomePai+' '+nome, parent= pai)

def retornaListaFilhos(branch=Node):
    children = []
    if branch.is_leaf == False:
        for child in branch.children:
            if child.is_leaf == False:
                children.append([child.name, [retornaListaFilhos(child)]])
            else:
                children.append(child.name)
    else:
        children = branch.name
    return children


class RegraCausa:
        causa: str  # Nome da causa
        YY: list  # Lista de tuplas
        probYY: list  # Cada item representa a probabilidade da tupla YY de mesmo indice
        YN: list  # Lista de tuplas
        probYN: list  # Cada item representa a probabilidade da tupla YN de mesmo indice
        NN: list  # Lista de tuplas
        probNN: list  # Cada item representa a probabilidade da tupla NN de mesmo indice
        sintYes: list  # Lista de sintomas que ao serem verdadeiros aumentam chance da causa
        sintNot: list  # Lista de sintomas que ao serem falsos aumentam chance da causa


class RegraSintoma:
        sintoma: str  # Nome do sintoma
        YY: list  # Lista de tuplas
        probYY: list  # Cada item representa a probabilidade da tupla YY de mesmo indice
        YN: list  # Lista de tuplas
        probYN: list  # Cada item representa a probabilidade da tupla YN de mesmo indice
        NN: list  # Lista de tuplas
        probNN: list  # Cada item representa a probabilidade da tupla NN de mesmo indice
        sintYes: list  # Lista de sintomas que ao serem verdadeiros aumentam chance da causa
        sintNot: list  # Lista de sintomas que ao serem falsos aumentam chance da causa
        ocorrencias: int



@app.get("/Regras")
async def getRegras():
    regras = projetoPAA.reference("/Regras").get()
    body = json.dumps(regras)
    projetoPAA.reference("/Regras").push(body)
    return regras




#           CREATE
@app.post("/primeiraRS")
async def primeiraRS():
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
                        dictRegraCausas[nomeCausa].probYY = []
                        dictRegraCausas[nomeCausa].probYN = []
                        dictRegraCausas[nomeCausa].probNN = []
                        dictRegraCausas[nomeCausa].sintYes = []
                        dictRegraCausas[nomeCausa].sintNot = []

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

                    # Analisa os dois sintomas e guarda no dict
                    # formato ?(?;?) cada interrogacao lida com um possivel NOT
                    # Y(?;?)
                    if isNOT == False:
                        # Y(Y;?)
                        if isNOTsint1 == False:
                            # Y(Y;Y)
                            if isNOTsint2 == False:
                                dictRegraCausas[nomeCausa].YY.append([sint1,sint2])
                                dictRegraCausas[nomeCausa].probYY.append(float(linha[2]))
                                dictRegraCausas[nomeCausa].sintYes.append(sint1)
                                dictRegraCausas[nomeCausa].sintYes.append(sint2)
                            # Y(Y;N)
                            else:
                                dictRegraCausas[nomeCausa].YN.append([sint1,sint2])
                                dictRegraCausas[nomeCausa].probYN.append(float(linha[2]))
                                dictRegraCausas[nomeCausa].sintYes.append(sint1)
                                dictRegraCausas[nomeCausa].sintNot.append(sint2)
                        # Y(N;?)
                        else:
                            # Y(N;Y)
                            if isNOTsint2 == False:
                                dictRegraCausas[nomeCausa].YN.append([sint2,sint1])
                                dictRegraCausas[nomeCausa].probYN.append(float(linha[2]))
                                dictRegraCausas[nomeCausa].sintYes.append(sint2)
                                dictRegraCausas[nomeCausa].sintNot.append(sint1)
                            # Y(N;N)
                            else:
                                dictRegraCausas[nomeCausa].NN.append([sint1,sint2])
                                dictRegraCausas[nomeCausa].probNN.append(float(linha[2]))
                                dictRegraCausas[nomeCausa].sintNot.append(sint1)
                                dictRegraCausas[nomeCausa].sintNot.append(sint2)
                    # N(?;?)
                    else:
                        # N(Y;?)
                        if isNOTsint1 == False:
                            # N(Y;Y)
                            if isNOTsint2 == False:
                                dictRegraCausas[nomeCausa].NN.append([sint1,sint2])
                                dictRegraCausas[nomeCausa].probNN.append(float(linha[2]))
                                dictRegraCausas[nomeCausa].sintNot.append(sint1)
                                dictRegraCausas[nomeCausa].sintNot.append(sint2)
                            # N(Y;N)
                            else:
                                dictRegraCausas[nomeCausa].YN.append([sint2,sint1])
                                dictRegraCausas[nomeCausa].probYN.append(float(linha[2]))
                                dictRegraCausas[nomeCausa].sintYes.append(sint2)
                                dictRegraCausas[nomeCausa].sintNot.append(sint1)
                        # N(N;?)
                        else:
                            # N(N;Y)
                            if isNOTsint2 == False:
                                dictRegraCausas[nomeCausa].YN.append([sint1,sint2])
                                dictRegraCausas[nomeCausa].probYN.append(float(linha[2]))
                                dictRegraCausas[nomeCausa].sintYes.append(sint1)
                                dictRegraCausas[nomeCausa].sintNot.append(sint2)
                            # N(N;N)
                            else:
                                dictRegraCausas[nomeCausa].YY.append([sint1,sint2])
                                dictRegraCausas[nomeCausa].probYY.append(float(linha[2]))
                                dictRegraCausas[nomeCausa].sintYes.append(sint1)
                                dictRegraCausas[nomeCausa].sintYes.append(sint2)

                    if sint1 not in dictRegraSintomas:
                        dictRegraSintomas[sint1] = RegraSintoma()
                        dictRegraSintomas[sint1].sintoma = sint1
                        dictRegraSintomas[sint1].YY = []
                        dictRegraSintomas[sint1].YN = []
                        dictRegraSintomas[sint1].NN = []
                        dictRegraSintomas[sint1].probYY = []
                        dictRegraSintomas[sint1].probYN = []
                        dictRegraSintomas[sint1].probNN = []
                        dictRegraSintomas[sint1].sintYes = []
                        dictRegraSintomas[sint1].sintNot = []
                        dictRegraSintomas[sint1].ocorrencias = 1
                    else:
                        dictRegraSintomas[sint1].ocorrencias +=1

                    if sint2 not in dictRegraSintomas:
                        dictRegraSintomas[sint2] = RegraSintoma()
                        dictRegraSintomas[sint2].sintoma = sint2
                        dictRegraSintomas[sint2].YY = []
                        dictRegraSintomas[sint2].YN = []
                        dictRegraSintomas[sint2].NN = []
                        dictRegraSintomas[sint2].probYY = []
                        dictRegraSintomas[sint2].probYN = []
                        dictRegraSintomas[sint2].probNN = []
                        dictRegraSintomas[sint2].sintYes = []
                        dictRegraSintomas[sint2].sintNot = []
                        dictRegraSintomas[sint2].ocorrencias = 1
                    else:
                        dictRegraSintomas[sint2].ocorrencias +=1
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
                "probYY": dictRegraCausas[item].probYY,
                "probYN": dictRegraCausas[item].probYN,
                "probNN": dictRegraCausas[item].probNN,
                "sintYes": dictRegraCausas[item].sintYes,
                "sintNot": dictRegraCausas[item].sintNot
            }
            body = json.dumps(newCausa)
            body1 = json.loads(body)
            projetoPAA.reference("/Regras/Causas").push(body1)
    for item in dictRegraSintomas:
            newSint = {
                "sintoma": dictRegraSintomas[item].sintoma,
                "YY": dictRegraSintomas[item].YY,
                "YN": dictRegraSintomas[item].YN,
                "NN": dictRegraSintomas[item].NN,
                "probYY": dictRegraSintomas[item].probYY,
                "probYN": dictRegraSintomas[item].probYN,
                "probNN": dictRegraSintomas[item].probNN,
                "sintYes": dictRegraSintomas[item].sintYes,
                "sintNot": dictRegraSintomas[item].sintNot,
                "ocorrencias": dictRegraSintomas[item].ocorrencias
            }
            body = json.dumps(newSint)
            body1 = json.loads(body)
            projetoPAA.reference("/Regras/Sintomas").push(body1)


@app.get("/Regras/Arvore")
async def makeTree():
    sints = projetoPAA.reference("/Regras/Sintomas").get()
    caus = projetoPAA.reference("/Regras/Causas").get()
    root = Node("Origem")
    listSintWithCausas = []
    listSint = []
    listCausas = []
    dictRegraCausas = {}
    dictRegraSintomas = {}
    for item in sints:
        listSint.append(sints[item]["sintoma"])
        dictRegraSintomas[sints[item]["sintoma"]] = RegraSintoma()
        dictRegraSintomas[sints[item]["sintoma"]].sintoma = sints[item]["sintoma"]
        if "YY" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].YY = sints[item]["YY"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].YY = []
        if "YN" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].YN = sints[item]["YN"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].YN = []
        if "NN" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].NN = sints[item]["NN"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].NN = []
        if "probYY" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].probYY = sints[item]["probYY"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].probYY = []
        if "probYN" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].probYN = sints[item]["probYN"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].probYN = []
        if "probNN" in sints[item]:
            dictRegraSintomas[sints[item]["sintoma"]].probNN = sints[item]["probNN"]
        else:
            dictRegraSintomas[sints[item]["sintoma"]].probNN = []
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
        if "probYY" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].probYY = caus[item]["probYY"]
        else:
            dictRegraCausas[caus[item]["causa"]].probYY = []
        if "probYN" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].probYN = caus[item]["probYN"]
        else:
            dictRegraCausas[caus[item]["causa"]].probYN = []
        if "probNN" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].probNN = caus[item]["probNN"]
        else:
            dictRegraCausas[caus[item]["causa"]].probNN = []
        if "sintYes" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].sintYes = caus[item]["sintYes"]
        else:
            dictRegraCausas[caus[item]["causa"]].sintYes = []
        if "sintNot" in caus[item]:
            dictRegraCausas[caus[item]["causa"]].sintNot = caus[item]["sintNot"]
        else:
            dictRegraCausas[caus[item]["causa"]].sintNot = []


    for item in dictRegraCausas:
        for elem in dictRegraCausas[item].sintYes:
            if elem not in listSintWithCausas:
                listSintWithCausas.append(elem)
        for xis in dictRegraCausas[item].sintNot:
            if xis not in listSintWithCausas:
                listSintWithCausas.append(elem)

    for sint in listSintWithCausas:
        branch = Node(sint, parent= root)
        aux = []
        for xus in dictRegraSintomas[sint].sintYes:
            if xus not in aux:
                aux.append(xus)
        for it in aux:
            dictRegras = dictRegraCausas
            criaFilho1(branch, it, dictRegras)

    # Criar arvore como lista
    arvore = retornaListaFilhos(root)

    projetoPAA.reference("/Regras/Arvore").push(arvore)
    return arvore
