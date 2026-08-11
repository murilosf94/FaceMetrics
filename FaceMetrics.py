import cv2
import mediapipe as mp
import socket
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import os
import sys

#detectar cameras
def listar_cameras():
    arr = []
    for i in range(4): #pega os primeiros 4 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret: arr.append(i)
            cap.release()
    return arr

#configuração UDP para Unity
UDP_IP = "127.0.0.1"
UDP_PORT = 5052
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class MenuInicial: #tudo que está aqui faz parte do menu
    def __init__(self): #inicializa a janela do menu
        self.root = tk.Tk() #cria a janela principal
        self.root.title("Configuração do FaceMetrics") 
        self.root.state('zoomed') #tela cheia
        
        #nome do paciente
        tk.Label(self.root, text="Nome do Paciente:", font=("Arial", 10, "bold")).pack(pady=5)
        self.entry_nome = tk.Entry(self.root, width=30)
        self.entry_nome.pack(pady=5)
        
        #seleciona a camera
        tk.Label(self.root, text="Selecione a Câmera:", font=("Arial", 10, "bold")).pack(pady=5)
        self.cameras_disponiveis = listar_cameras()
        if not self.cameras_disponiveis: self.cameras_disponiveis = [0]
        
        self.camera_selecionada = tk.IntVar(value=self.cameras_disponiveis[0])
        self.menu_camera = tk.OptionMenu(self.root, self.camera_selecionada, *self.cameras_disponiveis, command=self.trocar_camera) #cria o menu de seleção de câmera, se mudo no menu ele avisa ao trocar_camera para atualizar o preview
        self.menu_camera.pack(pady=5)

        #preview da camera
        self.canvas_preview = tk.Canvas(self.root, width=400, height=300, bg="black")
        self.canvas_preview.pack(pady=10)
        
        #CONTAINER PRINCIPAL PARA AS OPÇÕES LADO A LADO
        frame_opcoes_main = tk.Frame(self.root)
        frame_opcoes_main.pack(pady=10, fill=tk.X, padx=20) #esticar horizontalmente até preencher a tela, mas mantendo margem lateral de 20px

        #ESQUERDA: opções do gráfico
        frame_radio = tk.LabelFrame(frame_opcoes_main, text="O que analisar no gráfico?", font=("Arial", 10, "bold"))
        frame_radio.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.opcao = tk.StringVar(value="7")
        opcoes = [
            ("Boca", "1"), ("Sorriso", "2"), 
            ("Olho Esq.", "3"), ("Olho Dir.", "4"), 
            ("Ambos os Olhos (Sobrepostos)", "8"),
            ("Sobr. Esq.", "5"), ("Sobr. Dir.", "6"), 
            ("Ambas as Sobr. (Sobrepostas)", "9"),
            ("Tudo (Lado a Lado)", "7")
        ]
        
        for text, mode in opcoes:
            tk.Radiobutton(frame_radio, text=text, variable=self.opcao, value=mode).pack(anchor=tk.W, padx=5)

        #DIREITA: valores Esperados
        frame_esperados = tk.LabelFrame(frame_opcoes_main, text="Movimento Esperado (Opcional)", font=("Arial", 10, "bold"))
        frame_esperados.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.entries_esperados = {}
        colunas_nomes = [
            ('Boca_Vertical', 'Boca Vertical'), ('Boca_Horizontal', 'Sorriso'),
            ('Olho_Esquerdo', 'Olho Esq.'), ('Olho_Direito', 'Olho Dir.'),
            ('Sobrancelha_Esquerda', 'Sobr. Esq.'), ('Sobrancelha_Direita', 'Sobr. Dir.')
        ]
        
        for i, (col, nome) in enumerate(colunas_nomes):
            tk.Label(frame_esperados, text=nome).grid(row=i, column=0, sticky=tk.E, padx=5, pady=5)
            entry = tk.Entry(frame_esperados, width=10)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries_esperados[col] = entry

        #botão para iniciar a captura
        tk.Button(self.root, text="INICIAR CAPTURA", command=self.confirmar, bg="green", fg="white", font=("Arial", 12, "bold")).pack(pady=15)
        
        #inicia a captura da camera selecionada
        self.cap_preview = cv2.VideoCapture(self.camera_selecionada.get())
        self.dados_confirmados = False
        self.atualizar_preview()
        
        #fecha a janela corretamente
        self.root.protocol("WM_DELETE_WINDOW", self.fechar)
        self.root.mainloop()

    #funcao para trocar a camera
    def trocar_camera(self, escolha):
        self.cap_preview.release()
        self.cap_preview = cv2.VideoCapture(int(escolha))

    #funcao para atualizar o preview da camera
    def atualizar_preview(self):
        ret, frame = self.cap_preview.read()
        if ret:
            frame = cv2.resize(frame, (400, 300))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)
            self.canvas_preview.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.canvas_preview.image = img_tk
        self.root.after(15, self.atualizar_preview)

    #popup de confirmação dos dados
    def confirmar(self):
        if not self.entry_nome.get().strip():
            messagebox.showwarning("Aviso", "Digite o nome do paciente.")
            return
        self.nome_paciente = self.entry_nome.get().strip().replace(" ", "_")
        self.opcao_selecionada = self.opcao.get()
        self.camera_index = self.camera_selecionada.get()
        
        #SALVA OS VALORES ESPERADOS
        self.valores_esperados = {}
        for col, entry in self.entries_esperados.items():
            val = entry.get().strip().replace(',', '.')
            if val:
                try:
                    self.valores_esperados[col] = float(val)
                except ValueError:
                    messagebox.showwarning("Aviso", f"Valor inválido em {col}. Ignorando.")
        
        self.dados_confirmados = True
        self.fechar()

    #fecha a janela corretamente
    def fechar(self):
        self.cap_preview.release()
        self.root.destroy()
        
