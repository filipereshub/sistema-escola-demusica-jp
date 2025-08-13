import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
from datetime import date, datetime
import webbrowser
#from PIL import Image, ImageTk # Comentado conforme solicitado

# --- Configuração do Banco de Dados ---
try:
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="PERES",
        database="escola_db"
    )
    cursor = conexao.cursor()
except mysql.connector.Error as err:
    messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {err}")
    exit()

# --- Funções CRUD ---
def cadastrar():
    # Verifica se os campos estão visíveis antes de tentar obter os valores
    if not show_fields.get():
        messagebox.showwarning("Campos Ocultos", "Por favor, ative os campos de preenchimento primeiro!")
        return

    nome = entry_nome.get()
    nascimento_str = entry_nascimento.get()
    sexo = entry_sexo.get()
    curso = entry_curso.get()
    data_pagamento_str = entry_data_pagamento.get()
    telefone = entry_telefone.get()

    if nome and nascimento_str and sexo and curso and data_pagamento_str and telefone:
        try:
            nascimento_date = datetime.strptime(nascimento_str, '%Y-%m-%d').date()
            data_pagamento_date = datetime.strptime(data_pagamento_str, '%Y-%m-%d').date()

            sql = "INSERT INTO alunos (nome_completo, nascimento, sexo, curso, data_pagamento, telefone) VALUES (%s, %s, %s, %s, %s, %s)"
            dados = (nome, nascimento_date, sexo, curso, data_pagamento_date, telefone)
            cursor.execute(sql, dados)
            conexao.commit()
            messagebox.showinfo("Sucesso", "Aluno cadastrado!")
            limpar_campos()
        except ValueError:
            messagebox.showerror("Erro de Data", "Formato de data inválido. Use AAAA-MM-DD.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao cadastrar: {e}")
    else:
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos!")

def listar():
    try:
        cursor.execute("SELECT id, nome_completo, nascimento, sexo, curso, data_pagamento, telefone FROM alunos")
        resultado = cursor.fetchall()

        if resultado:
            texto = "ID | Nome Completo | Nascimento | Sexo | Curso | Pagamento | Telefone\n"
            texto += "-" * 90 + "\n"
            for linha in resultado:
                id_aluno, nome_completo, nascimento, sexo, curso, data_pagamento, telefone = linha
                
                # CORREÇÃO AQUI: Verifica se a data não é None antes de formatar
                nasc_str = nascimento.strftime('%Y-%m-%d') if isinstance(nascimento, date) and nascimento is not None else ""
                pag_str = data_pagamento.strftime('%Y-%m-%d') if isinstance(data_pagamento, date) and data_pagamento is not None else ""
                
                # NOVO: Garante que sexo, curso e telefone não sejam None antes de formatar
                sexo_str = str(sexo) if sexo is not None else ""
                curso_str = str(curso) if curso is not None else ""
                telefone_str = str(telefone) if telefone is not None else ""
                
                # Ajuste no f-string para incluir o sexo e garantir que o número de colunas bate com o cabeçalho
                # A linha original tinha 6 variáveis mas o cabeçalho tinha 5
                # texto += f"{linha[0]:<3} | {linha[1]:<13} | {nasc_str:<10} | {linha[3]:<4} | {linha[4]:<5} | {pag_str:<10}\n"
                # A correção abaixo considera 7 variáveis (ID, Nome, Nascimento, Sexo, Curso, Pagamento, Telefone)
                texto += f"{id_aluno:<3} | {nome_completo:<13} | {nasc_str:<10} | {sexo_str:<4} | {curso_str:<5} | {pag_str:<10} | {telefone_str:<10}\n"
            messagebox.showinfo("Meus Alunos", texto)
        else:
            messagebox.showinfo("Meus Alunos", "Nenhum aluno cadastrado.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao listar: {e}")

