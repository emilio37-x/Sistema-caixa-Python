import customtkinter as ctk
from datetime import datetime
import winsound
import tkinter.messagebox as msg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ================= PRODUTOS =================
# Exemplo:
# unidade e caixa como produtos diferentes
produtos = {
    "789123": ("Arroz", 20.50),
    "789456": ("Feijão", 8.90),
    "789111": ("Cerveja Lata", 4.50),
    "789222": ("Caixa de Cerveja 12un", 48.00),
    "5":      ('Caixa de Heineken', 63.00)
}

total = 0.0
vendas = []
itens_compra = []

# Cada item da compra:
# (codigo, nome, preco_unitario, quantidade)

# ================= FUNÇÕES =================

def obter_quantidade():
    texto = entrada_qtd.get().strip()
    if texto.isdigit() and int(texto) > 0:
        return int(texto)
    return 1


def limpar_quantidade():
    entrada_qtd.delete(0, "end")


def ler_codigo(event=None):
    global total

    codigo = entrada.get().strip()
    entrada.delete(0, "end")

    if not codigo:
        return

    quantidade = obter_quantidade()

    if codigo in produtos:
        nome, preco = produtos[codigo]
        subtotal = preco * quantidade
        total += subtotal

        itens_compra.append((codigo, nome, preco, quantidade))

        winsound.Beep(1000, 150)

        label_produto.configure(
            text=f"{nome} x{quantidade} - R$ {subtotal:.2f}"
        )
        label_total.configure(text=f"R$ {total:.2f}")

        atualizar_lista()
    else:
        label_produto.configure(text="Produto não encontrado")

    # a quantidade vale só para o próximo item
    limpar_quantidade()


def atualizar_lista():
    lista_itens.delete("0.0", "end")

    for _, nome, preco, quantidade in itens_compra:
        subtotal = preco * quantidade
        lista_itens.insert(
            "end",
            f"{nome} x{quantidade} - R$ {subtotal:.2f}\n"
        )

    lista_itens.insert("end", "----------------------\n")
    lista_itens.insert("end", f"TOTAL: R$ {total:.2f}")


def remover_item():
    global total

    if itens_compra:
        _, nome, preco, quantidade = itens_compra.pop()
        subtotal = preco * quantidade
        total -= subtotal

        if total < 0:
            total = 0

        label_produto.configure(text=f"Removido: {nome} x{quantidade}")
        label_total.configure(text=f"R$ {total:.2f}")

        atualizar_lista()


def cancelar_compra():
    global total

    if itens_compra and msg.askyesno("Confirmar", "Cancelar compra?"):
        total = 0.0
        itens_compra.clear()
        lista_itens.delete("0.0", "end")

        label_produto.configure(text="Compra cancelada")
        label_total.configure(text="R$ 0.00")

        esconder_dinheiro()
        limpar_quantidade()


def finalizar(forma):
    global total

    if total == 0:
        return

    data = datetime.now().strftime("%d/%m/%Y %H:%M")

    vendas.append((data, total, forma))
    lista_vendas.insert("end", f"{data} | R$ {total:.2f} | {forma}\n")

    atualizar_resumo()

    if forma != "Dinheiro":
        label_produto.configure(text=f"Pago via {forma}")

    total = 0.0
    itens_compra.clear()
    lista_itens.delete("0.0", "end")
    label_total.configure(text="R$ 0.00")
    limpar_quantidade()


def atualizar_resumo():
    total_geral = sum(v[1] for v in vendas)

    dinheiro = sum(v[1] for v in vendas if v[2] == "Dinheiro")
    pix = sum(v[1] for v in vendas if v[2] == "Pix")
    credito = sum(v[1] for v in vendas if v[2] == "Crédito")
    debito = sum(v[1] for v in vendas if v[2] == "Débito")

    resumo.configure(
        text=(
            f"TOTAL: R$ {total_geral:.2f}\n"
            f"Dinheiro: R$ {dinheiro:.2f} | Pix: R$ {pix:.2f}\n"
            f"Crédito: R$ {credito:.2f} | Débito: R$ {debito:.2f}"
        )
    )

# ================= DINHEIRO =================

def mostrar_dinheiro():
    frame_dinheiro.pack(pady=10, fill="x", padx=10)
    entrada_dinheiro.focus()


def esconder_dinheiro():
    frame_dinheiro.pack_forget()
    entrada_dinheiro.delete(0, "end")
    label_troco.configure(text="R$ 0.00", text_color="white")


def calcular_troco(event=None):
    try:
        valor = float(entrada_dinheiro.get().replace(",", "."))
        troco = valor - total

        if troco < 0:
            label_troco.configure(text="Valor insuficiente", text_color="red")
        else:
            label_troco.configure(text=f"R$ {troco:.2f}", text_color="green")
    except ValueError:
        label_troco.configure(text="R$ 0.00", text_color="white")


def confirmar_dinheiro():
    global total

    try:
        valor = float(entrada_dinheiro.get().replace(",", "."))
        troco = valor - total

        if troco < 0:
            label_produto.configure(text="Valor insuficiente")
            return

        label_produto.configure(text=f"Troco: R$ {troco:.2f}")

        finalizar("Dinheiro")
        esconder_dinheiro()

    except ValueError:
        label_produto.configure(text="Valor inválido")

# ================= RELATÓRIO =================

