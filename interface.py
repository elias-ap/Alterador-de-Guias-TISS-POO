from poo import carregarGuia as cG, alteraDados, alteraValores, Conta



class Interface:
    # GUI COLOR CONFIG
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('green')

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

        self.botao_carregar_guia = ctk.CTkButton(self.frame, text='Carregar Guia', command=lambda: self.carregarGuia())
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

        self.value_alteration_check_button = ctk.CTkSwitch(self.frame, text='Alteração de valor', text_color='white')
        self.value_alteration_check_button.pack(side='top', padx=5, pady=10)

    # DESTROY RELATIVE BUTTONS
    def destroy(self):
        self.generateHashAndSave_button.destroy()
        self.botao_carregar_guia.destroy()

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
        self.conta = cG()

    def realizarAlteracoes(self):
        altera_dados, altera_valores = self.tipoDeAlteracao()

        if altera_dados == True:
            alteraDados(self.conta)

        if altera_valores == True:
            alteraValores(self.conta)

    def salvarGuia(self):
        self.conta.salvarConta()

    def cancelAlteration(self):
        # REDEFINE BUTTONS
        if 'control_var' not in globals():
            for button in (
            self.alteration_button, self.cancel_button, self.data_alteration_check_button, self.value_alteration_check_button,
            self.check_button_information):
                button.destroy()

        elif self.control_var > 0:
            for button in (self.saveGuide_button, self.cancel_button):
                button.destroy()


interface = Interface()
interface.main_window.mainloop()
