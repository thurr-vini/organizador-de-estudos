import sqlite3
import os
from colorama import Fore, Style, init

init(autoreset=True)

BANCO_DADOS = "historico_estudos.db"

# --- BLOCO DE FUNÇÕES ---

def criar_banco():
    # Conexão do arquivo do banco
    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()

    # Criando a tabela usando comandos SQL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estudos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            materia TEXT NOT NULL,
            minutos INTEGER NOT NULL,
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conexao.commit()
    conexao.close()

def exibir_menu():
    """Mostra as opções e retorna a escolha da opção"""
    # Cabeçalho
    print("\n" + Fore.CYAN + "="*30)
    print(Fore.YELLOW + Style.BRIGHT + "--- ORGANIZADOR DE ESTUDOS ---")
    print(Fore.CYAN + "="*30)

    # Menu
    print("1. Registrar Novo Estudo")
    print("2. Editar um Registro Específico")
    print("3. Ver Histórico de Estudos")
    print("4. Limpar Histórico de Estudos")
    print("5. Excluir um Registro Específico")
    print("6. Gerar Relatório")
    print(Fore.RED + "0. Sair do Programa")
    escolha = input("\nEscolha uma opção: ")
    print(Fore.CYAN + "="*30)
    return escolha

def salvar_estudo(materia, minutos):
    """Calcula as horas, salva no arquivo e dá o feedback."""
    try:
        print("\nCategorias: [1] Teoria | [2] Prática | [3] Revisão")
        categorias_opcoes = input("Escolha uma categoria: ")
        categorias = {"1": "Teoria", "2": "Prática", "3": "Revisão"}
        categoria = categorias.get(categorias_opcoes, "Outros") # Se o usuário digitar algo fora de 1, 2 ou 3, vira "Outros"

        # Conexão com o banco de dados
        conexao = sqlite3.connect(BANCO_DADOS)
        cursor = conexao.cursor()

        cursor.execute("INSERT INTO estudos (categoria, materia, minutos) VALUES (?, ?, ?)",
                       (categoria, materia, minutos))

        conexao.commit()
        conexao.close()

        print(Fore.GREEN + Style.BRIGHT + "\n[OK] Salvo com sucesso!")
        return True

    except ValueError:
        print(Fore.RED + "\n[ERRO] Por favor, digite apenas números para o tempo!")
        return False

def editar_estudo():
    id_item = input("\nDigite o ID do item que deseja editar (Você pode localizar na opção 'Ver histórico de Estudo:')\n")

    nova_materia = input("Nome da Matéria:\n")
    novo_tempo = input("Quanto tempo?:\n")

    print("Categorias: [1] Teoria | [2] Prática | [3] Revisão")
    categorias_opcoes = input("Escolha uma categoria: ")
    categorias = {"1": "Teoria", "2": "Prática", "3": "Revisão"}
    nova_categoria = categorias.get(categorias_opcoes, "Outros")

    try:
        novo_tempo_int = int(novo_tempo)

        conexao = sqlite3.connect(BANCO_DADOS)
        cursor = conexao.cursor()

        sql = """
            UPDATE estudos
            SET categoria = ?, materia = ?, minutos = ?
            WHERE id = ?
            """

        cursor.execute(sql, (nova_categoria, nova_materia, novo_tempo_int, id_item))

        if cursor.rowcount > 0:
            conexao.commit()
            print(Fore.GREEN + Style.BRIGHT + f"\n[OK] Registro ID {id_item} atualizado com sucesso!")
        else:
            print(Fore.RED + "\n[ERRO] ID não encontrado. Nenhuma alteração realizada.")

        conexao.close()

    except ValueError:
        print(Fore.RED + "\n[ERRO] O tempo precisar ser um número inteiro!")
    
def dar_incentivo(minutos):
        """Recebe o tempo e dá um incentivo baseado no tempo gasto."""
        minutos_int = int(minutos)
        horas = minutos_int / 60
        if horas < 1:
            print(Fore.GREEN + "Dica: Bom começo! Amanhã tente focar um pouquinho mais. Constância é tudo!")

        elif 1 <= horas < 3:
            print(Fore.GREEN + "Dica: Boa! Esse é o ritmo certo para quem quer aquela vaga de estágio!")

        elif horas > 3:
            print(Fore.GREEN + "Dica: Excelente! Você estudou acima do nível comum, parabéns!")

