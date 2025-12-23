import customtkinter as ctk
import pandas as pd
import sqlite3
import sys
import os
import time
import json
import webbrowser
from datetime import datetime
from tkinter import messagebox, ttk
from urllib.request import urlopen, Request
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ==============================================================================
# ⚙️ CONFIGURAÇÕES
# ==============================================================================
DB_FILE = 'controle_cotas.db'
GITHUB_USER = "fellipesillvaoff"
GITHUB_REPO = "carteira"
VERSION = "1.0.0"

def obter_caminho_externo(arquivo):
    if getattr(sys, 'frozen', False):
        pasta_base = os.path.dirname(sys.executable)
    else:
        pasta_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(pasta_base, arquivo)

# ==============================================================================
# 🗄️ BANCO DE DADOS
# ==============================================================================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. Movimentação de Cotistas
    c.execute('''
        CREATE TABLE IF NOT EXISTS cotistas_mov (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Data TEXT,
            Cotista TEXT,
            Tipo TEXT, 
            Valor REAL,
            Cota_Ref REAL,
            Qtd_Cotas REAL,
            Ticker_Ref TEXT
        )
    ''')

    # 2. Carteira de Ativos
    c.execute('''
        CREATE TABLE IF NOT EXISTS ativos (
            Ticker TEXT PRIMARY KEY,
            Qtd REAL,
            Preco_Medio REAL,
            Preco_Atual REAL,
            Stop_Loss REAL,
            Tipo TEXT 
        )
    ''')
    
    c.execute("INSERT OR IGNORE INTO ativos (Ticker, Qtd, Preco_Medio, Preco_Atual, Stop_Loss, Tipo) VALUES ('CAIXA', 0, 1, 1, 0, 'Caixa')")
    
    # 3. Histórico de Cota
    c.execute('''
        CREATE TABLE IF NOT EXISTS historico_cota (
            Data TEXT,
            Valor_Cota REAL
        )
    ''')

    # Migração para garantir compatibilidade
    try: c.execute("ALTER TABLE cotistas_mov ADD COLUMN Ticker_Ref TEXT")
    except: pass

    conn.commit()
    conn.close()

# --- CÁLCULOS FINANCEIROS ---
def get_patrimonio_liquido():
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query("SELECT * FROM ativos", conn)
        if df.empty: return 0.0
        df['Valor_Total'] = df['Qtd'] * df['Preco_Atual']
        return df['Valor_Total'].sum()
    except: return 0.0
    finally: conn.close()

def get_total_cotas():
    conn = sqlite3.connect(DB_FILE)
    try:
        res = conn.execute("SELECT SUM(Qtd_Cotas) FROM cotistas_mov").fetchone()[0]
        return res if res else 0.0
    except: return 0.0
    finally: conn.close()

def calcular_valor_cota():
    pl = get_patrimonio_liquido()
    total_cotas = get_total_cotas()
    if total_cotas <= 0: return 1.0
    return pl / total_cotas

def registrar_historico_cota(data_ref=None):
    if not data_ref:
        data_ref = datetime.today().strftime('%Y-%m-%d')
    
    cota = calcular_valor_cota()
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM historico_cota WHERE Data = ?", (data_ref,))
    conn.execute("INSERT INTO historico_cota VALUES (?, ?)", (data_ref, cota))
    conn.commit()
    conn.close()

