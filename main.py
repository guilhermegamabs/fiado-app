from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from db import criar_tabelas, inserir_cliente

class CadastroClienteScreen(BoxLayout):
    def cadastrar(self):
        nome = self.ids.nome_input.text

        if nome.strip() != "":
            inserir_cliente(nome)
            self.ids.status_label.text = f"✅ Cliente '{nome}' cadastrado!"
            self.ids.nome_input.text = ""
        else:
            self.ids.status_label.text = "❌ Nome é obrigatório."

class FiadoApp(App):
    def build(self):
        criar_tabelas()
        return CadastroClienteScreen()

if __name__ == '__main__':
    FiadoApp().run()