def atualizar():
    # Verifica se os campos estão visíveis antes de tentar obter os valores
    if not show_fields.get():
        messagebox.showwarning("Campos Ocultos", "Por favor, ative os campos de preenchimento primeiro!")
        return

    id_aluno = entry_id.get()
    novo_curso = entry_curso.get()
    novo_telefone = entry_telefone.get()
    novo_nascimento_str = entry_nascimento.get()
    nova_data_pagamento_str = entry_data_pagamento.get()

    if id_aluno:
        try:
            sql_parts = []
            dados = []

            if novo_curso:
                sql_parts.append("curso = %s")
                dados.append(novo_curso)
            if novo_telefone:
                sql_parts.append("telefone = %s")
                dados.append(novo_telefone)
            if novo_nascimento_str:
                novo_nascimento_date = datetime.strptime(novo_nascimento_str, '%Y-%m-%d').date()
                sql_parts.append("nascimento = %s")
                dados.append(novo_nascimento_date)
            if nova_data_pagamento_str:
                nova_data_pagamento_date = datetime.strptime(nova_data_pagamento_str, '%Y-%m-%d').date()
                sql_parts.append("data_pagamento = %s")
                dados.append(nova_data_pagamento_date)
            
            if not sql_parts:
                messagebox.showwarning("Campos obrigatórios", "Preencha o ID e pelo menos um campo para atualizar!")
                return

            sql = "UPDATE alunos SET " + ", ".join(sql_parts) + " WHERE id = %s"
            dados.append(int(id_aluno))
            
            cursor.execute(sql, tuple(dados))
            conexao.commit()
            
            if cursor.rowcount:
                messagebox.showinfo("Sucesso", "Aluno atualizado!")
                limpar_campos()
            else:
                messagebox.showwarning("Aviso", "Aluno não encontrado ou nenhum dado para atualizar.")
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno deve ser um número inteiro válido ou formato de data inválido (use AAAA-MM-DD).")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao atualizar: {e}")
    else:
        messagebox.showwarning("Campo obrigatório", "Por favor, insira o ID do aluno para atualizar.")


def remover():
    # Verifica se os campos estão visíveis antes de tentar obter o ID
    if not show_fields.get():
        messagebox.showwarning("Campos Ocultos", "Por favor, ative os campos de preenchimento primeiro!")
        return
        
    id_aluno = entry_id.get()
    if id_aluno:
        try:
            sql = "DELETE FROM alunos WHERE id = %s"
            cursor.execute(sql, (id_aluno,))
            conexao.commit()
            if cursor.rowcount:
                messagebox.showinfo(" OK", "Aluno removido!")
                limpar_campos()
            else:
                messagebox.showwarning("POXA", "Não encontrei esse Aluno .")
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno deve ser um número inteiro válido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao remover: {e}")
    else:
        messagebox.showwarning("Campo obrigatório", "Por favor, insira o ID do aluno para remover.")

def limpar_campos():
    entry_id.delete(0, tk.END)
    entry_nome.delete(0, tk.END)
    entry_nascimento.delete(0, tk.END)
    entry_sexo.delete(0, tk.END)
    entry_curso.delete(0, tk.END)
    entry_data_pagamento.delete(0, tk.END)
    entry_telefone.delete(0, tk.END)

def verificar_atrasos():
    try:
        cursor.execute("SELECT nome_completo, data_pagamento FROM alunos WHERE data_pagamento < CURDATE()")
        alunos_atrasados = cursor.fetchall()

        if alunos_atrasados:
            mensagem = "Alunos com Pagamento Atrasado:\n\n"
            for nome, data_pagamento in alunos_atrasados:
                mensagem += f"- {nome} (Vencimento: {data_pagamento.strftime('%d/%m/%Y')})\n"
            messagebox.showwarning("ALERTA DE ATRASO", mensagem)
        else:
            messagebox.showinfo("Sem Atrasos", "Nenhum aluno com pagamento atrasado encontrado!")
    except Exception as e:
        messagebox.showerror("Erro na Verificação", f"Ocorreu um erro ao verificar atrasos: {e}")

def abrir_whatsapp():
    # Verifica se os campos estão visíveis antes de tentar obter o ID
    if not show_fields.get():
        messagebox.showwarning("Campos Ocultos", "Por favor, ative os campos de preenchimento primeiro!")
        return

    id_aluno = entry_id.get()
    if not id_aluno:
        messagebox.showwarning("Campo obrigatório", "Por favor, insira o ID do aluno para abrir o WhatsApp.")
        return

    try:
        cursor.execute("SELECT telefone FROM alunos WHERE id = %s", (int(id_aluno),))
        resultado = cursor.fetchone()

        if resultado:
            telefone = resultado[0]
            if telefone:
                telefone_limpo = ''.join(filter(str.isdigit, telefone))
                whatsapp_url = f"https://wa.me/{telefone_limpo}"
                webbrowser.open(whatsapp_url)
            else:
                messagebox.showinfo("WhatsApp", "Você precisa cadastrar o numero desse aluno primeiro .")
        else:
            messagebox.showwarning("Aviso", "Aluno não encontrado.")
    except ValueError:
        messagebox.showerror("Erro", "ID do aluno deve ser um número inteiro válido.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao abrir o WhatsApp: {e}")