# ==============================================================================
# 🛠️ POP-UP: MARK-TO-MARKET (Atualização de Preços)
# ==============================================================================
class JanelaAtualizacaoAtivos(ctk.CTkToplevel):
    def __init__(self, parent, callback_confirmar):
        super().__init__(parent)
        self.title("Mark-to-Market (Atualizar Preços)")
        self.geometry("500x500")
        self.callback = callback_confirmar
        self.attributes("-topmost", True)
        
        ctk.CTkLabel(self, text="⚠️ ATUALIZE OS ATIVOS ANTES DA MOVIMENTAÇÃO", text_color="orange", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.entradas = {}
        conn = sqlite3.connect(DB_FILE)
        ativos = conn.execute("SELECT Ticker, Preco_Atual FROM ativos WHERE Ticker != 'CAIXA' AND Qtd > 0").fetchall()
        conn.close()
        
        if not ativos:
            ctk.CTkLabel(self.scroll, text="Apenas CAIXA na carteira. Pode prosseguir.").pack(pady=20)
        
        for ticker, preco in ativos:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=ticker, width=80, anchor="w").pack(side="left")
            ent = ctk.CTkEntry(row)
            ent.insert(0, str(preco))
            ent.pack(side="right", fill="x", expand=True)
            self.entradas[ticker] = ent

        ctk.CTkButton(self, text="CONFIRMAR E PROCESSAR", command=self.salvar, fg_color="green").pack(pady=10, padx=20)

    def salvar(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            for ticker, entry in self.entradas.items():
                novo = float(entry.get().replace(",", "."))
                conn.execute("UPDATE ativos SET Preco_Atual = ? WHERE Ticker = ?", (novo, ticker))
            conn.commit()
            conn.close()
            self.callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Erro", "Preços inválidos.")

# ==============================================================================
# 🚀 TELA DE CARREGAMENTO (SPLASH)
# ==============================================================================
class SplashWithLog(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.running = True
        
        # Centralizar
        w, h = 500, 600
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x, y = int((sw/2)-(w/2)), int((sh/2)-(h/2))
            self.geometry(f'{w}x{h}+{x}+{y}')
        except: self.geometry(f'{w}x{h}')

        self.configure(fg_color='#1a1a1a')
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="ASSET MANAGEMENT", font=("Arial", 24, "bold"), text_color="white").pack(pady=(40, 10))
        self.lbl_gif = ctk.CTkLabel(self, text="")
        self.lbl_gif.pack(pady=10)
        
        self.lbl_status = ctk.CTkLabel(self, text="Iniciando...", text_color="#ffcc00")
        self.lbl_status.pack(pady=10)
        
        self.log_box = ctk.CTkTextbox(self, height=120, fg_color="black", text_color="#00ff00")
        self.log_box.pack(pady=10, padx=20, fill="x")
        
        self.gif_frames = []
        self.current_frame = 0
        self.carregar_gif("loading.gif")
        self.after(500, self.iniciar)

    def log(self, msg):
        if not self.running: return
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")
        self.update()

    def carregar_gif(self, filename):
        path = obter_caminho_externo(filename)
        if os.path.exists(path):
            try:
                pil_image = Image.open(path)
                for _ in range(pil_image.n_frames):
                    pil_image.seek(len(self.gif_frames))
                    frame = pil_image.convert("RGBA")
                    ctk_img = ctk.CTkImage(light_image=frame, dark_image=frame, size=(440, 400))
                    self.gif_frames.append(ctk_img)
                self.animate()
            except: self.log("Erro no GIF")

    def animate(self):
        if not self.running or not self.winfo_exists(): return
        if self.gif_frames:
            self.lbl_gif.configure(image=self.gif_frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.after(500, self.animate)

    def iniciar(self):
        try:
            self.log("Conectando Banco de Dados...")
            init_db()
            time.sleep(0.5)
            self.log("Sistema Pronto.")
            self.after(1000, self.abrir_app)
        except Exception as e:
            self.log(f"Erro Fatal: {e}")

    def abrir_app(self):
        self.running = False
        self.destroy()
        app = AppCotas()
        app.mainloop()

# ==============================================================================
# 🏠 ABA 1: SUMÁRIO
# ==============================================================================
class FrameSumario(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.frame_top = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_top.pack(fill="x", padx=10, pady=10)
        self.card_pl = self.criar_card(self.frame_top, "Patrimônio Líquido", "R$ 0.00", 0)
        self.card_cota = self.criar_card(self.frame_top, "Valor Cota", "R$ 1.00", 1)
        self.card_caixa = self.criar_card(self.frame_top, "Caixa Livre", "R$ 0.00", 2)

        self.frame_mid = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_mid.pack(fill="both", expand=True, padx=10)
        
        self.frame_graph = ctk.CTkFrame(self.frame_mid)
        self.frame_graph.pack(side="left", fill="both", expand=True, padx=5)
        
        self.frame_list = ctk.CTkFrame(self.frame_mid, width=300)
        self.frame_list.pack(side="right", fill="both", padx=5)
        
        ctk.CTkLabel(self.frame_list, text="Posição dos Cotistas", font=("Arial", 14, "bold")).pack(pady=5)
        
        cols = ("Nome", "Cotas", "PM", "Rentab")
        self.tree = ttk.Treeview(self.frame_list, columns=cols, show="headings", height=15)
        for c in cols: 
            self.tree.heading(c, text=c)
            self.tree.column(c, width=70, anchor="center")
        self.tree.column("Nome", width=100)
        self.tree.pack(fill="both", expand=True)

    def criar_card(self, parent, t, v, c):
        f = ctk.CTkFrame(parent, fg_color="#333333")
        f.grid(row=0, column=c, sticky="ew", padx=5)
        parent.grid_columnconfigure(c, weight=1)
        ctk.CTkLabel(f, text=t, text_color="gray").pack(pady=5)
        lbl = ctk.CTkLabel(f, text=v, font=("Arial", 18, "bold"))
        lbl.pack(pady=5)
        return lbl

    def atualizar(self):
        pl = get_patrimonio_liquido()
        cota = calcular_valor_cota()
        conn = sqlite3.connect(DB_FILE)
        caixa = conn.execute("SELECT Qtd FROM ativos WHERE Ticker='CAIXA'").fetchone()
        conn.close()
        
        self.card_pl.configure(text=f"R$ {pl:,.2f}")
        self.card_cota.configure(text=f"R$ {cota:.6f}")
        self.card_caixa.configure(text=f"R$ {caixa[0]:,.2f}" if caixa else "R$ 0.00")

        # Tabela
        for i in self.tree.get_children(): self.tree.delete(i)
        
        # Algoritmo de Preço Médio
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM cotistas_mov ORDER BY Data ASC, ID ASC", conn)
        conn.close()
        
        posicoes = {}
        for _, row in df.iterrows():
            nome = row['Cotista']
            qtd = row['Qtd_Cotas']
            ref = row['Cota_Ref']
            if nome not in posicoes: posicoes[nome] = {'Qtd': 0.0, 'PM': 0.0}
            
            p = posicoes[nome]
            if qtd > 0: # Compra
                total_atual = p['Qtd'] * p['PM']
                novo_total = qtd * ref
                p['Qtd'] += qtd
                if p['Qtd'] > 0: p['PM'] = (total_atual + novo_total) / p['Qtd']
            else: # Venda
                p['Qtd'] += qtd
                if p['Qtd'] <= 0: p['Qtd'], p['PM'] = 0, 0

        for nome, p in posicoes.items():
            if p['Qtd'] > 0.001:
                rent = ((cota - p['PM']) / p['PM']) * 100 if p['PM'] > 0 else 0
                self.tree.insert("", "end", values=(nome, f"{p['Qtd']:.4f}", f"R$ {p['PM']:.4f}", f"{rent:.2f}%"))

        self.plotar_grafico()

    def plotar_grafico(self):
        for w in self.frame_graph.winfo_children(): w.destroy()
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM historico_cota ORDER BY Data", conn)
        conn.close()
        
        fig = Figure(figsize=(5,4), dpi=100, facecolor="#2b2b2b")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#2b2b2b")
        if not df.empty:
            ax.plot(pd.to_datetime(df['Data']), df['Valor_Cota'], color='#00ff00')
            ax.fill_between(pd.to_datetime(df['Data']), df['Valor_Cota'], alpha=0.1, color='#00ff00')
        ax.set_title("Evolução da Cota", color="white")
        ax.tick_params(colors='white')
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

# ==============================================================================
# 👥 ABA 2: APORTES E SAQUES (COM DATA E CHECK DE ATIVOS)
# ==============================================================================
class FrameCotistas(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        ctk.CTkLabel(self, text="Movimentação de Cotistas", font=("Arial", 18, "bold")).pack(pady=20)
        
        self.form = ctk.CTkFrame(self)
        self.form.pack(pady=10)
        
        # Linha 1
        self.entry_data = ctk.CTkEntry(self.form, placeholder_text="Data (YYYY-MM-DD)")
        self.entry_data.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.entry_data.grid(row=0, column=0, padx=5, pady=5)
        
        self.entry_nome = ctk.CTkEntry(self.form, placeholder_text="Nome Cotista")
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)
        
        # Linha 2
        self.cb_tipo = ctk.CTkComboBox(self.form, values=["Aporte (+)", "Saque (-)"])
        self.cb_tipo.grid(row=1, column=0, padx=5, pady=5)
        
        self.entry_ativo = ctk.CTkEntry(self.form, placeholder_text="Ativo (CAIXA)")
        self.entry_ativo.insert(0, "CAIXA")
        self.entry_ativo.grid(row=1, column=1, padx=5, pady=5)
        
        self.entry_valor = ctk.CTkEntry(self.form, placeholder_text="Valor Financeiro (R$)")
        self.entry_valor.grid(row=1, column=2, padx=5, pady=5)
        
        ctk.CTkButton(self.form, text="Processar", command=self.pre_check).grid(row=1, column=3, padx=10)

        # Histórico
        self.tree = ttk.Treeview(self, columns=("Data", "Nome", "Tipo", "Valor", "Cotas"), show="headings", height=10)
        for c in ("Data", "Nome", "Tipo", "Valor", "Cotas"): 
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

    def pre_check(self):
        try:
            if not self.entry_nome.get(): return messagebox.showwarning("Erro", "Nome obrigatório")
            float(self.entry_valor.get().replace(",", "."))
            # Abre verificação de preços
            JanelaAtualizacaoAtivos(self, self.efetivar)
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido")

    def efetivar(self):
        try:
            data = self.entry_data.get()
            nome = self.entry_nome.get()
            valor = float(self.entry_valor.get().replace(",", "."))
            tipo = self.cb_tipo.get()
            ticker = self.entry_ativo.get().upper()
            
            cota = calcular_valor_cota()
            if cota == 0: cota = 1.0
            
            qtd = valor / cota
            fator = 1 if "Aporte" in tipo else -1
            qtd_cotas = qtd * fator
            
            conn = sqlite3.connect(DB_FILE)
            # 1. Registra Movimentação
            conn.execute("INSERT INTO cotistas_mov (Data, Cotista, Tipo, Valor, Cota_Ref, Qtd_Cotas, Ticker_Ref) VALUES (?,?,?,?,?,?,?)",
                         (data, nome, tipo, valor, cota, qtd_cotas, ticker))
            
            # 2. Atualiza Saldo do Ativo (Caixa ou outro)
            # Simplificação: Tudo impacta o saldo financeiro do ativo (Qtd)
            conn.execute(f"UPDATE ativos SET Qtd = Qtd + ? WHERE Ticker = 'CAIXA'", (valor * fator,))
            
            conn.commit()
            conn.close()
            registrar_historico_cota(data)
            messagebox.showinfo("Sucesso", "Registrado!")
            self.atualizar()
            
        except Exception as e: messagebox.showerror("Erro", str(e))

    def atualizar(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query("SELECT * FROM cotistas_mov ORDER BY ID DESC LIMIT 20", conn)
        conn.close()
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(row['Data'], row['Cotista'], row['Tipo'], f"R$ {row['Valor']:,.2f}", f"{row['Qtd_Cotas']:.4f}"))

# ==============================================================================
# 📈 ABA 3: TRADING (COM DATA)
# ==============================================================================
class FrameTrading(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Mesa de Operações", font=("Arial", 18, "bold")).pack(pady=20)
        
        self.form = ctk.CTkFrame(self)
        self.form.pack(pady=10)
        
        self.entry_data = ctk.CTkEntry(self.form, placeholder_text="Data")
        self.entry_data.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.entry_data.grid(row=0, column=0, padx=5)
        
        self.cb_op = ctk.CTkComboBox(self.form, values=["COMPRA", "VENDA"])
        self.cb_op.grid(row=0, column=1, padx=5)
        
        self.entry_ticker = ctk.CTkEntry(self.form, placeholder_text="Ticker")
        self.entry_ticker.grid(row=0, column=2, padx=5)
        
        self.entry_qtd = ctk.CTkEntry(self.form, placeholder_text="Qtd")
        self.entry_qtd.grid(row=0, column=3, padx=5)
        
        self.entry_preco = ctk.CTkEntry(self.form, placeholder_text="Preço")
        self.entry_preco.grid(row=0, column=4, padx=5)
        
        ctk.CTkButton(self.form, text="ENVIAR", command=self.enviar).grid(row=0, column=5, padx=10)
        
        self.lbl_caixa = ctk.CTkLabel(self, text="Caixa: R$ 0.00", text_color="#00ff00")
        self.lbl_caixa.pack(pady=10)

    def enviar(self):
        try:
            op = self.cb_op.get()
            ticker = self.entry_ticker.get().upper()
            qtd = int(self.entry_qtd.get())
            preco = float(self.entry_preco.get().replace(",", "."))
            total = qtd * preco
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            caixa = cursor.execute("SELECT Qtd FROM ativos WHERE Ticker='CAIXA'").fetchone()[0]
            
            if op == "COMPRA":
                if caixa < total: return messagebox.showerror("Erro", "Sem Caixa")
                cursor.execute("UPDATE ativos SET Qtd = Qtd - ? WHERE Ticker='CAIXA'", (total,))
                
                existe = cursor.execute("SELECT Qtd, Preco_Medio FROM ativos WHERE Ticker=?", (ticker,)).fetchone()
                if existe:
                    nova_qtd = existe[0] + qtd
                    novo_pm = ((existe[0] * existe[1]) + total) / nova_qtd
                    cursor.execute("UPDATE ativos SET Qtd=?, Preco_Medio=?, Preco_Atual=? WHERE Ticker=?", (nova_qtd, novo_pm, preco, ticker))
                else:
                    cursor.execute("INSERT INTO ativos VALUES (?, ?, ?, ?, 0, 'Ação')", (ticker, qtd, preco, preco))
                    
            elif op == "VENDA":
                existe = cursor.execute("SELECT Qtd FROM ativos WHERE Ticker=?", (ticker,)).fetchone()
                if not existe or existe[0] < qtd: return messagebox.showerror("Erro", "Sem Ativos")
                
                cursor.execute("UPDATE ativos SET Qtd = Qtd + ? WHERE Ticker='CAIXA'", (total,))
                nova_qtd = existe[0] - qtd
                if nova_qtd == 0: cursor.execute("DELETE FROM ativos WHERE Ticker=?", (ticker,))
                else: cursor.execute("UPDATE ativos SET Qtd=? WHERE Ticker=?", (nova_qtd, ticker))

            conn.commit()
            conn.close()
            registrar_historico_cota(self.entry_data.get())
            messagebox.showinfo("Sucesso", "Ordem Executada")
            self.atualizar()
            
        except ValueError: messagebox.showerror("Erro", "Dados inválidos")

    def atualizar(self):
        conn = sqlite3.connect(DB_FILE)
        caixa = conn.execute("SELECT Qtd FROM ativos WHERE Ticker='CAIXA'").fetchone()[0]
        conn.close()
        self.lbl_caixa.configure(text=f"Caixa Disponível: R$ {caixa:,.2f}")

# ==============================================================================
# 📝 ABA 4: EDITOR DE REGISTROS (NOVA)
# ==============================================================================
class FrameEditor(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        ctk.CTkLabel(self, text="Editor de Registros (Correção)", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.frame_sel = ctk.CTkFrame(self)
        self.frame_sel.pack(fill="x", padx=10)
        
        ctk.CTkLabel(self.frame_sel, text="Tabela:").pack(side="left", padx=5)
        self.cb_tabela = ctk.CTkComboBox(self.frame_sel, values=["cotistas_mov", "ativos"], command=self.carregar_dados)
        self.cb_tabela.pack(side="left", padx=5)
        self.cb_tabela.set("cotistas_mov")
        
        ctk.CTkButton(self.frame_sel, text="🗑️ Excluir Selecionado", command=self.excluir, fg_color="red").pack(side="right", padx=10)
        ctk.CTkButton(self.frame_sel, text="✏️ Salvar Edição", command=self.salvar_edicao).pack(side="right", padx=10)

        # Treeview
        self.tree = ttk.Treeview(self, show="headings", height=15)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.ao_selecionar)
        
        # Area de Edição
        self.frame_edit = ctk.CTkScrollableFrame(self, height=100, orientation="horizontal")
        self.frame_edit.pack(fill="x", padx=10, pady=10)
        self.entradas = {}
        
        self.carregar_dados()

    def carregar_dados(self, _=None):
        tabela = self.cb_tabela.get()
        # Limpar
        for i in self.tree.get_children(): self.tree.delete(i)
        for w in self.frame_edit.winfo_children(): w.destroy()
        self.entradas = {}
        
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
        conn.close()
        
        if df.empty: return
        
        cols = list(df.columns)
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100, anchor="center")
            
            # Criar campos de edição
            f = ctk.CTkFrame(self.frame_edit)
            f.pack(side="left", padx=5)
            ctk.CTkLabel(f, text=c).pack()
            e = ctk.CTkEntry(f, width=100)
            e.pack()
            self.entradas[c] = e
            
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def ao_selecionar(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        cols = self.tree["columns"]
        
        for i, c in enumerate(cols):
            self.entradas[c].delete(0, "end")
            self.entradas[c].insert(0, str(vals[i]))

    def salvar_edicao(self):
        tabela = self.cb_tabela.get()
        pk = "ID" if tabela == "cotistas_mov" else "Ticker"
        id_val = self.entradas[pk].get()
        
        set_clause = []
        params = []
        for col, ent in self.entradas.items():
            set_clause.append(f"{col} = ?")
            params.append(ent.get())
        
        params.append(id_val) # Para o WHERE
        
        query = f"UPDATE {tabela} SET {', '.join(set_clause)} WHERE {pk} = ?"
        
        try:
            conn = sqlite3.connect(DB_FILE)
            conn.execute(query, params)
            conn.commit()
            conn.close()
            messagebox.showinfo("Info", "Registro atualizado!")
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def excluir(self):
        sel = self.tree.selection()
        if not sel: return
        tabela = self.cb_tabela.get()
        pk = "ID" if tabela == "cotistas_mov" else "Ticker"
        id_val = self.tree.item(sel[0])['values'][0] # Assume PK na col 0
        
        if messagebox.askyesno("Confirmar", "Apagar registro?"):
            conn = sqlite3.connect(DB_FILE)
            conn.execute(f"DELETE FROM {tabela} WHERE {pk} = ?", (id_val,))
            conn.commit()
            conn.close()
            self.carregar_dados()

# ==============================================================================
# APP PRINCIPAL
# ==============================================================================
class AppCotas(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestão de Fundo")
        self.geometry("1920x1080")
        init_db()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="ASSET MANAGER", font=("Arial", 20, "bold")).pack(pady=30)
        
        self.btn_sumario = self.menu_btn("🏠 Sumário", lambda: self.show("Sumario"))
        self.btn_cotistas = self.menu_btn("👥 Aportes/Saques", lambda: self.show("Cotistas"))
        self.btn_trading = self.menu_btn("📈 Trading", lambda: self.show("Trading"))
        self.btn_editor = self.menu_btn("📝 Editor BD", lambda: self.show("Editor"))
        
        ctk.CTkLabel(self.sidebar, text="--- Sistema ---").pack(pady=10)
        self.menu_btn("☁️ Checar Updates", self.checar_updates)

        self.frames = {
            "Sumario": FrameSumario(self),
            "Cotistas": FrameCotistas(self),
            "Trading": FrameTrading(self),
            "Editor": FrameEditor(self)
        }
        self.show("Sumario")

    def menu_btn(self, t, c):
        btn = ctk.CTkButton(self.sidebar, text=t, command=c, fg_color="transparent", anchor="w", height=40)
        btn.pack(pady=5, padx=10, fill="x")
        return btn

    def show(self, name):
        for f in self.frames.values(): f.grid_forget()
        self.frames[name].grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        if hasattr(self.frames[name], "atualizar"): self.frames[name].atualizar()
        if hasattr(self.frames[name], "carregar_dados"): self.frames[name].carregar_dados()

    def checar_updates(self):
        try:
            url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                tag = data.get('tag_name', '').replace('v', '')
                if tag > VERSION:
                    if messagebox.askyesno("Update", f"Versão {tag} disponível! Baixar?"):
                        webbrowser.open(data.get('html_url'))
                else:
                    messagebox.showinfo("Info", "Sistema atualizado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao verificar: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = SplashWithLog()
    app.mainloop()
