import xml.etree.ElementTree as Et
from pandas import read_excel, DataFrame

ans_prefix = {"ans": "http://www.ans.gov.br/padroes/tiss/schemas"}


class Conta:
    corpo_guia: Et.Element
    guias: [Et.Element]

    def __init__(self):
        caminho_guia = r"00000000000000011306_92a0e8826a52304e3ac85dfe30c83f38.xml"
        self.corpo_guia = Et.parse(caminho_guia, parser=Et.XMLParser(encoding="ISO-8859-1")).getroot()
        self.guias = self.corpo_guia.find('.//ans:guiasTISS', ans_prefix)

    def setCorpoGuia(self, corpo_guia):
        self.setCorpoGuia(corpo_guia)

    def getCorpoGuia(self):
        return self.corpo_guia


class Guia:
    numero_guia: Et.ElementTree
    guia: Et.ElementTree
    procedimentos: Et.ElementTree
    despesas: Et.ElementTree
    lista_de_procedimentos: [Et.ElementTree]
    lista_de_despesas: [Et.ElementTree]
    procedimento: str

    def __init__(self, guia, p):
        self.setNumeroGuia(guia)
        self.setGuia(guia)
        self.procedimento = p
        self.setProcedimentosExecutados(guia)
        self.setDespesas(guia)
        self.setListaProcedimentos()
        self.setListaDespesa()

    def setNumeroGuia(self, guia: []):
        self.numero_guia = guia.find('.//ans:cabecalhoGuia/ans:numeroGuiaPrestador', ans_prefix).text

    def getNumeroGuia(self):
        return self.numero_guia

    def setGuia(self, guia):
        self.guia = guia

    def getGuia(self):
        return self.guia

    def setProcedimentosExecutados(self, guia):
        self.procedimentos = guia.find('ans:procedimentosExecutados', ans_prefix)

    def getProcedimentosExecutados(self):
        return self.procedimentos

    def setDespesas(self, guia):
        self.despesas = guia.find('ans:outrasDespesas', ans_prefix)

    def getDespesas(self):
        return self.despesas

    def setListaProcedimentos(self):
        if Et.iselement(self.getProcedimentosExecutados()):
            self.lista_de_procedimentos = list(self.getProcedimentosExecutados().iterfind(
                f'.//ans:procedimento[ans:codigoProcedimento="{self.procedimento}"]..', ans_prefix))

    def getListaProcedimento(self):
        return self.lista_de_procedimentos

    def setListaDespesa(self):
        if Et.iselement(self.getDespesas()):
            self.lista_de_despesas = list(self.getDespesas().iterfind(
                f'.//ans:servicosExecutados[ans:codigoProcedimento="{self.procedimento}"]..', ans_prefix))

    def getListaDespesa(self):
        return self.lista_de_despesas

    def alteraValorTotalGeral(self, diferenca):
        valores_totais = self.getGuia().find('ans:valorTotal', ans_prefix)
        valor_total_geral = valores_totais.find('ans:valorTotalGeral', ans_prefix)

        for valor_total in valores_totais:
            if float(valor_total.text) > diferenca:
                valor_total.text = '%.2f' % (float(valor_total.text) - diferenca)
                valor_total_geral.text = '%.2f' % (float(valor_total_geral.text) - diferenca)
                break

        print(f"\n----- Valores totais -----\n\nValor total alterado para {valor_total.text}")
        print(f"Valor total geral alterado para {valor_total_geral.text}\n")


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

    def podeAlterar(self):
        if numero_guia != '':
            if numero_guia == self.guia.getNumeroGuia():
                return True
            else:
                return False

        else:
            return True

    def alteraCodigoProcedimentoExecutado(self, codigo, novo_codigo):
        if self.podeAlterar():
            if len(self.guia.getListaProcedimento()) > 0:
                tag_codigo_de_procedimento = self.getProcedimento().find('ans:procedimento/ans:codigoProcedimento', ans_prefix)
                if tag_codigo_de_procedimento.text == codigo and novo_codigo != '':
                    tag_codigo_de_procedimento.text = novo_codigo
                    print(f"Codigo de procedimento (executado) alterado de {codigo} para {novo_codigo}")

    def alteraCodigoProcedimentoDespesa(self, codigo, novo_codigo):
        if self.podeAlterar():
            if len(self.guia.getListaDespesa()) > 0:
                tag_codigo_de_procedimento = self.getProcedimento().find('.//ans:codigoProcedimento', ans_prefix)
                if tag_codigo_de_procedimento.text == codigo and novo_codigo != '':
                    tag_codigo_de_procedimento.text = novo_codigo
                    print(f"Codigo de procedimento (despesa) alterado de {codigo} para {novo_codigo}")

    def alteraValorUnitario(self, valor, novo_valor):
        if self.podeAlterar():
            tag_valor_unitario = self.getProcedimento().find('.//ans:valorUnitario', ans_prefix)
            quantidade_executada = float(
                self.getProcedimento().find('.//ans:quantidadeExecutada', ans_prefix).text)
            valor_total = self.getProcedimento().find('.//ans:valorTotal', ans_prefix)

            if float(tag_valor_unitario.text) == valor and float(tag_valor_unitario.text) != novo_valor:
                novoValorTotal = float(novo_valor * quantidade_executada)
                if float(valor_total.text) > novoValorTotal:
                    diferenca = (float(valor_total.text) - novoValorTotal)
                else:
                    diferenca = (novoValorTotal - float(valor_total.text))

                tag_valor_unitario.text = '%.2f' % novo_valor
                valor_total.text = '%.2f' % novoValorTotal

                print(f"Valor unitario alterado para {tag_valor_unitario.text}")
                print(f"Valor total alterado para {valor_total.text}")

                self.guia.alteraValorTotalGeral(diferenca)

    def alteraCodigoDeTabela(self, codigo, novo_codigo):
        if self.podeAlterar():
            tag_codigo_tabela = self.getProcedimento().find('.//ans:codigoTabela', ans_prefix)
            if tag_codigo_tabela.text == codigo and novo_codigo != '':
                tag_codigo_tabela.text = novo_codigo
                print('Código de tabela alterado para: ' + tag_codigo_tabela.text)

    def alteraCodigoDeDespesa(self, codigo, novo_codigo):
        if self.podeAlterar():
            tag_codigo_despesa = self.getProcedimento().find('.//ans:codigoDespesa', ans_prefix)
            if tag_codigo_despesa.text == codigo and novo_codigo != '':
                tag_codigo_despesa.text = novo_codigo
                print('Código de despesa alterado para: ' + tag_codigo_despesa.text)

    def alteraGrauDeParticipacao(self, grau, novo_grau):
        if self.podeAlterar():
            tag_grau_participacao = self.getProcedimento().find('.//ans:grauPart', ans_prefix)
            if tag_grau_participacao.text == grau and novo_grau != '':
                tag_grau_participacao.text = novo_grau
                print('Código de despesa alterado para: ' + tag_grau_participacao.text)

    def alteraUnidadeDeMedida(self, unidade, nova_unidade):
        if self.podeAlterar():
            tag_unidade_de_medida = self.getProcedimento().find('.//ans:unidadeMedida', ans_prefix)
            if tag_unidade_de_medida.text == unidade and nova_unidade != '':
                tag_unidade_de_medida.text = nova_unidade
                print('Unidade de medida alterado para: ' + tag_unidade_de_medida.text)


