from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from datetime import datetime

from db import (
    criar_tabelas, inserir_cliente, buscar_clientes, inserir_fiado,
    buscar_fiados_por_cliente, registrar_pagamento
)

class CadastroClienteScreen(Screen):
    def cadastrar(self):
        nome = self.ids.nome_input.text.strip()
        if nome:
            inserir_cliente(nome)
            self.ids.status_label.text = f"✅ Cliente '{nome}' cadastrado!"
            self.ids.nome_input.text = ""
            App.get_running_app().atualizar_lista_clientes()
        else:
            self.ids.status_label.text = "❌ Nome é obrigatório."

class ListaClientesScreen(Screen):
    def atualizar(self, clientes):
        self.ids.rv.data = [{'text': nome, 'on_press': lambda x=nome: self.abrir_fiados(x)} for _, nome in clientes]

    def abrir_fiados(self, nome_cliente):
        app = App.get_running_app()
        app.mostrar_fiados_por_cliente(nome_cliente)

class RegistroFiadoScreen(Screen):
    def on_pre_enter(self):
        Clock.schedule_once(self.atualizar_spinner)

    def atualizar_spinner(self, dt):
        nomes = [c[1] for c in buscar_clientes()]
        self.ids.spinner_cliente.values = nomes
        self.ids.spinner_cliente.text = nomes[0] if nomes else "Nenhum cliente"

    def registrar(self):
        nome = self.ids.spinner_cliente.text
        descricao = self.ids.descricao.text.strip()
        valor = self.ids.valor.text.strip()

        if not nome or nome == "Nenhum cliente":
            self.ids.status_label.text = "❌ Selecione um cliente."
            return
        if not descricao or not valor:
            self.ids.status_label.text = "❌ Preencha todos os campos."
            return
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                raise ValueError
        except ValueError:
            self.ids.status_label.text = "❌ Valor inválido."
            return

        # CORREÇÃO AQUI: dicionário {nome: id}
        clientes = {nome: id for id, nome in buscar_clientes()}
        cliente_id = clientes.get(nome)
        if cliente_id is None:
            self.ids.status_label.text = "❌ Cliente não encontrado."
            return

        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        inserir_fiado(cliente_id, descricao, valor_float, data)
        self.ids.status_label.text = "✅ Fiado registrado!"
        self.ids.descricao.text = ""
        self.ids.valor.text = ""

class ListaFiadosPorClienteScreen(Screen):
    nome_cliente = ""

    def on_pre_enter(self):
        self.atualizar_dados()

    def atualizar_dados(self):
        dados, total, ultima, valor_ultimo = buscar_fiados_por_cliente(self.nome_cliente)
        self.ids.label_cliente.text = f"Fiados de: {self.nome_cliente}"
        self.ids.label_total.text = f"Total Devido: R$ {total:.2f}"
        if ultima:
            self.ids.label_ultima.text = f"Último pagamento: {ultima} (R$ {valor_ultimo:.2f})"
        else:
            self.ids.label_ultima.text = "Último pagamento: --"
        self.ids.rv.data = [{'text': f"{f[2]} - R$ {f[3]:.2f} - {f[4]}"} for f in dados]

    def registrar_pagamento(self):
        valor_pagamento = self.ids.input_pagamento.text.strip()
        if not valor_pagamento:
            return
        try:
            valor = float(valor_pagamento)
            if valor <= 0:
                self.ids.status_label.text = "❌ Valor inválido."
                return
        except ValueError:
            self.ids.status_label.text = "❌ Valor inválido."
            return

        erro = registrar_pagamento(self.nome_cliente, valor)
        if erro:
            self.ids.status_label.text = erro
        else:
            self.ids.status_label.text = "✅ Pagamento registrado!"
            self.ids.input_pagamento.text = ""
            self.atualizar_dados()

class FiadoApp(App):
    def build(self):
        criar_tabelas()
        self.sm = ScreenManager()
        self.cadastro_screen = CadastroClienteScreen(name='cadastro')
        self.lista_screen = ListaClientesScreen(name='lista')
        self.registro_fiado_screen = RegistroFiadoScreen(name='registro_fiado')
        self.fiados_cliente_screen = ListaFiadosPorClienteScreen(name='fiados_cliente')

        self.sm.add_widget(self.cadastro_screen)
        self.sm.add_widget(self.lista_screen)
        self.sm.add_widget(self.registro_fiado_screen)
        self.sm.add_widget(self.fiados_cliente_screen)
        return self.sm

    def atualizar_lista_clientes(self):
        clientes = buscar_clientes()
        self.lista_screen.atualizar(clientes)

    def mostrar_cadastro(self):
        self.sm.current = 'cadastro'

    def mostrar_lista(self):
        self.atualizar_lista_clientes()
        self.sm.current = 'lista'

    def mostrar_registro_fiado(self):
        self.sm.current = 'registro_fiado'

    def mostrar_fiados_por_cliente(self, nome):
        self.fiados_cliente_screen.nome_cliente = nome
        self.sm.current = 'fiados_cliente'

if __name__ == '__main__':
    FiadoApp().run()