def salvar():
    if not vendas:
        return

    nome = datetime.now().strftime("relatorio_%d-%m-%Y.txt")

    total_geral = sum(v[1] for v in vendas)
    dinheiro = sum(v[1] for v in vendas if v[2] == "Dinheiro")
    pix = sum(v[1] for v in vendas if v[2] == "Pix")
    credito = sum(v[1] for v in vendas if v[2] == "Crédito")
    debito = sum(v[1] for v in vendas if v[2] == "Débito")

    with open(nome, "w", encoding="utf-8") as f:
        f.write("RELATÓRIO DE VENDAS - DEPÓSITO\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}\n\n")

        f.write("-" * 45 + "\n")
        f.write("VENDAS REALIZADAS:\n")
        f.write("-" * 45 + "\n")

        for data, valor, forma in vendas:
            hora = data.split()[1]
            f.write(f"{hora} | R$ {valor:.2f} | {forma}\n")

        f.write("\n" + "-" * 45 + "\n")
        f.write("RESUMO DO DIA:\n")
        f.write("-" * 45 + "\n")
        f.write(f"Dinheiro: R$ {dinheiro:.2f}\n")
        f.write(f"Pix: R$ {pix:.2f}\n")
        f.write(f"Crédito: R$ {credito:.2f}\n")
        f.write(f"Débito: R$ {debito:.2f}\n")
        f.write("\n" + "-" * 45 + "\n")
        f.write(f"TOTAL GERAL: R$ {total_geral:.2f}\n")
        f.write("-" * 45 + "\n")


def fechar():
    salvar()
    app.destroy()

# ================= INTERFACE =================

app = ctk.CTk()
app.title("Caixa - Depósito")
app.geometry("1050x760")
app.protocol("WM_DELETE_WINDOW", fechar)

# ===== ESQUERDA =====
frame_esq = ctk.CTkFrame(app)
frame_esq.pack(side="left", fill="both", expand=True, padx=10, pady=10)

ctk.CTkLabel(frame_esq, text="Código do Produto", font=("Arial", 16)).pack(pady=(15, 5))

entrada = ctk.CTkEntry(
    frame_esq,
    font=("Arial", 22),
    placeholder_text="Escaneie o produto"
)
entrada.pack(pady=5, padx=20, fill="x")
entrada.bind("<Return>", ler_codigo)

# quantidade
ctk.CTkLabel(frame_esq, text="Quantidade (opcional)", font=("Arial", 16)).pack(pady=(10, 5))

entrada_qtd = ctk.CTkEntry(
    frame_esq,
    width=120,
    font=("Arial", 20),
    placeholder_text="1"
)
entrada_qtd.pack(pady=5)

label_produto = ctk.CTkLabel(
    frame_esq,
    text="Aguardando produto...",
    font=("Arial", 18)
)
label_produto.pack(pady=10)

ctk.CTkLabel(frame_esq, text="TOTAL", font=("Arial", 16)).pack()
label_total = ctk.CTkLabel(
    frame_esq,
    text="R$ 0.00",
    font=("Arial", 38, "bold"),
    text_color="green"
)
label_total.pack(pady=8)

ctk.CTkLabel(frame_esq, text="Itens da Compra", font=("Arial", 16)).pack(pady=(8, 5))
lista_itens = ctk.CTkTextbox(frame_esq, height=220)
lista_itens.pack(padx=10, pady=5, fill="both")

# botões
frame_btn = ctk.CTkFrame(frame_esq)
frame_btn.pack(pady=8)

ctk.CTkButton(
    frame_btn,
    text="Pix",
    width=120,
    command=lambda: finalizar("Pix")
).grid(row=0, column=0, padx=5, pady=5)

ctk.CTkButton(
    frame_btn,
    text="Crédito",
    width=120,
    command=lambda: finalizar("Crédito")
).grid(row=0, column=1, padx=5, pady=5)

ctk.CTkButton(
    frame_btn,
    text="Débito",
    width=120,
    command=lambda: finalizar("Débito")
).grid(row=1, column=0, padx=5, pady=5)

ctk.CTkButton(
    frame_btn,
    text="Remover",
    width=120,
    fg_color="orange",
    command=remover_item
).grid(row=1, column=1, padx=5, pady=5)

ctk.CTkButton(
    frame_btn,
    text="Cancelar",
    width=250,
    fg_color="red",
    command=cancelar_compra
).grid(row=2, column=0, columnspan=2, pady=5)

ctk.CTkButton(
    frame_btn,
    text="Dinheiro",
    width=250,
    fg_color="green",
    command=mostrar_dinheiro
).grid(row=3, column=0, columnspan=2, pady=5)

# dinheiro
frame_dinheiro = ctk.CTkFrame(frame_esq)

ctk.CTkLabel(frame_dinheiro, text="Valor recebido", font=("Arial", 16)).pack(pady=(8, 5))

entrada_dinheiro = ctk.CTkEntry(frame_dinheiro, font=("Arial", 20))
entrada_dinheiro.pack(pady=5, fill="x", padx=10)
entrada_dinheiro.bind("<KeyRelease>", calcular_troco)

label_troco = ctk.CTkLabel(
    frame_dinheiro,
    text="R$ 0.00",
    font=("Arial", 32, "bold"),
    text_color="green"
)
label_troco.pack(pady=8)

ctk.CTkButton(
    frame_dinheiro,
    text="Confirmar",
    command=confirmar_dinheiro
).pack(pady=(5, 10))

# ===== DIREITA =====
frame_dir = ctk.CTkFrame(app)
frame_dir.pack(side="right", fill="both", expand=True, padx=10, pady=10)

ctk.CTkLabel(frame_dir, text="Vendas do Dia", font=("Arial", 18)).pack(pady=10)

lista_vendas = ctk.CTkTextbox(frame_dir)
lista_vendas.pack(fill="both", expand=True, padx=10, pady=10)

resumo = ctk.CTkLabel(frame_dir, text="TOTAL: R$ 0.00", font=("Arial", 16))
resumo.pack(pady=10)

entrada.focus()

app.mainloop()