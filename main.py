from os import path, startfile, getcwd
from customtkinter import set_appearance_mode, set_default_color_theme, CTk, CTkFrame, CTkButton, CTkLabel, CTkSwitch
from hashlib import md5
from xml.etree.ElementTree import ElementTree, Element, parse, XMLParser, iselement
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from sys import exit
from pandas import read_excel, DataFrame, ExcelWriter

ans_prefix = {"ans": "http://www.ans.gov.br/padroes/tiss/schemas"}

# Fecha a aplicação se não estiver executando a partir do diretório definido
caminho_diretorio = r"O:\Informatica\Geral\Funcionais\Faturamento de Convênios\Alterador de Guias TISS"
caminho_de_execucao = getcwd()
if caminho_de_execucao != caminho_diretorio:
    mb.showwarning('Erro',
                   f'A aplicação só pode ser executada a partir do diretório original:\n{caminho_diretorio}')
    exit()


class Conta:
    caminho_da_conta: [str]
    corpo_da_conta: ElementTree
    tag_raiz: Element
    guias_da_conta: [Element]
    qtd_alteracoes: int
    total_de_linhas_alteradas: list

    def __init__(self, caminho: str):
        self.caminho_da_conta = caminho
        self.corpo_da_conta = parse(self.caminho_da_conta, parser=XMLParser(encoding="ISO-8859-1"))
        self.tag_raiz = self.corpo_da_conta.getroot()
        self.guias_da_conta = self.tag_raiz.find('.//ans:guiasTISS', ans_prefix)
        self.qtd_alteracoes = 0
        self.total_de_linhas_alteradas = []

    def gerarNovoHash(self):
        # Remove o código hash atual
        self.tag_raiz.find('ans:epilogo', ans_prefix).find('ans:hash', ans_prefix).text = ''
        todas_tags_da_conta = self.tag_raiz.iter()

        lista_de_texto = []
        linha_de_texto_unica = ''
        for tag in todas_tags_da_conta:
            # Remove os paragráfos
            lista_de_texto.append(tag.text.replace("\n", ''))

        for texto in lista_de_texto:
            # Forma uma linha única com todos os textos da conta/arquivo
            linha_de_texto_unica += texto

        # Cria um novo código hash a partir da linha
        h = md5(linha_de_texto_unica.encode('iso-8859-1'))
        novo_codigo_hash = h.hexdigest()
        return novo_codigo_hash

    def salvarConta(self):
        nome_da_conta = path.basename(self.caminho_da_conta).split("_")[0]
        caminho = path.abspath(self.caminho_da_conta).rsplit("\\", 1)[0]
        novo_codigo_hash = self.gerarNovoHash()
        self.tag_raiz.find('ans:epilogo', ans_prefix).find('ans:hash', ans_prefix).text = novo_codigo_hash
        self.corpo_da_conta.write(f'{caminho}\\{nome_da_conta}_{novo_codigo_hash}.xml', encoding="ISO-8859-1")


class Guia:
    numero_da_guia: ElementTree
    guia: ElementTree

    tag_procedimentosExecutados: ElementTree
    tag_outrasDespesas: ElementTree
    codigo_de_procedimento: str

    # Esses atributos irão armazenar uma lista com todos os dados de procedimento ou despesa com código correspondente
    lista_de_procedimentos_executados: [ElementTree]
    lista_de_despesas: [ElementTree]

    def __init__(self, guia, codigo):
        self.setNumeroDaGuia(guia)
        self.setGuia(guia)

        self.codigo_de_procedimento = codigo

        self.setProcedimentosExecutados(guia)
        self.setOutrasDespesas(guia)

        self.setListaDeProcedimentosExecutados()
        self.setListaDeDespesas()

    def setNumeroDaGuia(self, guia: []):
        self.numero_da_guia = guia.find('.//ans:cabecalhoGuia/ans:numeroGuiaPrestador', ans_prefix).text

    def getNumeroGuia(self):
        return self.numero_da_guia

    def setGuia(self, guia):
        self.guia = guia

    def getGuia(self):
        return self.guia

    def setProcedimentosExecutados(self, guia):
        self.tag_procedimentosExecutados = guia.find('ans:procedimentosExecutados', ans_prefix)

    def getProcedimentosExecutados(self):
        return self.tag_procedimentosExecutados

    def setOutrasDespesas(self, guia):
        self.tag_outrasDespesas = guia.find('ans:outrasDespesas', ans_prefix)

    def getOutrasDespesas(self):
        return self.tag_outrasDespesas

    def setListaDeProcedimentosExecutados(self):
        if iselement(self.getProcedimentosExecutados()):
            self.lista_de_procedimentos_executados = list(self.getProcedimentosExecutados().iterfind(
                f'.//ans:procedimento[ans:codigoProcedimento="{self.codigo_de_procedimento}"]..', ans_prefix))

    def getListaDeProcedimentosExecutados(self):
        return self.lista_de_procedimentos_executados

    def setListaDeDespesas(self):
        if iselement(self.getOutrasDespesas()):
            self.lista_de_despesas = list(self.getOutrasDespesas().iterfind(
                f'.//ans:servicosExecutados[ans:codigoProcedimento="{self.codigo_de_procedimento}"]..', ans_prefix))

    def getListaDeDespesa(self):
        return self.lista_de_despesas

    def alteraValorTotalGeral(self, diferenca):
        valores_totais = self.getGuia().find('ans:valorTotal', ans_prefix)
        valor_total_geral = valores_totais.find('ans:valorTotalGeral', ans_prefix)

        for valor_total in valores_totais:
            if float(valor_total.text) > diferenca:
                valor_total.text = '%.2f' % (float(valor_total.text) - diferenca)
                valor_total_geral.text = '%.2f' % (float(valor_total_geral.text) - diferenca)
                break