class TabelaDeCritica:
    tabela_de_dados: DataFrame
    tabela_de_valores: DataFrame

    def __init__(self):
        self.tabela_de_dados = read_excel("Planilha de Críticas.xlsx", sheet_name='Dados', dtype=str, keep_default_na=False)
        self.tabela_de_valores = read_excel("Planilha de Críticas.xlsx", sheet_name='Valores', dtype=str,
                                            keep_default_na=False)
        self.formataDadosTabelaValores()
        self.formataDadosTabelaDados()

    def formataDadosTabelaValores(self):
        coluna_valor_atual = self.tabela_de_valores['Valor unitário (atual)'].str.replace(',', '.')
        coluna_valor_novo = self.tabela_de_valores['Valor unitário (novo)'].str.replace(',', '.')

        self.tabela_de_valores['Valor unitário (atual)'] = coluna_valor_atual
        self.tabela_de_valores['Valor unitário (novo)'] = coluna_valor_novo
        self.tabela_de_valores['Valor unitário (atual)'] = coluna_valor_atual.astype(float)
        self.tabela_de_valores['Valor unitário (novo)'] = coluna_valor_novo.astype(float)

    def formataDadosTabelaDados(self):
        for indice, texto in self.tabela_de_dados['Unidade de medida (novo)'].items():
            tamanho_texto = len(texto)
            if tamanho_texto == 2:
                self.tabela_de_dados['Unidade de medida (novo)'][indice] = texto.rjust(tamanho_texto + 1, '0')

        for indice, texto in self.tabela_de_dados['Tipo de tabela (novo)'].items():
            if texto == '0':
                texto = '00'
                self.tabela_de_dados['Tipo de tabela (novo)'][indice] = texto

    def getTabelaDados(self):
        return self.tabela_de_dados.values

    def getTabelaValores(self):
        return self.tabela_de_valores.values


def setLinhaAlteracaoDeDados(linha):
    global numero_guia
    numero_guia = linha[0]
    codigo_de_procedimento = linha[1]
    novo_codigo_de_procedimento = linha[2]
    codigo_de_tabela = linha[3]
    novo_codigo_de_tabela = linha[4]
    grau_de_participacao = linha[5]
    novo_grau_de_participacao = linha[6]
    codigo_de_desepsa = linha[7]
    novo_codigo_de_despesa = linha[8]
    unidade_de_medida = linha[9]
    novo_unidade_de_medida = linha[10]

    return numero_guia, codigo_de_procedimento, novo_codigo_de_procedimento, codigo_de_tabela, novo_codigo_de_tabela, \
           grau_de_participacao, novo_grau_de_participacao, codigo_de_desepsa, novo_codigo_de_despesa, unidade_de_medida, \
           novo_unidade_de_medida


def setLinhaAlteracaoDeValores(linha):
    numero_guia = linha[0]
    codigo_procedimento = linha[1]
    valor_unitario = linha[2]
    novo_valor_unitario = linha[3]

    return numero_guia, codigo_procedimento, valor_unitario, novo_valor_unitario
