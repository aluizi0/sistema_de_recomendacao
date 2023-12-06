from anytree import Node, RenderTree


f = open("regras.txt", "r")

# Criacao de classes
class RegraCausa:
    causa = str  # Nome da causa
    YY = list  # Lista de tuplas
    probYY = list  # Cada item representa a probabilidade da tupla YY de mesmo indice
    YN = list  # Lista de tuplas
    probYN = list  # Cada item representa a probabilidade da tupla YN de mesmo indice
    NN = list  # Lista de tuplas
    probNN = list  # Cada item representa a probabilidade da tupla NN de mesmo indice
    sintYes = list  # Lista de sintomas que ao serem verdadeiros aumentam chance da causa
    sintNot = list  # Lista de sintomas que ao serem falsos aumentam chance da causa

class RegraSintoma:
    sintoma = str  # Nome do sintoma
    YY = list  # Lista de tuplas
    probYY = list  # Cada item representa a probabilidade da tupla YY de mesmo indice
    YN = list  # Lista de tuplas
    probYN = list  # Cada item representa a probabilidade da tupla YN de mesmo indice
    NN = list  # Lista de tuplas
    probNN = list  # Cada item representa a probabilidade da tupla NN de mesmo indice
    sintYes = list  # Lista de sintomas que ao serem verdadeiros aumentam chance da causa
    sintNot = list  # Lista de sintomas que ao serem falsos aumentam chance da causa
    ocorrencias = int



def criaFilho1(pai = Node, nome = str):
    # Cria um no
    branch = Node(nome, parent=pai)
    # Chama a funcao criafilho2
    criaFilho2(branch, nome)

def criaFilho2(pai = Node, nome = str):
    # Cria uma folha com a causa
    # Caso nao haja causa para a combinacao de sintomas cria uma folha com Goback
    nomePai = pai.parent.name
    nome = pai.name
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



# Declara dicts
dictRegraCausas = {}
dictRegraSintomas = {}

# Declara listas
listCausas = []
listCausasUsadas = []

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
                        dictRegraSintomas[nomeSintoma].sintYes.append(sint1)
                        dictRegraSintomas[nomeSintoma].sintYes.append(sint2)
                    # Y(Y;N)
                    else:
                        dictRegraSintomas[nomeSintoma].YN.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probYN.append(float(linha[2]))
                        dictRegraSintomas[nomeSintoma].sintYes.append(sint1)
                        dictRegraSintomas[nomeSintoma].sintNot.append(sint2)
                # Y(N;?)
                else:
                    # Y(N;Y)
                    if isNOTsint2 == False:
                        dictRegraSintomas[nomeSintoma].YN.append([sint2, sint1])
                        dictRegraSintomas[nomeSintoma].probYN.append(float(linha[2]))
                        dictRegraSintomas[nomeSintoma].sintYes.append(sint2)
                        dictRegraSintomas[nomeSintoma].sintNot.append(sint1)
                    # Y(N;N)
                    else:
                        dictRegraSintomas[nomeSintoma].NN.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probNN.append(float(linha[2]))
                        dictRegraSintomas[nomeSintoma].sintNot.append(sint1)
                        dictRegraSintomas[nomeSintoma].sintNot.append(sint2)
            # N(?;?)
            else:
                # N(Y;?)
                if isNOTsint1 == False:
                    # N(Y;Y)
                    if isNOTsint2 == False:
                        dictRegraSintomas[nomeSintoma].NN.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probNN.append(float(linha[2]))
                        dictRegraSintomas[nomeSintoma].sintNot.append(sint1)
                        dictRegraSintomas[nomeSintoma].sintNot.append(sint2)
                    # N(Y;N)
                    else:
                        dictRegraSintomas[nomeSintoma].YN.append([sint2, sint1])
                        dictRegraSintomas[nomeSintoma].probYN.append(float(linha[2]))
                        dictRegraSintomas[nomeSintoma].sintYes.append(sint2)
                        dictRegraSintomas[nomeSintoma].sintNot.append(sint1)
                # N(N;?)
                else:
                    # N(N;Y)
                    if isNOTsint2 == False:
                        dictRegraSintomas[nomeSintoma].YN.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probYN.append(float(linha[2]))
                        dictRegraSintomas[nomeSintoma].sintYes.append(sint1)
                        dictRegraSintomas[nomeSintoma].sintNot.append(sint2)
                    # N(N;N)
                    else:
                        dictRegraSintomas[nomeSintoma].YY.append([sint1, sint2])
                        dictRegraSintomas[nomeSintoma].probYY.append(float(linha[2]))
                        dictRegraSintomas[nomeSintoma].sintYes.append(sint1)
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


