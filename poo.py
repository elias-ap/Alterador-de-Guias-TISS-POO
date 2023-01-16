import typing
import xml.etree.ElementTree as Et


codigoProcedimento = '41101014'
codigoDespesa = '90289870'


class ContaTiss:
    corpoGuia: Et.Element
    guias: typing.Generator
    ans_prefix = {"ans": "http://www.ans.gov.br/padroes/tiss/schemas"}

    def __init__(self):
        caminhoGuia = r"00000000000000011306_92a0e8826a52304e3ac85dfe30c83f38.xml"
        self.corpoGuia = Et.parse(caminhoGuia, parser=Et.XMLParser(encoding="ISO-8859-1")).getroot()
        self.guias = self.corpoGuia.find('.//ans:guiasTISS', self.ans_prefix)

    def setCorpoGuia(self, corpo):
        self.setCorpoGuia(corpo)

    def getCorpoGuia(self):
        return self.corpoGuia


class Guia:
    numeroGuia: Et.ElementTree
    guia: Et.ElementTree
    procedimentosExecutados: Et.ElementTree
    outrasDespesas: Et.ElementTree
    dadosProcedimento: [Et.ElementTree]
    dadosDespesa: [Et.ElementTree]
    ans_prefix = ContaTiss.ans_prefix
    proc: str

    def __init__(self, guia, p):
        self.setNumeroGuia(guia)
        self.setGuia(guia)
        self.proc = p
        self.setProcedimentosExecutados(guia)
        self.setOutrasDespesas(guia)
        self.setListaProcedimentos()
        self.setListaDespesa()

    def setNumeroGuia(self, guia: str):
        self.numeroGuia = guia.find('.//ans:cabecalhoGuia/ans:numeroGuiaPrestador', self.ans_prefix).text

    def getNumeroGuia(self):
        return self.numeroGuia

    def setGuia(self, guia):
        self.guia = guia

    def getGuia(self):
        return self.guia

    def setProcedimentosExecutados(self, guia):
        self.procedimentosExecutados = guia.find('ans:procedimentosExecutados', self.ans_prefix)

    def getProcedimentosExecutados(self):
        return self.procedimentosExecutados

    def setOutrasDespesas(self, guia):
        self.outrasDespesas = guia.find('ans:outrasDespesas', self.ans_prefix)

    def getOutrasDespesas(self):
        return self.outrasDespesas

    def setListaProcedimentos(self):
        if Et.iselement(self.getProcedimentosExecutados()):
            self.dadosProcedimento = list(self.getProcedimentosExecutados().iterfind(
                f'.//ans:procedimento[ans:codigoProcedimento="{self.proc}"]..', self.ans_prefix))

    def getListaProcedimento(self):
        return self.dadosProcedimento

    def setListaDespesa(self):
        if Et.iselement(self.getOutrasDespesas()):
            self.dadosDespesa = list(self.getOutrasDespesas().iterfind(
                f'.//ans:servicosExecutados[ans:codigoProcedimento="{self.proc}"]..', self.ans_prefix))

    def getListaDespesa(self):
        return self.dadosDespesa

    def alteraValorTotalGeral(self, diferenca):
        valoresTotais = self.getGuia().find('ans:valorTotal', self.ans_prefix)
        valorTotalGeral = valoresTotais.find('ans:valorTotalGeral', self.ans_prefix)

        for valorTotal in valoresTotais:
            if float(valorTotal.text) > diferenca:
                valorTotal.text = '%.2f' % (float(valorTotal.text) - diferenca)
                valorTotalGeral.text = '%.2f' % (float(valorTotalGeral.text) - diferenca)
                break

        print(f"\n----- Valores totais -----\n\nValor total alterado para {valorTotal.text}")
        print(f"Valor total geral alterado para {valorTotalGeral.text}\n")


class Procedimento:
    procedimento: Et.ElementTree
    guia: Guia

    def __init__(self, procedimento, guia):
        self.setProcedimento(procedimento)
        self.guia = guia

    def setProcedimento(self, procedimento):
        self.procedimento = procedimento

    def getProcedimento(self):
        return self.procedimento

    def alteraCodigoProcedimento(self, codProc, novoCodProc):
        if len(self.guia.getListaProcedimento()) > 0:
            codigo = self.getProcedimento().find('ans:procedimento/ans:codigoProcedimento', self.guia.ans_prefix)
            if codigo.text == codProc and novoCodProc != '':
                codigo.text = novoCodProc
                print(f"Codigo de procedimento alterado de {codProc} para {novoCodProc}")

        elif len(self.guia.getListaDespesa()) > 0:
            codigo = self.getProcedimento().find('.//ans:codigoProcedimento', self.guia.ans_prefix)
            if codigo.text == codProc and novoCodProc != '':
                codigo.text = novoCodProc
                print(f"Codigo de procedimento alterado de {codProc} para {novoCodProc}")

    def alteraValorUnitario(self):
        novoValorUnitario = 10
        valorUnitario = self.getProcedimento().find('.//ans:valorUnitario', self.guia.ans_prefix)
        quantidadeExecutada = float(self.getProcedimento().find('.//ans:quantidadeExecutada', self.guia.ans_prefix).text)
        valorTotal = self.getProcedimento().find('.//ans:valorTotal', self.guia.ans_prefix)
        if float(valorUnitario.text) != novoValorUnitario:
            novoValorTotal = float(novoValorUnitario * quantidadeExecutada)
            if float(valorTotal.text) > novoValorTotal:
                diferenca = (float(valorTotal.text) - novoValorTotal)
            else:
                diferenca = (novoValorTotal - float(valorTotal.text))

            valorUnitario.text = '%.2f' % novoValorUnitario
            valorTotal.text = '%.2f' % novoValorTotal

            print(f"Valor unitario alterado para {valorUnitario.text}")
            print(f"Valor total alterado para {valorTotal.text}")

            self.guia.alteraValorTotalGeral(diferenca)

    def alteraCodigoTabela(self):
        codigoTabela = self.getProcedimento().find('.//ans:codigoTabela', self.guia.ans_prefix)
        codigoTabela.text = '050'
        print('Código de tabela alterado para: ' + codigoTabela.text)

    def alteraGrauParticipacao(self):
        grauParticipacao = self.getProcedimento().find('.//ans:grauPart', self.guia.ans_prefix)
        grauParticipacao.text = '20'
        print('Grau de participação alterado para: ' + grauParticipacao.text)
