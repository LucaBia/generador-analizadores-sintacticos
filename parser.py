import tkinter as tk
from tkinter import scrolledtext as st

window = tk.Tk()
window.title("Resultado")
window.geometry("500x250")
text_area = st.ScrolledText(window, width = 60, height = 15, font = ("Times New Roman",15), foreground = "white")
text_area.grid(column = 1, row = 1, columnspan=2)
class Parser():
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]
        self.EstadoInicial()

    def update_current_token(self):
        if self.current_token_index < len(self.tokens) - 1:
            self.current_token_index += 1
            self.current_token = self.tokens[self.current_token_index]

    def EstadoInicial(self):
        while self.current_token['type'] in ['numeroToken']:
            self.Instruccion()

            if self.current_token["value"] == ";":
                self.update_current_token()

    def Instruccion(self):
        resultado = 0
        resultado = self.Expresion(resultado)
        print("Resultado: ", resultado)
        text_area.insert(tk.INSERT, f'{resultado}    ')

    def Expresion(self, resultado):
        resultado1, resultado2 = 0, 0
        resultado1 = self.Termino(resultado1)
        while self.current_token['value'] in []:
            suma = None
            if self.current_token["type"] == "suma":
                suma = float(self.current_token["value"])
                self.update_current_token()
            resultado2 = self.Termino(resultado2)
            resultado1 += resultado2
            print("Termino: ", resultado1)
        return resultado1
        print("Termino: ", resultado)

    def Termino(self, resultado):
        resultado1, resultado2 = 0, 0
        resultado1 = self.Factor(resultado1)
        while self.current_token['value'] in ['*']:

            if self.current_token["value"] == "*":
                self.update_current_token()
                resultado2 = self.Factor(resultado2)
                resultado1 *= resultado2
                print("Factor: ", resultado1)

        return resultado1
        print("Factor: ", resultado)

    def Factor(self, resultado):
        resultado1 = 0
        resultado1 = self.Numero(resultado1)
        return resultado1
        print("Numero: ", resultado)

    def Numero(self, resultado):
        numeroToken = None
        if self.current_token["type"] == "numeroToken":
            numeroToken = float(self.current_token["value"])
            self.update_current_token()
        return numeroToken
        print("Token: ", resultado)

Parser([{'type': 'numeroToken', 'value': '1'}, {'type': 'suma', 'value': 's'}, {'type': 'numeroToken', 'value': '1'}, {'type': 'final', 'value': ';'}, {'type': 'numeroToken', 'value': '2'}, {'type': 'suma', 'value': 'ss'}, {'type': 'numeroToken', 'value': '2'}, {'type': 'final', 'value': ';'}, {'type': 'numeroToken', 'value': '11'}, {'type': 'suma', 'value': 'sss'}, {'type': 'numeroToken', 'value': '4'}, {'type': 'final', 'value': ';'}, {'type': 'final', 'value': ';'}])
window.mainloop()