from poo import *
import pandas as pd

# READ WORKSHEET TABLE OF DATA ALTERATION
tabelaDeCriticas = pd.read_excel("Planilha de Críticas.xlsx", sheet_name='Dados', dtype=str, keep_default_na=False)

conta = ContaTiss()
tabela = TabelaDeCritica()
for linha in tabela.getTabelaDados():
    setLinhaAlteracaoDeDados(linha)

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
                p.alteraCodigoDespesa()
                p.alteraCodigoTabela()
                p.alteraUnidadeMedida()
                p.alteraValorUnitario()



        else:
            print('nao existe outras despesas nessa conta')