class Procedimento:
    procedimento: ElementTree
    guia: Guia
    qtd_alteracoes: int = 0
    linha_alterada: list

    def __init__(self, procedimento, guia):
        self.setProcedimento(procedimento)
        self.guia = guia
        self.linha_alterada = []

    def setProcedimento(self, procedimento):
        self.procedimento = procedimento

    def getProcedimento(self):
        return self.procedimento

    def podeAlterar(self):
        # Se a guia for específicada altera apenas quando a mesma estiver sendo processada
        if numero_guia != '':
            if numero_guia == self.guia.getNumeroGuia():
                return True
            else:
                return False

        else:
            return True

    def alteraCodigoProcedimentoExecutado(self, codigo, novo_codigo):
        if self.podeAlterar() and len(self.guia.getListaDeProcedimentosExecutados()) > 0:
            tag_codigo_de_procedimento = self.getProcedimento().find('ans:procedimento/ans:codigoProcedimento',
                                                                     ans_prefix)
            if tag_codigo_de_procedimento.text == codigo and novo_codigo != '':
                self.linha_alterada.append(
                    (self.guia.getNumeroGuia(),
                     self.guia.codigo_de_procedimento,
                     'Código de procedimento',
                     tag_codigo_de_procedimento.text,
                     novo_codigo)
                )
                tag_codigo_de_procedimento.text = novo_codigo
                self.qtd_alteracoes += 1

    def alteraCodigoProcedimentoDespesa(self, codigo, novo_codigo):
        if self.podeAlterar() and len(self.guia.getListaDeDespesa()) > 0:
            tag_codigo_de_procedimento = self.getProcedimento().find('.//ans:codigoProcedimento', ans_prefix)
            if tag_codigo_de_procedimento.text == codigo and novo_codigo != '':
                self.linha_alterada.append(
                    (self.guia.getNumeroGuia(),
                     self.guia.codigo_de_procedimento,
                     'Código de procedimento',
                     tag_codigo_de_procedimento.text,
                     novo_codigo)
                )
                tag_codigo_de_procedimento.text = novo_codigo
                self.qtd_alteracoes += 1

    def alteraValorUnitario(self, valor, novo_valor):
        try:
            if self.podeAlterar() and len(self.guia.getListaDeDespesa()) > 0 or len(
                    self.guia.getListaDeProcedimentosExecutados()) > 0:

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

                    self.linha_alterada.append(
                        (self.guia.getNumeroGuia(),
                         self.guia.codigo_de_procedimento,
                         'Valor unitário',
                         tag_valor_unitario.text,
                         novo_valor)
                    )
                    tag_valor_unitario.text = '%.2f' % novo_valor
                    valor_total.text = '%.2f' % novoValorTotal
                    self.qtd_alteracoes += 1
                    self.guia.alteraValorTotalGeral(diferenca)
        except AttributeError:
            pass

    def alteraCodigoDeTabela(self, codigo, novo_codigo):
        if self.podeAlterar() and len(self.guia.getListaDeDespesa()) > 0 or len(
                self.guia.getListaDeProcedimentosExecutados()) > 0:
            tag_codigo_tabela = self.getProcedimento().find('.//ans:codigoTabela', ans_prefix)
            if tag_codigo_tabela.text == codigo and novo_codigo != '':
                self.linha_alterada.append(
                    (self.guia.getNumeroGuia(),
                     self.guia.codigo_de_procedimento,
                     'Código de tabela',
                     tag_codigo_tabela.text,
                     novo_codigo)
                )
                tag_codigo_tabela.text = novo_codigo
                self.qtd_alteracoes += 1

    def alteraCodigoDeDespesa(self, codigo, novo_codigo):
        if self.podeAlterar() and len(self.guia.getListaDeDespesa()):
            tag_codigo_despesa = self.getProcedimento().find('.//ans:codigoDespesa', ans_prefix)
            if tag_codigo_despesa.text == codigo and novo_codigo != '':
                self.linha_alterada.append(
                    (self.guia.getNumeroGuia(),
                     self.guia.codigo_de_procedimento,
                     'Código de despesa',
                     tag_codigo_despesa.text,
                     novo_codigo)
                )
                tag_codigo_despesa.text = novo_codigo
                self.qtd_alteracoes += 1

    def alteraGrauDeParticipacao(self, grau, novo_grau):
        if self.podeAlterar() and len(self.guia.getListaDeProcedimentosExecutados()) > 0:
            tag_grau_participacao = self.getProcedimento().find('.//ans:grauPart', ans_prefix)

            if tag_grau_participacao.text == grau and novo_grau != '':
                self.linha_alterada.append(
                    (self.guia.getNumeroGuia(),
                     self.guia.codigo_de_procedimento,
                     'Grau de participação',
                     tag_grau_participacao.text,
                     novo_grau)
                )
                tag_grau_participacao.text = novo_grau
                self.qtd_alteracoes += 1

    def alteraUnidadeDeMedida(self, unidade, nova_unidade):
        if self.podeAlterar() and len(self.guia.getListaDeDespesa()):
            tag_unidade_de_medida = self.getProcedimento().find('.//ans:unidadeMedida', ans_prefix)

            if tag_unidade_de_medida.text == unidade and nova_unidade != '':
                self.linha_alterada.append(
                    (self.guia.getNumeroGuia(),
                     self.guia.codigo_de_procedimento,
                     'Unidade de medida',
                     tag_unidade_de_medida.text,
                     nova_unidade)
                )
                tag_unidade_de_medida.text = nova_unidade
                self.qtd_alteracoes += 1


