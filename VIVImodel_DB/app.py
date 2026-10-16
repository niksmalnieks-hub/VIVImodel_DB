
import tkinter as tk
from tkinter import ttk, messagebox
 
from funkcijas import (
    add_vilciens,
    get_vilcieni,
    get_vilciens,
    delete_vilciens,
    update_vilciens,
)
 
# None = pievienojam jaunu, citādi labojam šo ID
selected_id = None
 
 
def refresh():
    """Pārlādē vilcienu sarakstu tabulā."""
    for item in tree.get_children():
        tree.delete(item)
 
    for row in get_vilcieni():
        values = ["" if value is None else value for value in row]
        tree.insert("", tk.END, iid=str(row[0]), values=values)
 
 
def clear_form():
    global selected_id
    selected_id = None
 
    for entry in (model_input, number_input, built_input,
                  category_input, info_input):
        entry.delete(0, tk.END)
 
    form_block.config(text="Pievienot vilcienu")
    save_button.config(text="Saglabāt")
 
 
def save():
    try:
        if selected_id is None:
            add_vilciens(
                model_input.get(), number_input.get(),
                built_input.get(), category_input.get(),
                info_input.get(),
            )
            message = "Vilciens pievienots!"
        else:
            update_vilciens(
                selected_id, model_input.get(), number_input.get(),
                built_input.get(), category_input.get(),
                info_input.get(),
            )
            message = "Vilciens atjaunināts!"
    except ValueError as error:
        messagebox.showerror("Kļūda", str(error))
        return
 
    clear_form()
    refresh()
    result.config(text=message)
    tabs.select(list_tab)
 
 
def edit_selected():
    global selected_id
 
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("Uzmanību", "Izvēlies vilcienu no saraksta!")
        return
 
    train = get_vilciens(int(selection[0]))
    if train is None:
        return
 
    clear_form()
    selected_id = train[0]
 
    values = ["" if value is None else str(value) for value in train[1:]]
    for entry, value in zip(
        (model_input, number_input, built_input,
         category_input, info_input),
        values,
    ):
        entry.insert(0, value)
 
    form_block.config(text=f"Labot vilcienu (ID {selected_id})")
    save_button.config(text="Saglabāt izmaiņas")
    tabs.select(form_tab)
 
 
def delete_selected():
    selection = tree.selection()
    if not selection:
        messagebox.showwarning("Uzmanību", "Izvēlies vilcienu no saraksta!")
        return
 
    if messagebox.askyesno("Dzēst", "Vai tiešām dzēst izvēlēto vilcienu?"):
        delete_vilciens(int(selection[0]))
        refresh()
        result.config(text="Vilciens izdzēsts!")
 
 
# ---------------- Logs ----------------
window = tk.Tk()
window.title("Vilcienu datubāze")
window.geometry("900x500")
 
tk.Label(
    window, text="Vilcienu datubāze", font=("Arial", 20, "bold")
).pack(pady=10)
 
tabs = ttk.Notebook(window)
tabs.pack(fill="both", expand=True, padx=10, pady=5)
 
list_tab = ttk.Frame(tabs)
form_tab = ttk.Frame(tabs)
tabs.add(list_tab, text="Vilcieni")
tabs.add(form_tab, text="Pievienot / Labot")
 
# ---------------- Saraksta cilne ----------------
columns = ("id", "modelis", "numurs", "built", "category", "info")
headings = ("ID", "Modelis", "Numurs", "Uzbūvēts", "Kategorija", "Info")
widths = (50, 150, 100, 90, 120, 300)
 
tree = ttk.Treeview(list_tab, columns=columns, show="headings")
for column, heading, width in zip(columns, headings, widths):
    tree.heading(column, text=heading)
    tree.column(column, width=width, anchor="w")
 
scrollbar = ttk.Scrollbar(list_tab, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
 
tree.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="left", fill="y")
 
buttons = tk.Frame(list_tab)
buttons.pack(side="left", fill="y", padx=10)
 
tk.Button(buttons, text="Labot", width=12,
          command=edit_selected).pack(pady=5)
tk.Button(buttons, text="Dzēst", width=12,
          command=delete_selected).pack(pady=5)
tk.Button(buttons, text="Atsvaidzināt", width=12,
          command=refresh).pack(pady=5)
 
# ---------------- Formas cilne ----------------
form_block = tk.LabelFrame(
    form_tab, text="Pievienot vilcienu", padx=10, pady=10
)
form_block.pack(fill="x", padx=20, pady=20)
 
 
def make_field(label):
    tk.Label(form_block, text=label).pack()
    entry = tk.Entry(form_block, width=60)
    entry.pack(pady=5)
    return entry
 
 
model_input = make_field("Modelis *")
number_input = make_field("Numurs *")
built_input = make_field("Uzbūves gads")
category_input = make_field("Kategorija")
info_input = make_field("Info")
 
button_row = tk.Frame(form_block)
button_row.pack(pady=5)
 
save_button = tk.Button(button_row, text="Saglabāt", command=save)
save_button.pack(side="left", padx=5)
tk.Button(button_row, text="Notīrīt", command=clear_form).pack(
    side="left", padx=5
)
 
# Ziņojums apakšā
result = tk.Label(window, text="", fg="green")
result.pack(pady=5)
 
refresh()
window.mainloop()