def mostrar_historico():
    """Exibe o histórico completo dos estudos registrados, se existir."""
    # Cabeçalho
    print("\n" + Fore.CYAN + "="*30)
    print(Fore.BLUE + Style.BRIGHT + "--- SEU HISTÓRICO DE ESTUDOS ---")
    print(Fore.CYAN + "="*30)

    # Verificando se o arquivo existe
    if os.path.exists(BANCO_DADOS):
        conexao = sqlite3.connect(BANCO_DADOS)
        cursor = conexao.cursor()

        cursor.execute("SELECT id, categoria, materia, minutos, data_registro FROM estudos")
        linhas = cursor.fetchall()

        if not linhas:
            print("Você ainda não registrou nenhum estudo.")

        else:
            for linha in linhas:
                print(f"ID: {linha[0]} | Cat: {linha[1]:<8} | Matéria: {linha[2]:<10} | Tempo: {linha[3]}min | Data: {linha[4]}")
        
        conexao.close()
    else:
        print("Dados não encontrado")

def limpar_historico():
    """Remove o arquivo de histórico se ele existir."""
    if os.path.exists(BANCO_DADOS):
        confirmar = input(Fore.YELLOW + "Tem certeza que deseja apagar TODOS os registros? (S/N):\n")
        
        if confirmar.lower() == "s":
            try: 
                conexao = sqlite3.connect(BANCO_DADOS)
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM estudos")
                print(Fore.MAGENTA +"\n[SUCESSO] Histórico deletado!")

                conexao.commit()
                conexao.close()

                print(Fore.MAGENTA + Style.BRIGHT + "\n[SUCESSO] Todos os registros foram apagados!")
            except sqlite3.Error as e:
                print(Fore.RED + f"\n[ERRO] Erro ao acessar o banco: {e}")
        else:
            print(Fore.LIGHTGREEN_EX + "\n[CANCELADO] O Histórico foi mantido.")

    else:
        print(Fore.RED + "\n[ERRO] Não existe nenhum histórico para apagar.")

def deletar_item():
    id_item = input("\nDigite o ID do estudo que deseja excluir (Você pode localizar na opção 'Ver histórico de Estudo:')\n")

    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()

    # Localizando o item que será excuído
    cursor.execute("DELETE FROM estudos WHERE id = ?", (id_item,))

    if cursor.rowcount > 0:
        print(Fore.GREEN + f"\n[OK] Registro ID {id_item} removido com sucesso!")

    else:
        print(Fore.RED + "\n[ERRO] ID não encontrado.")

    conexao.commit()
    conexao.close()

def gerar_relatorio():
    """Lê o histórico e gera estatísticas."""
    print("\n" + Fore.CYAN + "="*35)
    print(Fore.BLUE + Style.BRIGHT + "      RELATÓRIO DE ESTUDOS")
    print(Fore.CYAN + "="*35)

    conexao = sqlite3.connect(BANCO_DADOS)
    cursor = conexao.cursor()

    # Somando os minutos agrupando por categoria
    cursor.execute("SELECT categoria, SUM(minutos) FROM estudos GROUP BY categoria")
    resultados = cursor.fetchall()

    if not resultados:
        print(Fore.YELLOW + "Nenhum dado encontrado")
    else:
        tempo_total = 0
        for categoria, soma_minutos in resultados:
            horas = soma_minutos / 60
            tempo_total += soma_minutos
            print(f"{Fore.WHITE}{categoria:<8}: {Fore.CYAN}{soma_minutos} min ({horas:.2f}h)")

        print(Fore.CYAN + "-" * 35)
        print(Fore.GREEN + Style.BRIGHT + f"TOTAL GERAL: {tempo_total} min ({tempo_total/60:.2f}h)")

    conexao.close()
    print(Fore.CYAN + "=" * 35)

# --- PROGRAMA PRINCIPAL ---
criar_banco()

while True:
    opcao = exibir_menu() # Exibe o cabeçalho com o menu e retorna o valor da opção escolhida

    # Opção 1: Registrar Novo Estudo
    if opcao == "1":
        # Coletor de dados
        materia_input = input("Que matéria você estudou hoje?\n")
        tempo_input = input("Quanto tempo você estudou(em minutos)?\n")

        # Exibir dica de incentivo apenas se a função salvar_estudo() retornar True
        if salvar_estudo(materia_input, tempo_input):
            dar_incentivo(tempo_input)  

    elif opcao == "2":
        editar_estudo()

    elif opcao == "3":
        mostrar_historico()

    elif opcao == "4":
        limpar_historico()

    elif opcao == "5":
        deletar_item()

    elif opcao == "6":
        gerar_relatorio()

    elif opcao == "0":
        print(Fore.YELLOW + "Saindo do programa...")
        break

    else:
        print("Opção Inválida, tente novamente")