# Print de todas as regras que estao no dict
print("-----------CAUSAS----------")
for item in dictRegraCausas:
    print("-----", dictRegraCausas[item].causa, "-----")
    if len(dictRegraCausas[item].probYY) > 0:
        for y in range(len(dictRegraCausas[item].probYY)):
            print("YY", dictRegraCausas[item].YY[y], dictRegraCausas[item].probYY[y])
    if len(dictRegraCausas[item].probYN) > 0:
        for y in range(len(dictRegraCausas[item].probYN)):
            print("YN", dictRegraCausas[item].YN[y], dictRegraCausas[item].probYN[y])
    if len(dictRegraCausas[item].probNN) > 0:
        for y in range(len(dictRegraCausas[item].probNN)):
            print("NN", dictRegraCausas[item].NN[y], dictRegraCausas[item].probNN[y])
    if len(dictRegraCausas[item].sintYes) > 0:
        print("SintYes", dictRegraCausas[item].sintYes)
    if len(dictRegraCausas[item].sintNot) > 0:
        print("SintNot", dictRegraCausas[item].sintNot)
    print("--------------------")
print("")
print("-----------SINTOMAS----------")
for item in dictRegraSintomas:
    print("-----", dictRegraSintomas[item].sintoma, "-----")
    if len(dictRegraSintomas[item].probYY) > 0:
        for y in range(len(dictRegraSintomas[item].probYY)):
            print("YY", dictRegraSintomas[item].YY[y], dictRegraSintomas[item].probYY[y])
    if len(dictRegraSintomas[item].probYN) > 0:
        for y in range(len(dictRegraSintomas[item].probYN)):
            print("YN", dictRegraSintomas[item].YN[y], dictRegraSintomas[item].probYN[y])
    if len(dictRegraSintomas[item].probNN) > 0:
        for y in range(len(dictRegraSintomas[item].probNN)):
            print("NN", dictRegraSintomas[item].NN[y], dictRegraSintomas[item].probNN[y])
    if len(dictRegraSintomas[item].sintYes) > 0:
        print("SintYes", dictRegraSintomas[item].sintYes)
    if len(dictRegraSintomas[item].sintNot) > 0:
        print("SintNot", dictRegraSintomas[item].sintNot)
    print("Ocorrencias", dictRegraSintomas[item].ocorrencias)
print("---------------------")


# Arvore

root = Node("Origem")
listSintWithCausas = []
listSint = []

for xesque in dictRegraSintomas:
    if dictRegraSintomas[xesque].sintoma not in listSint:
        listSint.append(xesque)

for item in dictRegraCausas:
    for elem in dictRegraCausas[item].sintYes:
        if elem not in listSintWithCausas:
            listSintWithCausas.append(elem)
    for xis in dictRegraCausas[item].sintNot:
        if xis not in listSintWithCausas:
            listSintWithCausas.append(elem)

for sint in listSintWithCausas:
    branch = Node(sint, parent= root)
    for xus in dictRegraSintomas[sint].sintYes:
        criaFilho1(branch,xus)
    for xes in dictRegraSintomas[sint].sintNot:
        criaFilho1(branch,xes)


for pre, fill, node in RenderTree(root):
    print("%s%s" % (pre, node.name))