#inicia o menu
menu = MenuInicial()
if not menu.dados_confirmados: sys.exit()

#configuração para salvar os dados e iniciar mediapipe
if not os.path.exists("analises"): os.makedirs("analises")
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

#LANDMARKS
TOPO, FUNDO = 10, 152
NARIZ = 1
LABIO_CIMA, LABIO_BAIXO = 13, 14
CANTO_ESQ_BOCA, CANTO_DIR_BOCA = 61, 291
OLHOESQ_CIMA, OLHOESQ_BAIXO = 159, 145 
OLHODIR_CIMA, OLHODIR_BAIXO = 386, 374 
SOBESQ_TOPO, SOBESQ_REF = 107, 243 
SOBDIR_TOPO, SOBDIR_REF = 336, 463 

#dados para análise
dados_analise = []
webcam = cv2.VideoCapture(menu.camera_index)

#captura dos dados faciais
with mp_face_mesh.FaceMesh(refine_landmarks=True) as face_mesh:
    while webcam.isOpened(): 
        success, image = webcam.read()
        if not success: break

        image = cv2.flip(image, 1) 
        h, w, _ = image.shape
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        reacao, status_olho, h_x, h_y = "Neutro", "Abertos", "Centro", "Centro"

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmark = face_landmarks.landmark
                face_h = abs(landmark[FUNDO].y - landmark[TOPO].y) * h #tirar o tamanho da face da pessoa

                boca_abert = round(abs(landmark[LABIO_BAIXO].y - landmark[LABIO_CIMA].y) * h / face_h, 4)
                sorriso_larg = round(abs(landmark[CANTO_DIR_BOCA].x - landmark[CANTO_ESQ_BOCA].x) * w / face_h, 4)
                olho_e = round(abs(landmark[OLHOESQ_BAIXO].y - landmark[OLHOESQ_CIMA].y) * h / face_h, 4)
                olho_d = round(abs(landmark[OLHODIR_BAIXO].y - landmark[OLHODIR_CIMA].y) * h / face_h, 4)
                sob_e = round(abs(landmark[SOBESQ_REF].y - landmark[SOBESQ_TOPO].y) * h / face_h, 4)
                sob_d = round(abs(landmark[SOBDIR_REF].y - landmark[SOBDIR_TOPO].y) * h / face_h, 4)

                if sorriso_larg > 0.35: reacao = "Feliz"
                elif sob_e > 0.18 and sob_d > 0.18: reacao = "Surpresa"
                                
                if olho_e < 0.03 and olho_d < 0.03: 
                    status_olho = "Piscando"
                else:
                    status_olho = "Abertos"
                
                direcao_x = landmark[NARIZ].x * w
                direcao_y = landmark[NARIZ].y * h
                if direcao_x < (w / 2) - 60: h_x = "Esquerda"
                elif direcao_x > (w / 2) + 60: h_x = "Direita"
                else: h_x = "Centro"
                
                if direcao_y < (h / 2) - 50: h_y = "Cima"
                elif direcao_y > (h / 2) + 50: h_y = "Baixo"
                else: h_y = "Centro"

                dados_analise.append({
                    "Timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                    "Boca_Vertical": boca_abert, "Boca_Horizontal": sorriso_larg,
                    "Olho_Esquerdo": olho_e, "Olho_Direito": olho_d,
                    "Sobrancelha_Esquerda": sob_e, "Sobrancelha_Direita": sob_d,
                    "Reacao": reacao, "Direcao": h_x
                })

                #desenho dos landmarks
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )

                sock.sendto(f"{h_x},{h_y},{reacao},{status_olho},{boca_abert}".encode(), (UDP_IP, UDP_PORT)) #envia via UDP para a unity
        
        cv2.putText(image, f"Reacao: {reacao} | Olhos: {status_olho}", (20, 70), 1, 1.6, (255, 255, 255), 2)
        cv2.putText(image, f"Gravando: {menu.nome_paciente}", (20, 35), 1, 1.6, (255, 255, 255), 2)
        
        cv2.imshow(f'FaceMetrics | Paciente: {menu.nome_paciente}', image)
        if cv2.waitKey(5) == 27: break

