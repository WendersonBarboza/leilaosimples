import json
import os
import uuid
from tkinter import Tk, StringVar, DoubleVar, END, messagebox
from tkinter import ttk

DATA_FILE = "auctions_data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        data = {"users": [], "auctions": []}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"users": [], "auctions": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class AuctionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Leilão Simples")
        self.root.geometry("820x520")

        self.data = load_data()
        self.current_user = None

        self.username_var = StringVar()
        self.password_var = StringVar()

        self.title_var = StringVar()
        self.desc_var = StringVar()
        self.start_price_var = DoubleVar(value=0.0)

        self.bid_amount_var = DoubleVar(value=0.0)

        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        self.auth_frame = ttk.Frame(notebook, padding=16)
        self.market_frame = ttk.Frame(notebook, padding=16)

        notebook.add(self.auth_frame, text="Autenticação")
        notebook.add(self.market_frame, text="Leilões")

        self._build_auth_tab()
        self._build_market_tab()

    def _build_auth_tab(self):
        left = ttk.Frame(self.auth_frame)
        left.pack(side="left", fill="both", expand=True)

        title = ttk.Label(left, text="Entrar ou Cadastrar", font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w", pady=(0, 12))

        form = ttk.Frame(left)
        form.pack(anchor="w")

        ttk.Label(form, text="Usuário").grid(row=0, column=0, sticky="w", pady=4)
        user_entry = ttk.Entry(form, textvariable=self.username_var, width=30)
        user_entry.grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Senha").grid(row=1, column=0, sticky="w", pady=4)
        pass_entry = ttk.Entry(form, textvariable=self.password_var, show="*", width=30)
        pass_entry.grid(row=1, column=1, sticky="w", pady=4)

        btns = ttk.Frame(left)
        btns.pack(anchor="w", pady=8)

        ttk.Button(btns, text="Entrar", command=self.login).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(btns, text="Cadastrar", command=self.register).grid(row=0, column=1)

        self.session_lbl = ttk.Label(left, text="Não autenticado", foreground="#666")
        self.session_lbl.pack(anchor="w", pady=(8, 0))

        # Tips
        tip = ttk.Label(
            left,
            text=(
                "Dica: cadastre um usuário, faça login e vá na aba Leilões\n"
                "para criar um novo leilão ou dar lances."
            ),
            foreground="#555",
        )
        tip.pack(anchor="w", pady=(12, 0))

    def _build_market_tab(self):
        top = ttk.Frame(self.market_frame)
        top.pack(fill="x")

        self.user_badge = ttk.Label(top, text="Usuário: (desconectado)", font=("Segoe UI", 10, "bold"))
        self.user_badge.pack(side="left")

        ttk.Button(top, text="Atualizar", command=self.refresh_market).pack(side="right")

        body = ttk.Frame(self.market_frame)
        body.pack(fill="both", expand=True, pady=(12, 0))

        left = ttk.Labelframe(body, text="Criar Leilão", padding=12)
        left.pack(side="left", fill="y")

        form = ttk.Frame(left)
        form.pack(anchor="w")

        ttk.Label(form, text="Título").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.title_var, width=34).grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Descrição").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.desc_var, width=34).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(form, text="Preço inicial").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(form, textvariable=self.start_price_var, width=12).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Button(left, text="Criar", command=self.create_auction).pack(anchor="w", pady=(8, 0))

        center = ttk.Labelframe(body, text="Leilões", padding=12)
        center.pack(side="left", fill="both", expand=True, padx=12)

        columns = ("id", "titulo", "vendedor", "status", "preco", "maior_lance")
        self.tree = ttk.Treeview(center, columns=columns, show="headings", height=14)
        self.tree.heading("id", text="ID")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("vendedor", text="Vendedor")
        self.tree.heading("status", text="Status")
        self.tree.heading("preco", text="Atual")
        self.tree.heading("maior_lance", text="Por")

        self.tree.column("id", width=90, anchor="w")
        self.tree.column("titulo", width=160, anchor="w")
        self.tree.column("vendedor", width=100, anchor="w")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("preco", width=80, anchor="e")
        self.tree.column("maior_lance", width=100, anchor="w")

        self.tree.pack(fill="both", expand=True)

        right = ttk.Labelframe(body, text="Ações", padding=12)
        right.pack(side="left", fill="y")

        ttk.Label(right, text="Valor do lance").pack(anchor="w")
        ttk.Entry(right, textvariable=self.bid_amount_var, width=14).pack(anchor="w")
        ttk.Button(right, text="Dar lance no selecionado", command=self.place_bid).pack(anchor="w", pady=(6, 0))
        ttk.Separator(right, orient="horizontal").pack(fill="x", pady=8)
        ttk.Button(right, text="Fechar leilão (se seu)", command=self.close_auction).pack(anchor="w")

        self.refresh_market()

    # Auth
    def register(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Atenção", "Informe usuário e senha.")
            return
        if any(u["username"].lower() == username.lower() for u in self.data["users"]):
            messagebox.showerror("Erro", "Usuário já existe.")
            return
        self.data["users"].append({"username": username, "password": password})
        save_data(self.data)
        messagebox.showinfo("Sucesso", "Usuário cadastrado. Agora faça login.")

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("Atenção", "Informe usuário e senha.")
            return
        user = next((u for u in self.data["users"] if u["username"].lower() == username.lower() and u["password"] == password), None)
        if not user:
            messagebox.showerror("Erro", "Credenciais inválidas.")
            return
        self.current_user = user["username"]
        self.session_lbl.config(text=f"Autenticado como: {self.current_user}")
        self.user_badge.config(text=f"Usuário: {self.current_user}")
        messagebox.showinfo("Bem-vindo", f"Olá, {self.current_user}!")

    # Market
    def refresh_market(self):
        # reload from disk in case of external changes
        self.data = load_data()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for a in self.data.get("auctions", []):
            highest_by = a.get("highest_bidder") or "-"
            self.tree.insert("", END, values=(
                a.get("id"),
                a.get("title"),
                a.get("owner"),
                a.get("status"),
                f"R$ {a.get('current_price', 0):.2f}",
                highest_by,
            ))

    def create_auction(self):
        if not self.current_user:
            messagebox.showwarning("Atenção", "Faça login para criar leilões.")
            return
        title = self.title_var.get().strip()
        desc = self.desc_var.get().strip()
        try:
            start_price = float(self.start_price_var.get())
        except Exception:
            start_price = -1
        if not title or start_price is None or start_price < 0:
            messagebox.showwarning("Atenção", "Informe título e preço inicial válido.")
            return
        auction = {
            "id": uuid.uuid4().hex[:8],
            "title": title,
            "description": desc,
            "owner": self.current_user,
            "start_price": float(start_price),
            "current_price": float(start_price),
            "highest_bidder": None,
            "status": "aberto",
            "bids": [],
        }
        self.data["auctions"].append(auction)
        save_data(self.data)
        self.title_var.set("")
        self.desc_var.set("")
        self.start_price_var.set(0.0)
        self.refresh_market()
        messagebox.showinfo("Sucesso", "Leilão criado.")

    def _get_selected_auction(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        if not values:
            return None
        aid = values[0]
        return next((a for a in self.data["auctions"] if a["id"] == aid), None)

    def place_bid(self):
        if not self.current_user:
            messagebox.showwarning("Atenção", "Faça login para dar lances.")
            return
        auction = self._get_selected_auction()
        if not auction:
            messagebox.showwarning("Atenção", "Selecione um leilão.")
            return
        if auction["status"] != "aberto":
            messagebox.showwarning("Atenção", "Leilão não está aberto.")
            return
        if auction["owner"] == self.current_user:
            messagebox.showwarning("Atenção", "Você não pode dar lance no próprio leilão.")
            return
        try:
            amount = float(self.bid_amount_var.get())
        except Exception:
            amount = -1
        min_required = max(auction["current_price"], 0)
        if amount <= min_required:
            messagebox.showerror("Erro", f"Lance deve ser maior que R$ {min_required:.2f}.")
            return
        auction["current_price"] = amount
        auction["highest_bidder"] = self.current_user
        auction["bids"].append({"user": self.current_user, "amount": amount})
        # Regra: se atingir ou ultrapassar o triplo do preço inicial, encerra e declara vencedor
        base = float(auction.get("start_price", auction["current_price"]))
        if amount >= 3 * base:
            auction["status"] = "fechado"
            save_data(self.data)
            self.refresh_market()
            messagebox.showinfo(
                "Leilão fechado",
                f"Vencedor: {self.current_user}\nValor: R$ {amount:.2f}",
            )
            return
        save_data(self.data)
        self.refresh_market()
        messagebox.showinfo("Sucesso", "Lance registrado.")

    def close_auction(self):
        if not self.current_user:
            messagebox.showwarning("Atenção", "Faça login.")
            return
        auction = self._get_selected_auction()
        if not auction:
            messagebox.showwarning("Atenção", "Selecione um leilão.")
            return
        if auction["owner"] != self.current_user:
            messagebox.showwarning("Atenção", "Apenas o dono pode fechar o leilão.")
            return
        if auction["status"] != "aberto":
            messagebox.showinfo("Info", "Leilão já está fechado.")
            return
        auction["status"] = "fechado"
        save_data(self.data)
        self.refresh_market()
        winner = auction.get("highest_bidder")
        if winner:
            messagebox.showinfo(
                "Leilão fechado",
                f"Vencedor: {winner}\nValor: R$ {auction['current_price']:.2f}",
            )
        else:
            messagebox.showinfo("Leilão fechado", "Sem lances. Não houve vencedor.")


if __name__ == "__main__":
    root = Tk()
    # Tema nativo melhorado
    try:
        root.style = ttk.Style()
        if "vista" in root.style.theme_names():
            root.style.theme_use("vista")
        elif "clam" in root.style.theme_names():
            root.style.theme_use("clam")
    except Exception:
        pass
    app = AuctionApp(root)
    root.mainloop()
