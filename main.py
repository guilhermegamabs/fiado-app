from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from datetime import datetime

from db import criar_tabelas, inserir_cliente, buscar_clientes, inserir_fiado, buscar_fiados


class CadastroClienteScreen(Screen):
    def cadastrar(self):
        nome = self.ids.nome_input.text
        if nome.strip() != "":
            inserir_cliente(nome)
            self.ids.status_label.text = f"✅ Cliente '{nome}' cadastrado!"
            self.ids.nome_input.text = ""
            app = App.get_running_app()
            app.atualizar_lista_clientes()
        else:
            self.ids.status_label.text = "❌ Nome é obrigatório."


class ListaClientesScreen(Screen):
    def atualizar(self, clientes):
        lista = [f"{cliente[1]}" for cliente in clientes]
        self.ids.rv.data = [{'text': nome} for nome in lista]


class RegistroFiadoScreen(Screen):
    def on_pre_enter(self, *args):
        Clock.schedule_once(self.atualizar_spinner)

    def atualizar_spinner(self, dt):
        clientes = buscar_clientes()
        clientes_nomes = [c[1] for c in clientes]
        if clientes_nomes:
            self.ids.spinner_cliente.values = clientes_nomes
            self.ids.spinner_cliente.text = clientes_nomes[0]
        else:
            self.ids.spinner_cliente.values = []
            self.ids.spinner_cliente.text = "Nenhum cliente cadastrado"

    def registrar(self):
        cliente_nome = self.ids.spinner_cliente.text
        descricao = self.ids.descricao.text.strip()
        valor_text = self.ids.valor.text.strip()

        if not cliente_nome or cliente_nome == "Nenhum cliente cadastrado":
            self.ids.status_label.text = "❌ Selecione um cliente."
            return
        if not descricao:
            self.ids.status_label.text = "❌ Descrição é obrigatória."
            return
        try:
            valor = float(valor_text)
            if valor <= 0:
                raise ValueError
        except ValueError:
            self.ids.status_label.text = "❌ Valor inválido."
            return

        clientes = buscar_clientes()
        cliente_dict = {c[1]: c[0] for c in clientes}
        cliente_id = cliente_dict.get(cliente_nome)

        if cliente_id is None:
            self.ids.status_label.text = "❌ Cliente não encontrado."
            return

        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        inserir_fiado(cliente_id, descricao, valor, data)
        self.ids.status_label.text = f"✅ Fiado registrado para {cliente_nome}!"
        self.ids.descricao.text = ""
        self.ids.valor.text = ""


class ListaFiadosScreen(Screen):
    def atualizar(self, fiados):
        dados = [f"{f[1]} - {f[2]} - R$ {f[3]:.2f} - {f[4]}" for f in fiados]
        self.ids.rv.data = [{'text': item} for item in dados]


class FiadoApp(App):
    def build(self):
        criar_tabelas()
        self.sm = ScreenManager()

        self.cadastro_screen = CadastroClienteScreen(name='cadastro')
        self.lista_screen = ListaClientesScreen(name='lista')
        self.registro_fiado_screen = RegistroFiadoScreen(name='registro_fiado')
        self.lista_fiados_screen = ListaFiadosScreen(name='lista_fiados')

        self.sm.add_widget(self.cadastro_screen)
        self.sm.add_widget(self.lista_screen)
        self.sm.add_widget(self.registro_fiado_screen)
        self.sm.add_widget(self.lista_fiados_screen)

        return self.sm

    def atualizar_lista_clientes(self):
        clientes = buscar_clientes()
        self.lista_screen.atualizar(clientes)

    def mostrar_lista(self):
        self.atualizar_lista_clientes()
        self.sm.current = 'lista'

    def mostrar_cadastro(self):
        self.sm.current = 'cadastro'

    def mostrar_registro_fiado(self):
        self.sm.current = 'registro_fiado'

    def mostrar_lista_fiados(self):
        fiados = buscar_fiados()
        self.lista_fiados_screen.atualizar(fiados)
        self.sm.current = 'lista_fiados'


if __name__ == '__main__':
    FiadoApp().run()
