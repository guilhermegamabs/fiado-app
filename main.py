from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from db import criar_tabelas, inserir_cliente, buscar_clientes

class CadastroClienteScreen(Screen):
    def cadastrar(self):
        nome = self.ids.nome_input.text
        if nome.strip() != "":
            inserir_cliente(nome)
            self.ids.status_label.text = f"✅ Cliente '{nome}' cadastrado!"
            self.ids.nome_input.text = ""
            # Atualiza a lista de clientes na tela de lista
            app = App.get_running_app()
            app.atualizar_lista_clientes()
        else:
            self.ids.status_label.text = "❌ Nome é obrigatório."

class ListaClientesScreen(Screen):
    def atualizar(self, clientes):
        lista = [f"{cliente[1]}" for cliente in clientes]
        self.ids.rv.data = [{'text': nome} for nome in lista]

class FiadoApp(App):
    def build(self):
        criar_tabelas()
        self.sm = ScreenManager()
        self.cadastro_screen = CadastroClienteScreen(name='cadastro')
        self.lista_screen = ListaClientesScreen(name='lista')
        self.sm.add_widget(self.cadastro_screen)
        self.sm.add_widget(self.lista_screen)
        return self.sm

    def atualizar_lista_clientes(self):
        clientes = buscar_clientes()
        self.lista_screen.atualizar(clientes)

    def mostrar_lista(self):
        self.atualizar_lista_clientes()
        self.sm.current = 'lista'

    def mostrar_cadastro(self):
        self.sm.current = 'cadastro'


if __name__ == '__main__':
    FiadoApp().run()
