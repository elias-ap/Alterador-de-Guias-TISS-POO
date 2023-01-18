import hashlib
import os
import xml.etree.ElementTree as Et
import customtkinter as ctk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from pandas import read_excel, DataFrame

ans_prefix = {"ans": "http://www.ans.gov.br/padroes/tiss/schemas"}


class Conta:
    caminho_conta: [str]
    corpo_conta: Et.ElementTree
    tag_raiz: Et.Element
    guias: [Et.Element]

    def __init__(self, caminho: str):
        self.caminho_conta = caminho
        self.corpo_conta = Et.parse(self.caminho_conta, parser=Et.XMLParser(encoding="ISO-8859-1"))
        self.tag_raiz = self.corpo_conta.getroot()
        self.guias = self.tag_raiz.find('.//ans:guiasTISS', ans_prefix)

    def salvarConta(self):
        nome_da_conta = os.path.basename(self.caminho_conta).split("_")[0]
        caminho = os.path.abspath(self.caminho_conta).rsplit("\\", 1)[0]
        novo_codigo_hash = self.gerarNovoHash()
        self.corpo_conta.write(f'{caminho}\{nome_da_conta}_{novo_codigo_hash}.xml', encoding="ISO-8859-1")

    def gerarNovoHash(self):
        self.tag_raiz.find('ans:epilogo', ans_prefix).find('ans:hash', ans_prefix).text = ''
        todas_tags_da_conta = self.tag_raiz.iter()

        lista_de_texto = []
        linha_de_texto_unica = ''
        for tag in todas_tags_da_conta:
            # REMOVE OS PARÁGRAFOS
            lista_de_texto.append(tag.text.replace("\n", ''))

        for texto in lista_de_texto:
            linha_de_texto_unica += texto

        h = hashlib.md5(linha_de_texto_unica.encode('iso-8859-1'))
        novo_codigo_hash = h.hexdigest()
        return novo_codigo_hash


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
    qtd_alteracoes: int = 0

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
                tag_codigo_de_procedimento = self.getProcedimento().find('ans:procedimento/ans:codigoProcedimento',
                                                                         ans_prefix)
                if tag_codigo_de_procedimento.text == codigo and novo_codigo != '':
                    tag_codigo_de_procedimento.text = novo_codigo
                    self.qtd_alteracoes += 1
                    print(f"Codigo de procedimento (executado) alterado de {codigo} para {novo_codigo}")

    def alteraCodigoProcedimentoDespesa(self, codigo, novo_codigo):
        if self.podeAlterar():
            if len(self.guia.getListaDespesa()) > 0:
                tag_codigo_de_procedimento = self.getProcedimento().find('.//ans:codigoProcedimento', ans_prefix)
                if tag_codigo_de_procedimento.text == codigo and novo_codigo != '':
                    tag_codigo_de_procedimento.text = novo_codigo
                    self.qtd_alteracoes += 1
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
                self.qtd_alteracoes += 1
                print(f"Valor unitario alterado para {tag_valor_unitario.text}")
                print(f"Valor total alterado para {valor_total.text}")

                self.guia.alteraValorTotalGeral(diferenca)

    def alteraCodigoDeTabela(self, codigo, novo_codigo):
        if self.podeAlterar():
            tag_codigo_tabela = self.getProcedimento().find('.//ans:codigoTabela', ans_prefix)
            if tag_codigo_tabela.text == codigo and novo_codigo != '':
                tag_codigo_tabela.text = novo_codigo
                self.qtd_alteracoes += 1
                print('Código de tabela alterado para: ' + tag_codigo_tabela.text)

    def alteraCodigoDeDespesa(self, codigo, novo_codigo):
        if self.podeAlterar():
            tag_codigo_despesa = self.getProcedimento().find('.//ans:codigoDespesa', ans_prefix)
            if tag_codigo_despesa.text == codigo and novo_codigo != '':
                tag_codigo_despesa.text = novo_codigo
                self.qtd_alteracoes += 1
                print('Código de despesa alterado para: ' + tag_codigo_despesa.text)

    def alteraGrauDeParticipacao(self, grau, novo_grau):
        if self.podeAlterar():
            tag_grau_participacao = self.getProcedimento().find('.//ans:grauPart', ans_prefix)
            if tag_grau_participacao.text == grau and novo_grau != '':
                tag_grau_participacao.text = novo_grau
                self.qtd_alteracoes += 1
                print('Código de despesa alterado para: ' + tag_grau_participacao.text)

    def alteraUnidadeDeMedida(self, unidade, nova_unidade):
        if self.podeAlterar():
            tag_unidade_de_medida = self.getProcedimento().find('.//ans:unidadeMedida', ans_prefix)
            if tag_unidade_de_medida.text == unidade and nova_unidade != '':
                tag_unidade_de_medida.text = nova_unidade
                self.qtd_alteracoes += 1
                print('Unidade de medida alterado para: ' + tag_unidade_de_medida.text)