webcam.release()
cv2.destroyAllWindows()

#FUNÇÃO AUXILIAR PARA PINTAR A ÁREA ALVO NO GRÁFICO
def aplicar_meta_grafico(ax, col_name, y_data):
    esperado = menu.valores_esperados.get(col_name)
    if esperado is not None:
        ax.axhline(y=esperado, color='red', linestyle='--', alpha=0.8, label=f'Alvo ({esperado})')
        ax.fill_between(range(len(y_data)), y_data, esperado, where=(y_data >= esperado), color='red', alpha=0.3, label='Ultrapassou Alvo')

#GRÁFICOS
if dados_analise: 
    df = pd.DataFrame(dados_analise) 
    df.to_csv(f"analises/{menu.nome_paciente}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False) 
    
    mapa = {'1':'Boca_Vertical', '2':'Boca_Horizontal', '3':'Olho_Esquerdo', '4':'Olho_Direito', '5':'Sobrancelha_Esquerda', '6':'Sobrancelha_Direita'}

    #Opção 7: Tudo (Subplots)
    if menu.opcao_selecionada == '7':
        fig, axs = plt.subplots(3, 2, figsize=(9.8, 7))
        colunas = ['Boca_Vertical', 'Boca_Horizontal', 'Olho_Esquerdo', 'Olho_Direito', 'Sobrancelha_Esquerda', 'Sobrancelha_Direita']
        for i, col in enumerate(colunas):
            ax = axs[i//2, i%2]
            ax.plot(df[col], label='Movimento')
            aplicar_meta_grafico(ax, col, df[col]) #Aplica a meta visual
            ax.set_title(col)
            if menu.valores_esperados.get(col) is not None:
                ax.legend(loc="upper right", fontsize=8)
        plt.tight_layout()

    #Opção 8: Ambos os Olhos (Sobrepostos)
    elif menu.opcao_selecionada == '8':
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df['Olho_Esquerdo'], color='blue', label='Olho Esquerdo')
        ax.plot(df['Olho_Direito'], color='cyan', label='Olho Direito')
        aplicar_meta_grafico(ax, 'Olho_Esquerdo', df['Olho_Esquerdo'])
        aplicar_meta_grafico(ax, 'Olho_Direito', df['Olho_Direito'])
        ax.set_title("Comparativo: Ambos os Olhos")
        ax.legend()
        ax.grid(True, alpha=0.3)

    #Opção 9: Ambas as Sobrancelhas (Sobrepostas)
    elif menu.opcao_selecionada == '9':
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df['Sobrancelha_Esquerda'], color='magenta', label='Sobrancelha Esquerda')
        ax.plot(df['Sobrancelha_Direita'], color='purple', label='Sobrancelha Direita')
        aplicar_meta_grafico(ax, 'Sobrancelha_Esquerda', df['Sobrancelha_Esquerda'])
        aplicar_meta_grafico(ax, 'Sobrancelha_Direita', df['Sobrancelha_Direita'])
        ax.set_title("Comparativo: Ambas as Sobrancelhas")
        ax.legend()
        ax.grid(True, alpha=0.3)

    #Opções individuais
    else:
        fig, ax = plt.subplots(figsize=(10, 5))
        coluna = mapa[menu.opcao_selecionada]
        ax.plot(df[coluna], label='Movimento')
        aplicar_meta_grafico(ax, coluna, df[coluna])
        ax.set_title(f"Análise: {coluna.replace('_', ' ')}")
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.show()