def verificar_aniversarios():
    try:
        hoje = date.today()
        sql = "SELECT nome_completo FROM alunos WHERE MONTH(nascimento) = %s AND DAY(nascimento) = %s"
        cursor.execute(sql, (hoje.month, hoje.day))
        aniversariantes = cursor.fetchall()

        if aniversariantes:
            mensagem = "🎉 **UP UP **! ANIVERSARIANTES DE HOJE!** 🎉\n\n"
            for (nome,) in aniversariantes:
                mensagem += f"- {nome}\n"
            mensagem += "\nParabéns aos aniversariantes de hoje calaiooo!"
            messagebox.showinfo("Aniversariantes do Dia", mensagem)
    except Exception as e:
        messagebox.showerror("Erro de Aniversário", f"Ocorreu um erro ao verificar aniversários: {e}")

# NOVO: Função para alternar a visibilidade dos campos
def toggle_fields_visibility():
    if show_fields.get(): # Se a caixa está marcada (True)
        frame_campos.pack(padx=20, pady=10, fill="both", expand=True)
    else: # Se a caixa está desmarcada (False)
        frame_campos.pack_forget()

# --- Configuração da Janela Principal ---
janela = tk.Tk()
janela.title("Cadastro de Alunos - Escola de Música do JAO")
janela.geometry("450x680") # Mantido o tamanho por enquanto, pode ser ajustado

janela.configure(bg="#0E0D0D")

estilo = ttk.Style()
estilo.theme_use('clam')
estilo.configure('.', font=('Arial', 10))

estilo.configure('TLabel', background="#0E0D0D", foreground="#EE5011", font=('Arial', 10, 'bold'))
estilo.configure('TEntry', fieldbackground="#FCF8F8", foreground="#0A0A0A", insertbackground='#FFFF00')
estilo.configure('TButton',
                 font=('Arial', 10, 'bold'),
                 background="#F15214",
                 foreground="#0E0E0D",
                 relief='flat',
                 padding=10)

estilo.map('TButton',
           background=[('active', "#111111"), ('pressed', "#0C0C0C")],
           foreground=[('active', "#0A0A0A"), ('pressed', "#0F0F0E")])

# --- Adiciona a imagem/logo ---
#try:
#    img = Image.open("logo_escola.png")
#    img = img.resize((150, 75))
#    logo = ImageTk.PhotoImage(img)

#    label_logo = tk.Label(janela, image=logo, bg="#0E0D0D")
#    label_logo.image = logo
#    label_logo.pack(pady=10)
#except FileNotFoundError:
#    messagebox.showwarning("Aviso", "Arquivo de logo 'logo_escola.png' não encontrado. Continue sem logo.")
#except Exception as e:
#    messagebox.showerror("Erro de Imagem", f"Não foi possível carregar a imagem: {e}")

# --- Frame para os Botões (agora no topo, divididos em 2 colunas) ---
frame_botoes = ttk.Frame(janela, padding="10", style='TFrame')
frame_botoes.pack(pady=10)

# Configura as colunas do frame de botões para se expandirem
frame_botoes.columnconfigure(0, weight=1)
frame_botoes.columnconfigure(1, weight=1)

# Botões organizados em grid de 2 colunas
ttk.Button(frame_botoes, text="Cadastrar Aluno", command=cadastrar).grid(row=0, column=0, padx=5, pady=5, sticky='ew')
ttk.Button(frame_botoes, text="Listar Alunos", command=listar).grid(row=0, column=1, padx=5, pady=5, sticky='ew')
ttk.Button(frame_botoes, text="Atualizar Aluno", command=atualizar).grid(row=1, column=0, padx=5, pady=5, sticky='ew')
ttk.Button(frame_botoes, text="Remover Aluno", command=remover).grid(row=1, column=1, padx=5, pady=5, sticky='ew')
ttk.Button(frame_botoes, text="Limpar Campos", command=limpar_campos).grid(row=2, column=0, padx=5, pady=5, sticky='ew')
ttk.Button(frame_botoes, text="Verificar Atrasos", command=verificar_atrasos).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
ttk.Button(frame_botoes, text="Abrir WhatsApp", command=abrir_whatsapp).grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew') # Ocupa 2 colunas