class Tabela:
    tabela_de_dados: DataFrame
    tabela_de_valores: DataFrame

    def __init__(self):
        self.tabela_de_dados = read_excel("Planilha de Críticas.xlsx", sheet_name='Dados', dtype=str,
                                          keep_default_na=False)
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


# GUI COLOR CONFIG
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('green')


class Interface:
    # MAIN WINDOW
    main_window: ctk.CTk()
    # ctk.CTk.iconbitmap(main_window, r'Resources/icon.ico')

    # MAIN FRAME
    frame: ctk.CTkFrame

    # DEFAULT BUTTON
    open_plan_button: ctk.CTkButton

    # RELATIVE BUTTONS
    generateHashAndSave_button: ctk.CTkButton
    botao_carregar_guia: ctk.CTkButton

    # BUTTONS AFTER GUIDE CHOOSE
    # cancel_button = ctk.CTkButton(frame, text='Cancelar')
    # cancel_button.pack(side='bottom', pady=5, padx=5)

    check_button_information: ctk.CTkLabel
    alteration_button: ctk.CTkButton
    data_alteration_check_button: ctk.CTkSwitch
    value_alteration_check_button: ctk.CTkSwitch

    conta: Conta
    control_var: int

    def __init__(self):
        # MAIN WINDOW
        self.main_window = ctk.CTk()
        # ctk.CTk.iconbitmap(main_window, r'Resources/icon.ico')
        self.main_window.geometry('300x260')
        self.main_window.title('Alterador de Guias TISS')
        self.main_window.eval('tk::PlaceWindow . center')
        self.main_window.maxsize(300, 260)

        # MAIN FRAME
        self.frame = ctk.CTkFrame(self.main_window)
        self.frame.pack(side='left', fill='both', padx=10, pady=10, expand=True)

        # DEFAULT BUTTON
        self.open_plan_button = ctk.CTkButton(self.frame, text='Abrir planilha')
        self.open_plan_button.pack(side='bottom', pady=5, padx=5)

        # RELATIVE BUTTONS
        self.generateHashAndSave_button = ctk.CTkButton(self.frame, text='Gerar hash')
        self.generateHashAndSave_button.pack(side='bottom', pady=5, padx=5)

        self.botao_carregar_guia = ctk.CTkButton(self.frame, text='Carregar Guia',
                                                 command=lambda: self.carregarGuia())
        self.botao_carregar_guia.pack(side='bottom', pady=5, padx=5)

        # BUTTONS AFTER GUIDE CHOOSE
        # cancel_button = ctk.CTkButton(frame, text='Cancelar')
        # cancel_button.pack(side='bottom', pady=5, padx=5)

        self.check_button_information = ctk.CTkLabel(self.frame, text='Escolha os modos de alteração:')
        self.check_button_information.pack(side='top', pady=5, padx=5)

        self.alteration_button = ctk.CTkButton(self.frame, text='Realizar alterações',
                                               command=lambda: self.realizarAlteracoes())
        self.alteration_button.pack(side='bottom', pady=5, padx=5)

        self.data_alteration_check_button = ctk.CTkSwitch(self.frame, text='Alteração de dados', text_color='white')
        self.data_alteration_check_button.pack(pady=10, padx=5)

        self.value_alteration_check_button = ctk.CTkSwitch(self.frame, text='Alteração de valor',
                                                           text_color='white')
        self.value_alteration_check_button.pack(side='top', padx=5, pady=10)

    # DESTROY RELATIVE BUTTONS
    def destroy(self):
        self.generateHashAndSave_button.destroy()
        self.botao_carregar_guia.destroy()

    def createRelativeButtons(self):
        global generateHashAndSave_button, chooseGuide_button

        generateHashAndSave_button = ctk.CTkButton(self.frame, text='Gerar hash', command=lambda: print(1))
        generateHashAndSave_button.pack(side='bottom', pady=5, padx=5)

        chooseGuide_button = ctk.CTkButton(self.frame, text='Carregar Guia', command=lambda: print(1))
        chooseGuide_button.pack(side='bottom', pady=5, padx=5)

    def tipoDeAlteracao(self):
        altera_dados = self.data_alteration_check_button.get()
        altera_valores = self.value_alteration_check_button.get()
        if altera_dados == 1:
            altera_dados = True
        else:
            altera_dados = False

        if altera_valores == 1:
            altera_valores = True
        else:
            altera_valores = False

        return altera_dados, altera_valores

    def carregarGuia(self):
        self.conta = carregarGuia()

    def realizarAlteracoes(self):
        altera_dados, altera_valores = self.tipoDeAlteracao()

        if altera_dados == True:
            alteraDados(self.conta)

        if altera_valores == True:
            alteraValores(self.conta)

        if variavel_de_controle > 0:
            for button in (self.alteration_button, self.value_alteration_check_button,
                           self.data_alteration_check_button, self.check_button_information):
                button.destroy()

    def salvarGuia(self):
        self.conta.salvarConta()

    def cancelAlteration(self):
        # REDEFINE BUTTONS
        if 'control_var' not in globals():
            for button in (
                    self.alteration_button, self.cancel_button, self.data_alteration_check_button,
                    self.value_alteration_check_button,
                    self.check_button_information):
                button.destroy()

        elif self.control_var > 0:
            for button in (self.saveGuide_button, self.cancel_button):
                button.destroy()

    def getTabelaDados(self):
        return self.tabela_de_dados.values

    def getTabelaValores(self):
        return self.tabela_de_valores.values


