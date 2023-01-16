from poo import *
import pandas as pd

# READ WORKSHEET TABLE OF DATA ALTERATION
tabelaDeCriticas = pd.read_excel("Planilha de Críticas.xlsx", sheet_name='Dados', dtype=str, keep_default_na=False)

conta = ContaTiss()
for linha in tabelaDeCriticas.values:
    global numGuia,codProc,novoCodProc,codTabela,novoCodTabela,grauP,novoGrauP,codDespesa,novoCodDespesa,unidadeMedida,novoUnidadeMedida
    numGuia = linha[0]
    codProc = linha[1]
    novoCodProc = linha[2]
    codTabela = linha[3]
    novoCodTabela = linha[4]
    grauP = linha[5]
    novoGrauP = linha[6]
    codDespesa = linha[7]
    novoCodDespesa = linha[8]
    unidadeMedida = linha[9]
    novoUnidadeMedida = linha[10]

    for item in conta.guias:
        guia = Guia(item, codProc)

        print('----------- ' + guia.getNumeroGuia() + ' -----------')
        if Et.iselement(guia.getProcedimentosExecutados()):
            for procedimento in guia.getListaProcedimento():
                p = Procedimento(procedimento, guia)
                p.alteraCodigoProcedimento(codProc, novoCodProc)
                p.alteraGrauParticipacao()
                p.alteraCodigoTabela()
                p.alteraValorUnitario()

        if Et.iselement(guia.getOutrasDespesas()):
            for procedimento in guia.getListaDespesa():
                p = Procedimento(procedimento, guia)
                p.alteraCodigoProcedimento(codProc, novoCodProc)
                p.alteraCodigoTabela()
                p.alteraValorUnitario()

        else:
            print('nao existe outras despesas nessa conta')
