from poo import *

conta = Conta()
tabela = TabelaDeCritica()
for linha in tabela.getTabelaDados():
    numero_guia, codigoDeProcedimento, novoCodigoDeProcedimento, tipoDeTabela, novoTipoDeTabela, \
    grauDeParticipacao, novoGrauDeParticipacao, codigoDeDesepsa, novoCodigoDeDespesa, unidadeDeMedida, \
    novoUnidadeDeMedida = setLinhaAlteracaoDeDados(linha)

    for item in conta.guias:
        guia = Guia(item, codigoDeProcedimento)

        print('----------- ' + guia.getNumeroGuia() + ' -----------')
        if Et.iselement(guia.getProcedimentosExecutados()):
            for procedimento in guia.getListaProcedimento():
                p = Procedimento(procedimento, guia)
                p.alteraCodigoProcedimentoExecutado(codigoDeProcedimento, novoCodigoDeProcedimento)
                p.alteraGrauDeParticipacao(grauDeParticipacao, novoGrauDeParticipacao)
                p.alteraCodigoDeTabela(tipoDeTabela, novoTipoDeTabela)

        if Et.iselement(guia.getDespesas()):
            for procedimento in guia.getListaDespesa():
                p = Procedimento(procedimento, guia)
                p.alteraCodigoProcedimentoDespesa(codigoDeProcedimento, novoCodigoDeProcedimento)
                p.alteraCodigoDeDespesa(codigoDeDesepsa, novoCodigoDeDespesa)
                p.alteraCodigoDeTabela(tipoDeTabela, novoTipoDeTabela)
                p.alteraUnidadeDeMedida(unidadeDeMedida, novoUnidadeDeMedida)

for linha in tabela.getTabelaValores():
    numero_guia, codigoDeProcedimento, valor, novoValor = setLinhaAlteracaoDeValores(linha)

    for item in conta.guias:
        guia = Guia(item, codigoDeProcedimento)

        print('----------- ' + guia.getNumeroGuia() + ' -----------')
        if Et.iselement(guia.getProcedimentosExecutados()):
            for procedimento in guia.getListaProcedimento():
                p = Procedimento(procedimento, guia)
                p.alteraValorUnitario(valor, novoValor)

        if Et.iselement(guia.getDespesas()):
            for procedimento in guia.getListaDespesa():
                p = Procedimento(procedimento, guia)
                p.alteraValorUnitario(valor, novoValor)

conta.salvarConta()