def foiAlterado():
    global control_var
    control_var += 1


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
    global numero_guia
    numero_guia = linha[0]
    codigo_procedimento = linha[1]
    valor_unitario = linha[2]
    novo_valor_unitario = linha[3]

    return numero_guia, codigo_procedimento, valor_unitario, novo_valor_unitario


def carregarGuia():
    file_type = (('XML files', '*.xml'), ('All files', '*.*'))
    guide_path = fd.askopenfilename(filetypes=file_type)
    if os.path.isfile(guide_path):
        conta = Conta(guide_path)
        return conta
    else:
        mb.showwarning(title='Erro', message='A guia não foi escolhida!')


def alteraDados(conta):
    global variavel_de_controle
    variavel_de_controle = 0
    tabela = Tabela()
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
                    variavel_de_controle += p.qtd_alteracoes

            if Et.iselement(guia.getDespesas()):
                for procedimento in guia.getListaDespesa():
                    p = Procedimento(procedimento, guia)
                    p.alteraCodigoProcedimentoDespesa(codigoDeProcedimento, novoCodigoDeProcedimento)
                    p.alteraCodigoDeDespesa(codigoDeDesepsa, novoCodigoDeDespesa)
                    p.alteraCodigoDeTabela(tipoDeTabela, novoTipoDeTabela)
                    p.alteraUnidadeDeMedida(unidadeDeMedida, novoUnidadeDeMedida)
                    variavel_de_controle += p.qtd_alteracoes


def alteraValores(conta):
    global variavel_de_controle
    variavel_de_controle = 0
    tabela = Tabela()
    for linha in tabela.getTabelaValores():
        numero_guia, codigoDeProcedimento, valor, novoValor = setLinhaAlteracaoDeValores(linha)

        for item in conta.guias:
            guia = Guia(item, codigoDeProcedimento)

            print('----------- ' + guia.getNumeroGuia() + ' -----------')
            if Et.iselement(guia.getProcedimentosExecutados()):
                for procedimento in guia.getListaProcedimento():
                    p = Procedimento(procedimento, guia)
                    p.alteraValorUnitario(valor, novoValor)
                    variavel_de_controle += p.qtd_alteracoes

            if Et.iselement(guia.getDespesas()):
                for procedimento in guia.getListaDespesa():
                    p = Procedimento(procedimento, guia)
                    p.alteraValorUnitario(valor, novoValor)
                    variavel_de_controle += p.qtd_alteracoes

