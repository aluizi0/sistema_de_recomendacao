import json
from typing import Optional
from fastapi import APIRouter
from config_db import projetoPAA
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from models.regras_model import ModelRegraSintoma, ModelRegra, ModelRegraCausa


router = APIRouter(
    prefix="/Regras",
    tags=["Regras"],
    responses={404: {"description": "Not Found"}}
)

#           CREATE

@router.post("/add-regra/")
async def add_regra(regra: ModelRegra):
    causas = projetoPAA.reference("/Regras/Causas").get()
    sintomas = projetoPAA.reference("/Regras/Sintomas").get()
    # Corta a string x e guarda na variavel linha
    linha = regra.split(',')
    if len(linha) > 1:  # Se o tamanho da variavel for maior que 1
        if linha[0][1] == 'C':  # Se eh uma causa
            nomeCausa = linha[0][3:-1]  # Salva nome da causa
            if nomeCausa not in causas.items():  # Se a causa nao existe cria ela
                novaCausa = ModelRegraCausa()
                novaCausa.causa = nomeCausa
                novaCausa.YY = []
                novaCausa.YN = []
                novaCausa.NN = []
                novaCausa.probYY = []
                novaCausa.probYN = []
                novaCausa.probNN = []
                novaCausa.sintYes = []
                novaCausa.sintNot = []

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
                        novaCausa.YY.append([sint1, sint2])
                        novaCausa.probYY.append(float(linha[2]))
                    # Y(Y;N)
                    else:
                        novaCausa.YN.append([sint1, sint2])
                        novaCausa.probYN.append(float(linha[2]))
                # Y(N;?)
                else:
                    # Y(N;Y)
                    if isNOTsint2 == False:
                        novaCausa.YN.append([sint2, sint1])
                        novaCausa.probYN.append(float(linha[2]))
                    # Y(N;N)
                    else:
                        novaCausa.NN.append([sint1, sint2])
                        novaCausa.probNN.append(float(linha[2]))
            # N(?;?)
            else:
                # N(Y;?)
                if isNOTsint1 == False:
                    # N(Y;Y)
                    if isNOTsint2 == False:
                        novaCausa.NN.append([sint1, sint2])
                        novaCausa.probNN.append(float(linha[2]))
                    # N(Y;N)
                    else:
                        novaCausa.YN.append([sint2, sint1])
                        novaCausa.probYN.append(float(linha[2]))
                # N(N;?)
                else:
                    # N(N;Y)
                    if isNOTsint2 == False:
                        novaCausa.YN.append([sint1, sint2])
                        novaCausa.probYN.append(float(linha[2]))
                    # N(N;N)
                    else:
                        novaCausa.YY.append([sint1, sint2])
                        novaCausa.probYY.append(float(linha[2]))

            if sint1 not in sintomas.items():
                newSint = ModelRegraSintoma()
                newSint.sintoma = sint1
                newSint.YY = []
                newSint.YN = []
                newSint.NN = []
                newSint.probYY = []
                newSint.probYN = []
                newSint.probNN = []
                newSint.sintYes = []
                newSint.sintNot = []
                newSint.ocorrencias = 1
                body = json.loads(newSint.json())
                projetoPAA.reference("/Regras/Sintomas").push(body)
            else:
                dictRegraSintomas[sint1].ocorrencias += 1

            if sint2 not in sintomas.items:
                newSint = ModelRegraSintoma()
                newSint.sintoma = sint2
                newSint.YY = []
                newSint.YN = []
                newSint.NN = []
                newSint.probYY = []
                newSint.probYN = []
                newSint.probNN = []
                newSint.sintYes = []
                newSint.sintNot = []
                newSint.ocorrencias = 1
                body = json.loads(newSint.json())
                projetoPAA.reference("/Regras/Sintomas").push(body)
            else:
                dictRegraSintomas[sint2].ocorrencias += 1

            """
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


        # Caso seja sintoma
        # Mesma logica da Causa acima
        elif linha[0][1] == 'S':
            nomeSintoma = linha[0][3:-1]
            if nomeSintoma not in dictRegraSintomas:
                dictRegraSintomas[nomeSintoma] = RegraSintoma()
                dictRegraSintomas[nomeSintoma].sintoma = nomeSintoma
                dictRegraSintomas[nomeSintoma].YY = []
                dictRegraSintomas[nomeSintoma].YN = []
                dictRegraSintomas[nomeSintoma].NN = []
                dictRegraSintomas[nomeSintoma].probYY = []
                dictRegraSintomas[nomeSintoma].probYN = []
                dictRegraSintomas[nomeSintoma].probNN = []
                dictRegraSintomas[nomeSintoma].sintYes = []
                dictRegraSintomas[nomeSintoma].sintNot = []
                dictRegraSintomas[nomeSintoma].ocorrencias = 0

            sintomas = linha[1].split(';')
            isNOT = False

            if sintomas[0][0:3] == "NOT":
                isNOT = True
                sintomas[0] = sintomas[0][3:]

            sint1 = ''
            sint2 = ''
            isNOTsint1 = False
            isNOTsint2 = False

            if sintomas[0][1:4] == "NOT":
                sint1 = sintomas[0][7:-1]
                isNOTsint1 = True
            else:
                sint1 = sintomas[0][4:-1]

            if sintomas[1][0:3] == "NOT":
                sint2 = sintomas[1][6:-2]
                isNOTsint2 = True
            else:
                sint2 = sintomas[1][3:-2]

            # Y(?;?)
            if isNOT == False:
                # Y(Y;?)
                if isNOTsint1 == False:
                    # Y(Y;Y)
                    if isNOTsint2 == False:
                        dictRegraSintomas[nomeSintoma].YY.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probYY.append(float(linha[2]))
                        if sint1 not in dictRegraSintomas[nomeSintoma].sintYes:
                            dictRegraSintomas[nomeSintoma].sintYes.append(sint1)
                        if sint2 not in dictRegraSintomas[nomeSintoma].sintYes:
                            dictRegraSintomas[nomeSintoma].sintYes.append(sint2)
                    # Y(Y;N)
                    else:
                        dictRegraSintomas[nomeSintoma].YN.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probYN.append(float(linha[2]))
                        if sint1 not in dictRegraSintomas[nomeSintoma].sintYes:
                            dictRegraSintomas[nomeSintoma].sintYes.append(sint1)
                        if sint2 not in dictRegraSintomas[nomeSintoma].sintNot:
                            dictRegraSintomas[nomeSintoma].sintNot.append(sint2)
                # Y(N;?)
                else:
                    # Y(N;Y)
                    if isNOTsint2 == False:
                        dictRegraSintomas[nomeSintoma].YN.append([sint2, sint1])
                        dictRegraSintomas[nomeSintoma].probYN.append(float(linha[2]))
                        if sint2 not in dictRegraSintomas[nomeSintoma].sintYes:
                            dictRegraSintomas[nomeSintoma].sintYes.append(sint2)
                        if sint1 not in dictRegraSintomas[nomeSintoma].sintNot:
                            dictRegraSintomas[nomeSintoma].sintNot.append(sint1)
                    # Y(N;N)
                    else:
                        dictRegraSintomas[nomeSintoma].NN.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probNN.append(float(linha[2]))
                        if sint1 not in dictRegraSintomas[nomeSintoma].sintNot:
                            dictRegraSintomas[nomeSintoma].sintNot.append(sint1)
                        if sint2 not in dictRegraSintomas[nomeSintoma].sintNot:
                            dictRegraSintomas[nomeSintoma].sintNot.append(sint2)
            # N(?;?)
            else:
                # N(Y;?)
                if isNOTsint1 == False:
                    # N(Y;Y)
                    if isNOTsint2 == False:
                        dictRegraSintomas[nomeSintoma].NN.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probNN.append(float(linha[2]))
                        if sint1 not in dictRegraSintomas[nomeSintoma].sintNot:
                            dictRegraSintomas[nomeSintoma].sintNot.append(sint1)
                        if sint2 not in dictRegraSintomas[nomeSintoma].sintNot:
                            dictRegraSintomas[nomeSintoma].sintNot.append(sint2)
                    # N(Y;N)
                    else:
                        dictRegraSintomas[nomeSintoma].YN.append([sint2, sint1])
                        dictRegraSintomas[nomeSintoma].probYN.append(float(linha[2]))
                        if sint2 not in dictRegraSintomas[nomeSintoma].sintYes:
                            dictRegraSintomas[nomeSintoma].sintYes.append(sint2)
                        if sint1 not in dictRegraSintomas[nomeSintoma].sintNot:
                            dictRegraSintomas[nomeSintoma].sintNot.append(sint1)
                # N(N;?)
                else:
                    # N(N;Y)
                    if isNOTsint2 == False:
                        dictRegraSintomas[nomeSintoma].YN.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probYN.append(float(linha[2]))
                        if sint1 not in dictRegraSintomas[nomeSintoma].sintYes:
                            dictRegraSintomas[nomeSintoma].sintYes.append(sint1)
                        if sint2 not in dictRegraSintomas[nomeSintoma].sintNot:
                            dictRegraSintomas[nomeSintoma].sintNot.append(sint2)
                    # N(N;N)
                    else:
                        dictRegraSintomas[nomeSintoma].YY.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probYY.append(float(linha[2]))
                        if sint1 not in dictRegraSintomas[nomeSintoma].sintYes:
                            dictRegraSintomas[nomeSintoma].sintYes.append(sint1)
                        if sint2 not in dictRegraSintomas[nomeSintoma].sintYes:
                            dictRegraSintomas[nomeSintoma].sintYes.append(sint2)
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
                dictRegraSintomas[sint1].ocorrencias = 0

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
                dictRegraSintomas[sint2].ocorrencias = 0
        else:
            print("ERRO", linha)
"""