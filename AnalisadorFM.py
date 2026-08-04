import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

def gerar_grafico():
    arquivo = filedialog.askopenfilename(title="Selecione o CSV", filetypes=[("CSV", "*.csv")])
    if not arquivo: return

    try:
        # Lê o CSV (o utf-8-sig ignora o BOM se houver)
        df = pd.read_csv(arquivo, sep=',', encoding='utf-8-sig')
        
        # Mapeamento para colunas individuais
        mapa = {
            "1": "Boca_Vertical",
            "2": "Boca_Horizontal",
            "3": "Olho_Esquerdo",
            "4": "Olho_Direito",
            "5": "Sobrancelha_Esquerda",
            "6": "Sobrancelha_Direita"
        }
        
        opcao = var_opcao.get()
        
        # Opção 7: "Tudo" (6 subgráficos 3x2)
        if opcao == "7":
            fig, axs = plt.subplots(3, 2, figsize=(9.8, 7), sharex=True)
            
            # Linha 1: Boca e Sorriso
            axs[0, 0].plot(df['Boca_Vertical'], color='red'); axs[0, 0].set_title('Abertura Boca')
            axs[0, 1].plot(df['Boca_Horizontal'], color='green'); axs[0, 1].set_title('Largura Sorriso')
            
            # Linha 2: Olhos (Corrigido: título alinhado ao gráfico)
            axs[1, 0].plot(df['Olho_Esquerdo'], color='blue'); axs[1, 0].set_title('Olho Esquerdo')
            axs[1, 1].plot(df['Olho_Direito'], color='cyan'); axs[1, 1].set_title('Olho Direito')
            
            # Linha 3: Sobrancelhas
            axs[2, 0].plot(df['Sobrancelha_Esquerda'], color='magenta'); axs[2, 0].set_title('Sobrancelha Esquerda')
            axs[2, 1].plot(df['Sobrancelha_Direita'], color='purple'); axs[2, 1].set_title('Sobrancelha Direita')
            
            plt.tight_layout()
            

        # Opção 8: Ambos os Olhos (Sobrepostos)
        elif opcao == "8":
            plt.figure(figsize=(10, 5))
            plt.plot(df['Olho_Esquerdo'], color='blue', label='Olho Esquerdo')
            plt.plot(df['Olho_Direito'], color='cyan', label='Olho Direito')
            plt.title("Comparativo: Ambos os Olhos")
            plt.legend()
            plt.grid(True, alpha=0.3)
            

        # Opção 9: Ambas as Sobrancelhas (Sobrepostas)
        elif opcao == "9":
            plt.figure(figsize=(10, 5))
            plt.plot(df['Sobrancelha_Esquerda'], color='magenta', label='Sobrancelha Esquerda')
            plt.plot(df['Sobrancelha_Direita'], color='purple', label='Sobrancelha Direita')
            plt.title("Comparativo: Ambas as Sobrancelhas")
            plt.legend()
            plt.grid(True, alpha=0.3)
            

        # Opções 1 a 6: Individuais
        else:
            coluna_alvo = mapa[opcao]
            if coluna_alvo in df.columns:
                plt.figure(figsize=(10, 5))
                plt.plot(df[coluna_alvo], label=coluna_alvo.replace('_', ' '))
                plt.title(f"Análise: {coluna_alvo.replace('_', ' ')}")
                plt.legend()
                plt.grid(True, alpha=0.3)
                
            else:
                messagebox.showerror("Erro", f"Coluna '{coluna_alvo}' não encontrada!\nColunas no arquivo: {list(df.columns)}")
                return

        plt.show()

    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao processar arquivo: {e}")

# Interface
root = tk.Tk()
root.title("Analisador Face Metrics")
root.geometry("400x550")

var_opcao = tk.StringVar(value="7")
tk.Label(root, text="Escolha a visualização dos dados:", font=("Arial", 11, "bold")).pack(pady=15)

# Opções de rádio atualizadas com as novas funcionalidades
opcoes = [
    ("Abertura da Boca", "1"), 
    ("Largura do Sorriso", "2"), 
    ("Olho Esquerdo", "3"), 
    ("Olho Direito", "4"), 
    ("Ambos os Olhos (Sobrepostos)", "8"),
    ("Sobrancelha Esquerda", "5"), 
    ("Sobrancelha Direita", "6"), 
    ("Ambas as Sobrancelhas (Sobrepostas)", "9"),
    ("Visualizar Tudo (Lado a Lado)", "7")
]

for t, v in opcoes:
    tk.Radiobutton(root, text=t, variable=var_opcao, value=v, font=("Arial", 10)).pack(anchor=tk.W, padx=60, pady=2)

tk.Button(root, text="Selecionar Arquivo CSV", command=gerar_grafico, bg="#2b5ce7", fg="white", font=("Arial", 10, "bold"), height=2).pack(pady=30)

root.mainloop()