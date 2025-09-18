import pandas as pd
import os

def listar_colunas_planilha():
    """
    Lê uma planilha .xlsb e lista as colunas de abas específicas.
    """
    # Caminho para o arquivo, baseado na estrutura do seu projeto
    file_path = os.path.join('data', 'raw', 'Evolução.xlsb')
    
    # Nomes das abas que você quer inspecionar
    abas = ['BD 2023', 'FROTA', 'Filiais']

    print(f"🔍 Lendo o arquivo: '{file_path}'...\n")

    try:
        # Lê todas as abas de uma vez, o que é mais eficiente
        dfs = pd.read_excel(file_path, sheet_name=abas, engine='pyxlsb')
        
        # Itera sobre cada aba carregada e imprime suas colunas
        for nome_aba, df in dfs.items():
            print("-------------------------------------------")
            print(f"📊 Colunas da Aba: '{nome_aba}'")
            print("-------------------------------------------")
            
            if df.empty:
                print("-> Esta aba está vazia ou não pôde ser lida.")
            else:
                # Imprime uma coluna por linha para facilitar a leitura
                for coluna in df.columns:
                    print(f"  - {coluna}")
            
            print("\n") # Adiciona um espaço para separar as listas

    except FileNotFoundError:
        print(f"❌ ERRO: Arquivo não encontrado!")
        print(f"Verifique se o caminho '{file_path}' está correto e o arquivo existe.")
    except ValueError as e:
        print(f"❌ ERRO: Uma ou mais abas não foram encontradas no arquivo.")
        print(f"Verifique se os nomes {abas} estão corretos. Detalhe: {e}")
    except Exception as e:
        print(f"❌ Ocorreu um erro inesperado: {e}")

# Executa a função principal
if __name__ == "__main__":
    listar_colunas_planilha()