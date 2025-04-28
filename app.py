from extensions import Terminal
from components import Botao

def escrever_hello_world():
    print('Hello World')

def criar_saudacao(mensagem:str) -> str:
    def saudacao(nome:str) -> str:
        print(f'{mensagem}, {nome}')
    return saudacao


def main():
    botao = Botao()
    bom_dia_func = criar_saudacao("Bom dia")
    boa_noite_func = criar_saudacao("Boa noite")
    
    botao.Click.subscribe(escrever_hello_world)
    botao.Click.subscribe(bom_dia_func)
    botao.Click.subscribe(boa_noite_func)

    botao.clicar("Samuel")
    botao.clicar("Kelvin")
    botao.clicar("Lucas")
    botao.clicar("Caio")
    botao.clicar("Joanderson")
    botao.clicar("Pepê")
    botao.clicar("Neném")

if __name__ == '__main__':
    main()