# NOVO: Checkbox para visibilidade dos campos
show_fields = tk.BooleanVar()
show_fields.set(True) # Começa com os campos visíveis por padrão
ttk.Checkbutton(janela, text="Mostrar/Ocultar Campos de Preenchimento",
                variable=show_fields, command=toggle_fields_visibility,
                style='TLabel').pack(pady=10)


# --- Frame Principal para Campos de Entrada (agora na parte inferior) ---
frame_campos = ttk.Frame(janela, padding="20 20 20 20", relief="groove", borderwidth=2, style='TFrame')
frame_campos.pack(padx=20, pady=10, fill="both", expand=True) # Inicialmente visível

frame_campos.columnconfigure(1, weight=1)

# Rótulos e Entradas (Usando grid dentro de frame_campos)
row_idx = 0

ttk.Label(frame_campos, text="ID (para atualizar/remover):").grid(row=row_idx, column=0, sticky='w', pady=5)
entry_id = ttk.Entry(frame_campos, width=40, style='TEntry')
entry_id.grid(row=row_idx, column=1, sticky='ew', pady=5)
row_idx += 1

ttk.Label(frame_campos, text="Nome Completo:").grid(row=row_idx, column=0, sticky='w', pady=5)
entry_nome = ttk.Entry(frame_campos, width=40, style='TEntry')
entry_nome.grid(row=row_idx, column=1, sticky='ew', pady=5)
row_idx += 1

ttk.Label(frame_campos, text="Nascimento (AAAA-MM-DD):").grid(row=row_idx, column=0, sticky='w', pady=5)
entry_nascimento = ttk.Entry(frame_campos, width=40, style='TEntry')
entry_nascimento.grid(row=row_idx, column=1, sticky='ew', pady=5)
row_idx += 1

ttk.Label(frame_campos, text="Sexo:").grid(row=row_idx, column=0, sticky='w', pady=5)
entry_sexo = ttk.Entry(frame_campos, width=40, style='TEntry')
entry_sexo.grid(row=row_idx, column=1, sticky='ew', pady=5)
row_idx += 1

ttk.Label(frame_campos, text="Curso:").grid(row=row_idx, column=0, sticky='w', pady=5)
entry_curso = ttk.Entry(frame_campos, width=40, style='TEntry')
entry_curso.grid(row=row_idx, column=1, sticky='ew', pady=5)
row_idx += 1

ttk.Label(frame_campos, text="Data de Pagamento (AAAA-MM-DD):").grid(row=row_idx, column=0, sticky='w', pady=5)
entry_data_pagamento = ttk.Entry(frame_campos, width=40, style='TEntry')
entry_data_pagamento.grid(row=row_idx, column=1, sticky='ew', pady=5)
row_idx += 1

ttk.Label(frame_campos, text="Telefone (55DDNNNNNNNN):").grid(row=row_idx, column=0, sticky='w', pady=5)
entry_telefone = ttk.Entry(frame_campos, width=40, style='TEntry')
entry_telefone.grid(row=row_idx, column=1, sticky='ew', pady=5)
row_idx += 1

# --- Fechar Conexão ao Fechar a Janela ---
def on_closing():
    if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
        if cursor:
            cursor.close()
        if conexao and conexao.is_connected():
            conexao.close()
            print("Conexão com o MySQL fechada.")
        janela.destroy()

janela.protocol("WM_DELETE_WINDOW", on_closing)

#Chama a função de verificar aniversários no início 
janela.after(100, verificar_aniversarios)


janela.mainloop()

# Estas linhas após mainloop() podem não ser executadas se on_closing() for usado!!!.
if cursor:
    cursor.close()
if conexao and conexao.is_connected():
    conexao.close()
    print("Conexão com o MySQL fechada (fallback).") 
    
# --- Fim do Código ---