class Tabela:
    tabela_de_dados: DataFrame
    tabela_de_valores: DataFrame
    tabela_de_logs: DataFrame

    def __init__(self):
        self.tabela_de_dados = read_excel("Planilha de Críticas.xlsx", sheet_name='Dados', dtype=str,
                                          keep_default_na=False)
        self.tabela_de_valores = read_excel("Planilha de Críticas.xlsx", sheet_name='Valores', dtype=str,
                                            keep_default_na=False)

        self.tabela_de_logs = read_excel("Planilha de Críticas.xlsx", sheet_name='Log', dtype=str,
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

        for indice, texto in self.tabela_de_dados['Unidade de medida (atual)'].items():
            tamanho_texto = len(texto)

            if tamanho_texto == 2:
                self.tabela_de_dados['Unidade de medida (atual)'][indice] = texto.rjust(tamanho_texto + 1, '0')

        for indice, texto in self.tabela_de_dados['Tipo de tabela (novo)'].items():
            if texto == '0':
                texto = '00'
                self.tabela_de_dados['Tipo de tabela (novo)'][indice] = texto

    def getTabelaDados(self):
        return self.tabela_de_dados.values

    def getTabelaValores(self):
        return self.tabela_de_valores.values

    @staticmethod
    def geraLog(lista_de_alteracoes):
        lista_tratada = []
        for lista in list(filter(None, lista_de_alteracoes)):
            for item in lista:
                lista_tratada.append(item)

        df = DataFrame(lista_tratada,
                       columns=['Número da guia', 'Código de procedimento', 'Dado alterado', 'De', 'Para'])

        with ExcelWriter(
                "Planilha de Críticas.xlsx",
                mode="a",
                engine="openpyxl",
                if_sheet_exists="replace", ) as writer:
            df.to_excel(writer, sheet_name='Log')


class Interface:
    # Configuracões do customtkinter
    set_appearance_mode('dark')
    set_default_color_theme('green')
    # iconbitmap(main_window, r'Resources/icon.ico')

    janela_principal: CTk()
    frame: CTkFrame

    # Widgets
    abrir_planilha: CTkButton
    gerar_hash: CTkButton
    carregar_guia: CTkButton

    tipo_de_alteracoes: CTkLabel
    alteracao_de_dados: CTkSwitch
    alteracao_de_valor: CTkSwitch

    realizar_alteracoes: CTkButton
    cancelar: CTkButton

    salvar_conta: CTkButton
    conta: Conta

    def __init__(self):
        # Configurações da janela principal
        self.janela_principal = CTk()
        self.janela_principal.geometry('300x260')
        self.janela_principal.title('Alterador de Guias TISS')
        self.janela_principal.eval('tk::PlaceWindow . center')
        self.janela_principal.maxsize(300, 260)

        self.frame = CTkFrame(self.janela_principal)
        self.frame.pack(side='left', fill='both', padx=10, pady=10, expand=True)

        self.layoutPadrao()

    def layoutPadrao(self):
        self.abrir_planilha = CTkButton(self.frame, text='Abrir planilha', command=lambda: self.abrirPLanilha())
        self.abrir_planilha.pack(side='bottom', pady=5, padx=5)

        self.gerar_hash = CTkButton(self.frame, text='Gerar hash', command=lambda: self.gerarNovoHashParaVariasContas())
        self.gerar_hash.pack(side='bottom', pady=5, padx=5)

        self.carregar_guia = CTkButton(self.frame, text='Carregar guia',
                                       command=lambda: self.carregarConta())
        self.carregar_guia.pack(side='bottom', pady=5, padx=5)

    def layoutAposCarregarConta(self):
        self.gerar_hash.destroy()
        self.carregar_guia.destroy()

        self.tipo_de_alteracoes = CTkLabel(self.frame, text='Escolha os modos de alteração:')
        self.tipo_de_alteracoes.pack(side='top', pady=5, padx=5)

        self.alteracao_de_dados = CTkSwitch(self.frame, text='Alteração de dados', text_color='white')
        self.alteracao_de_dados.pack(pady=10, padx=5)

        self.alteracao_de_valor = CTkSwitch(self.frame, text='Alteração de valor', text_color='white')
        self.alteracao_de_valor.pack(side='top', padx=5, pady=10)

        self.cancelar = CTkButton(self.frame, text='Cancelar', command=lambda: self.cancelarOperacao())
        self.cancelar.pack(side='bottom', pady=5, padx=5)

        self.realizar_alteracoes = CTkButton(self.frame, text='Realizar alterações', command=lambda: self.alterar())
        self.realizar_alteracoes.pack(side='bottom', pady=5, padx=5)

    @staticmethod
    def abrirPLanilha():
        caminho = path.abspath('Planilha de Críticas.xlsx')
        startfile(f"{caminho}")

    def carregarConta(self):
        tipo_de_arquivos = (('XML files', '*.xml'), ('All files', '*.*'))
        caminho_da_conta = fd.askopenfilename(filetypes=tipo_de_arquivos)

        # Verifica se o caminho recebido é um arquivo
        if path.isfile(caminho_da_conta):
            self.conta = Conta(caminho_da_conta)
            self.layoutAposCarregarConta()
        else:
            mb.showwarning(title='Erro', message='A conta não foi escolhida')

    def defineTipoDeAlteracao(self):
        altera_dados = self.alteracao_de_dados.get()
        altera_valores = self.alteracao_de_valor.get()
        if altera_dados == 1:
            altera_dados = True
        else:
            altera_dados = False

        if altera_valores == 1:
            altera_valores = True
        else:
            altera_valores = False

        return altera_dados, altera_valores

    def alterar(self):
        altera_dados, altera_valores = self.defineTipoDeAlteracao()

        if altera_dados is True:
            alteraDados(self.conta)

        if altera_valores is True:
            alteraValores(self.conta)

        if altera_dados is False and altera_valores is False:
            mb.showinfo('Info', 'Informe o tipo de alteração a ser realizada')

        elif self.conta.qtd_alteracoes > 0:
            self.aguardarSalvamento()
        else:
            mb.showwarning('Erro', 'Nenhuma alteração realizada')

    def aguardarSalvamento(self):
        for button in (self.realizar_alteracoes, self.alteracao_de_valor,
                       self.alteracao_de_dados, self.tipo_de_alteracoes):
            button.destroy()

        self.salvar_conta = CTkButton(self.frame, text='Salvar Guia', command=lambda: self.salvarConta())
        self.salvar_conta.pack(side='bottom', pady=5, padx=5)

    def salvarConta(self):
        self.conta.salvarConta()
        self.cancelarOperacao()
        mb.showinfo('Info', 'Arquivo salvo')
        Tabela.geraLog(self.conta.total_de_linhas_alteradas)

    def cancelarOperacao(self):
        if self.conta.qtd_alteracoes == 0:
            for button in (
                    self.realizar_alteracoes, self.cancelar, self.alteracao_de_dados,
                    self.alteracao_de_valor,
                    self.tipo_de_alteracoes, self.abrir_planilha):
                button.destroy()
        elif self.conta.qtd_alteracoes > 0:
            for button in (self.salvar_conta, self.cancelar, self.abrir_planilha):
                button.destroy()

        self.layoutPadrao()

    def gerarNovoHashParaVariasContas(self):
        tipo_de_arquivos = (('XML files', '*.xml'), ('All files', '*.*'))
        lista_de_caminho_das_contas = fd.askopenfilenames(filetypes=tipo_de_arquivos)

        # Verifica se o caminho recebido é um arquivo
        if len(lista_de_caminho_das_contas) > 0:
            for caminho in lista_de_caminho_das_contas:
                if path.isfile(caminho):
                    conta = Conta(caminho)
                    conta.salvarConta()
            mb.showinfo('Info', 'Arquivos salvos')
        else:
            mb.showwarning(title='Erro', message='Nenhuma conta escolhida')


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
           grau_de_participacao, novo_grau_de_participacao, codigo_de_desepsa, novo_codigo_de_despesa, \
           unidade_de_medida, novo_unidade_de_medida


def setLinhaAlteracaoDeValores(linha):
    global numero_guia
    numero_guia = linha[0]
    codigo_procedimento = linha[1]
    valor_unitario = linha[2]
    novo_valor_unitario = linha[3]

    return numero_guia, codigo_procedimento, valor_unitario, novo_valor_unitario


def alteraDados(conta):
    tabela = Tabela()
    for linha in tabela.getTabelaDados():
        numero_guia, codigoDeProcedimento, novoCodigoDeProcedimento, tipoDeTabela, novoTipoDeTabela, \
        grauDeParticipacao, novoGrauDeParticipacao, codigoDeDesepsa, novoCodigoDeDespesa, unidadeDeMedida, \
        novoUnidadeDeMedida = setLinhaAlteracaoDeDados(linha)

        for item in conta.guias_da_conta:
            guia = Guia(item, codigoDeProcedimento)

            if iselement(guia.getProcedimentosExecutados()):
                for procedimento in guia.getListaDeProcedimentosExecutados():
                    p = Procedimento(procedimento, guia)
                    p.alteraCodigoProcedimentoExecutado(codigoDeProcedimento, novoCodigoDeProcedimento)
                    p.alteraGrauDeParticipacao(grauDeParticipacao, novoGrauDeParticipacao)
                    p.alteraCodigoDeTabela(tipoDeTabela, novoTipoDeTabela)
                    conta.qtd_alteracoes += p.qtd_alteracoes
                    conta.total_de_linhas_alteradas.append(p.linha_alterada)

            if iselement(guia.getOutrasDespesas()):
                for procedimento in guia.getListaDeDespesa():
                    p = Procedimento(procedimento, guia)
                    p.alteraCodigoProcedimentoDespesa(codigoDeProcedimento, novoCodigoDeProcedimento)
                    p.alteraCodigoDeDespesa(codigoDeDesepsa, novoCodigoDeDespesa)
                    p.alteraCodigoDeTabela(tipoDeTabela, novoTipoDeTabela)
                    p.alteraUnidadeDeMedida(unidadeDeMedida, novoUnidadeDeMedida)
                    conta.qtd_alteracoes += p.qtd_alteracoes
                    conta.total_de_linhas_alteradas.append(p.linha_alterada)


def alteraValores(conta):
    tabela = Tabela()
    for linha in tabela.getTabelaValores():
        numero_da_guia, codigoDeProcedimento, valor, novoValor = setLinhaAlteracaoDeValores(linha)

        for item in conta.guias_da_conta:
            guia = Guia(item, codigoDeProcedimento)

            if iselement(guia.getProcedimentosExecutados()):
                for procedimento in guia.getListaDeProcedimentosExecutados():
                    p = Procedimento(procedimento, guia)
                    p.alteraValorUnitario(valor, novoValor)
                    conta.qtd_alteracoes += p.qtd_alteracoes
                    conta.total_de_linhas_alteradas.append(p.linha_alterada)

            if iselement(guia.getOutrasDespesas()):
                for procedimento in guia.getListaDeDespesa():
                    p = Procedimento(procedimento, guia)
                    p.alteraValorUnitario(valor, novoValor)
                    conta.qtd_alteracoes += p.qtd_alteracoes
                    conta.total_de_linhas_alteradas.append(p.linha_alterada)


interface = Interface()
interface.janela_principal.mainloop()
