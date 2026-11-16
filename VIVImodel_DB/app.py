import os
import tkinter as tk
from tkinter import ttk, messagebox

import funkcijas as f
from funkcijas import STATUSI


LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "vivi_logo.png")
VIVI_YELLOW = "#F7B500"
VIVI_DARK = "#2E3138"


def ask_delete(parent, question):
    """
    Jā/Nē logs ar VIVI logo augšējā kreisajā stūrī un teksta lauku.
    Atgriež (True/False, ievadītais teksts).
    """
    answer = {"yes": False, "text": ""}

    dialog = tk.Toplevel(parent)
    dialog.title("Dzēst")
    dialog.resizable(False, False)
    dialog.transient(parent)

    # Augšējā josla ar logo kreisajā pusē
    header = tk.Frame(dialog, bg=VIVI_YELLOW)
    header.pack(fill="x")

    try:
        dialog.logo = tk.PhotoImage(file=LOGO_PATH)
        tk.Label(header, image=dialog.logo, bg=VIVI_YELLOW,
                 bd=0).pack(side="left", padx=8, pady=8)
    except tk.TclError:
        pass  # ja logo fails nav atrasts, logs tāpat darbojas

    tk.Label(header, text="Apstiprināt dzēšanu", bg=VIVI_YELLOW,
             fg=VIVI_DARK, font=("Arial", 14, "bold")).pack(
        side="left", padx=10)

    # Saturs
    body = tk.Frame(dialog, padx=20, pady=15)
    body.pack(fill="both", expand=True)

    tk.Label(body, text=question, font=("Arial", 11)).pack(anchor="w")

    tk.Label(body, text="Piezīme / iemesls (nav obligāts):").pack(
        anchor="w", pady=(12, 2))
    text_input = tk.Entry(body, width=45)
    text_input.pack(fill="x")
    text_input.focus_set()

    def yes():
        answer["yes"] = True
        answer["text"] = text_input.get().strip()
        dialog.destroy()

    def no():
        dialog.destroy()

    buttons_row = tk.Frame(body)
    buttons_row.pack(pady=(15, 0))
    tk.Button(buttons_row, text="Jā", width=10, command=yes).pack(
        side="left", padx=5)
    tk.Button(buttons_row, text="Nē", width=10, command=no).pack(
        side="left", padx=5)

    dialog.bind("<Return>", lambda event: yes())
    dialog.bind("<Escape>", lambda event: no())
    dialog.protocol("WM_DELETE_WINDOW", no)

    # Novietojam loga vidū un bloķējam galveno logu, kamēr atbild
    dialog.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width()
                                - dialog.winfo_width()) // 2
    y = parent.winfo_rooty() + (parent.winfo_height()
                                - dialog.winfo_height()) // 2
    dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    dialog.grab_set()
    parent.wait_window(dialog)

    return answer["yes"], answer["text"]


# ---------------------------------------------------------------
#  Vienota cilne: forma augšā (Pievienot / Labot) + saraksts zemāk
# ---------------------------------------------------------------
class Section:
    """
    cfg["fields"] = (atslēga, uzraksts, rinda, kolonna, platums, veids, avots)
      veids: "text"       - parasts teksta lauks
             "fixed"      - izvēlne no fiksēta saraksta (avots = tuple)
             "choice"     - obligāta izvēle no citas tabulas (avots = funkcija)
             "choice_opt" - neobligāta izvēle no citas tabulas
    """

    def __init__(self, tabs, cfg):
        self.cfg = cfg
        self.selected_id = None
        self.widgets = {}
        self.choices = {}

        self.tab = ttk.Frame(tabs)
        tabs.add(self.tab, text=cfg["tab"])

        # ---------- Forma ----------
        self.form = tk.LabelFrame(
            self.tab, text=cfg["add_title"], padx=10, pady=8)
        self.form.pack(fill="x", padx=10, pady=(10, 5))
        self.form.columnconfigure(0, weight=1)
        self.form.columnconfigure(1, weight=1)

        for key, label, row, col, span, kind, source in cfg["fields"]:
            cell = tk.Frame(self.form)
            cell.grid(row=row, column=col, columnspan=span,
                      sticky="ew", padx=10, pady=3)
            tk.Label(cell, text=label).pack(anchor="w")

            if kind == "text":
                widget = tk.Entry(cell)
            elif kind == "fixed":
                widget = ttk.Combobox(cell, values=source, state="readonly")
            else:
                widget = ttk.Combobox(cell, state="readonly")
            widget.pack(fill="x")
            self.widgets[key] = widget

        last_row = max(field[2] for field in cfg["fields"]) + 1
        button_row = tk.Frame(self.form)
        button_row.grid(row=last_row, column=0, columnspan=2, pady=(8, 0))
        self.save_button = tk.Button(
            button_row, text="Saglabāt", width=16, command=self.save)
        self.save_button.pack(side="left", padx=5)
        tk.Button(button_row, text="Notīrīt", width=16,
                  command=self.clear).pack(side="left", padx=5)

        # ---------- Saraksts ----------
        list_frame = tk.Frame(self.tab)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        columns = [f"c{i}" for i in range(len(cfg["headings"]))]
        self.tree = ttk.Treeview(list_frame, columns=columns,
                                 show="headings")
        for column, heading, width in zip(
                columns, cfg["headings"], cfg["widths"]):
            self.tree.heading(column, text=heading)
            self.tree.column(column, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")

        side = tk.Frame(list_frame)
        side.pack(side="left", fill="y", padx=10)
        tk.Button(side, text="Labot", width=12,
                  command=self.edit).pack(pady=5)
        tk.Button(side, text="Dzēst", width=12,
                  command=self.delete).pack(pady=5)
        tk.Button(side, text="Atsvaidzināt", width=12,
                  command=refresh_all).pack(pady=5)

        self.refresh_choices()
        self.clear()

    # ---------- Lauku apstrāde ----------
    def refresh_choices(self):
        """Pārlādē izvēlņu saturu no datubāzes (citu tabulu ieraksti)."""
        for key, _l, _r, _c, _s, kind, source in self.cfg["fields"]:
            if kind not in ("choice", "choice_opt"):
                continue
            items = source()
            self.choices[key] = items
            texts = [text for _id, text in items]
            if kind == "choice_opt":
                texts = [""] + texts
            widget = self.widgets[key]
            widget["values"] = texts
            if widget.get() not in texts:
                widget.set("")

    def get_value(self, key, kind):
        widget = self.widgets[key]
        if kind in ("choice", "choice_opt"):
            for item_id, text in self.choices[key]:
                if text == widget.get():
                    return item_id
            return None
        return widget.get()

    def set_value(self, key, kind, value):
        widget = self.widgets[key]
        if kind in ("choice", "choice_opt"):
            text = ""
            for item_id, item_text in self.choices[key]:
                if item_id == value:
                    text = item_text
            widget.set(text)
        elif kind == "fixed":
            widget.set(value or "")
        else:
            widget.delete(0, tk.END)
            widget.insert(0, "" if value is None else str(value))

    def clear(self):
        self.selected_id = None
        for key, _l, _r, _c, _s, kind, source in self.cfg["fields"]:
            if kind == "fixed":
                self.widgets[key].set(source[0])
            elif kind == "text":
                self.widgets[key].delete(0, tk.END)
            else:
                self.widgets[key].set(
                    self.cfg.get("defaults", {}).get(key, ""))
        self.form.config(text=self.cfg["add_title"])
        self.save_button.config(text="Saglabāt")

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.cfg["list"]():
            values = ["" if value is None else value for value in row]
            self.tree.insert("", tk.END, iid=str(row[0]), values=values)

    # ---------- Darbības ----------
    def save(self):
        data = {field[0]: self.get_value(field[0], field[5])
                for field in self.cfg["fields"]}
        try:
            if self.selected_id is None:
                self.cfg["add"](**data)
                message = self.cfg["added_msg"]
            else:
                self.cfg["update"](self.selected_id, **data)
                message = self.cfg["updated_msg"]
        except ValueError as error:
            messagebox.showerror("Kļūda", str(error))
            return

        self.clear()
        refresh_all()
        result.config(text=message)

    def edit(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Uzmanību", "Izvēlies ierakstu no saraksta!")
            return

        record = self.cfg["get"](int(selection[0]))
        if record is None:
            return

        self.clear()
        self.selected_id = int(selection[0])
        for key, _l, _r, _c, _s, kind, _src in self.cfg["fields"]:
            self.set_value(key, kind, record.get(key))

        self.form.config(
            text=f"{self.cfg['edit_title']} (ID {self.selected_id})")
        self.save_button.config(text="Saglabāt izmaiņas")

    def delete(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Uzmanību", "Izvēlies ierakstu no saraksta!")
            return

        confirmed, note = ask_delete(window, self.cfg["delete_q"])
        if not confirmed:
            return

        try:
            self.cfg["delete"](int(selection[0]))
        except ValueError as error:
            messagebox.showerror("Nevar dzēst", str(error))
            return

        if self.selected_id == int(selection[0]):
            self.clear()
        refresh_all()
        message = self.cfg["deleted_msg"]
        if note:
            message += f" Piezīme: {note}"
        result.config(text=message)


def refresh_all():
    """Pārlādē visus sarakstus un izvēlnes (tabulas ir saistītas)."""
    for section in sections:
        section.refresh_choices()
        section.refresh_list()


# ---------------------------------------------------------------
#  Logs
# ---------------------------------------------------------------
window = tk.Tk()
window.title("Vilcienu datubāze")
window.geometry("1300x720")

# ---------------------------------------------------------------
#  Augšējā josla: VIVI logo vidū, divi vilcieni griežas ap sevi
#  (kreisajā un labajā pusē)
# ---------------------------------------------------------------
MAPE = os.path.dirname(os.path.abspath(__file__))
JOSLAS_AUGSTUMS = 130
VILCIENA_KADRI = 36        # kadri vienā pilnā apgriezienā
KADRA_LAIKS = 50           # ms uz kadru


def load_frames(file_name):
    path = os.path.join(MAPE, file_name)
    return [tk.PhotoImage(file=path, format=f"gif -index {i}")
            for i in range(VILCIENA_KADRI)]


def create_banner(parent):
    banner = tk.Canvas(parent, height=JOSLAS_AUGSTUMS, bg="black",
                       highlightthickness=0)
    banner.pack(fill="x")
    y = JOSLAS_AUGSTUMS // 2

    try:
        banner.logo = tk.PhotoImage(
            file=os.path.join(MAPE, "vivi_logo_josla.png"))
        banner.left_frames = load_frames("vilciens_kreisais.gif")
        banner.right_frames = load_frames("vilciens_labais.gif")
    except tk.TclError:
        # Ja attēlu faili nav atrasti, rāda tikai tekstu
        banner.create_text(20, y, anchor="w", fill="#F7B500",
                           font=("Arial", 20, "bold"),
                           text="Vilcienu datubāze")
        return banner

    logo_item = banner.create_image(0, y, image=banner.logo)
    left_item = banner.create_image(
        0, y, image=banner.left_frames[0])
    right_item = banner.create_image(
        0, y, image=banner.right_frames[0])

    def place(event=None):
        width = banner.winfo_width()
        banner.coords(logo_item, width // 2, y)
        banner.coords(left_item, 20 + 62, y)            # augšā pa kreisi
        banner.coords(right_item, width - 20 - 62, y)   # augšā pa labi

    def animate(index=0):
        banner.itemconfigure(left_item, image=banner.left_frames[index])
        banner.itemconfigure(right_item, image=banner.right_frames[index])
        banner.after(KADRA_LAIKS, animate, (index + 1) % VILCIENA_KADRI)

    banner.bind("<Configure>", place)
    place()
    animate()
    return banner


create_banner(window)

tabs = ttk.Notebook(window)
tabs.pack(fill="both", expand=True, padx=10, pady=5)

result = tk.Label(window, text="", fg="green")
result.pack(pady=5)

sections = [
    Section(tabs, {
        "tab": "Vilcieni",
        "add_title": "Pievienot vilcienu",
        "edit_title": "Labot vilcienu",
        "fields": [
            ("numurs", "Numurs *", 0, 0, 1, "text",
             None),
            ("modelis_id", "Modelis", 0, 1, 1, "choice_opt",
             f.get_modeli_izvele),
            ("kategorija_id", "Kategorija", 1, 0, 1, "choice_opt",
             f.get_kategoriju_izvele),
            ("depo_id", "Depo", 1, 1, 1, "choice_opt",
             f.get_depo_izvele),
            ("statuss", "Ekspluatācijā / Nestrādā", 2, 0, 1, "fixed",
             STATUSI),
            ("izlaiduma_gads", "Izlaiduma gads", 2, 1, 1, "text",
             None),
        ],
        "headings": ("ID", "Numurs", "Modelis", "Ražotājs", "Kategorija", "Max km/h", "Izlaiduma gads", "Statuss", "Depo"),
        "widths": (45, 100, 120, 150, 130, 80, 110, 110, 150),
        "list": f.get_vilcieni, "get": f.get_vilciens,
        "add": f.add_vilciens, "update": f.update_vilciens,
        "delete": f.delete_vilciens,
        "delete_q": "Vai tiešām dzēst izvēlēto vilcienu?",
        "added_msg": "Vilciens pievienots!",
        "updated_msg": "Vilciens atjaunināts!",
        "deleted_msg": "Vilciens izdzēsts!",
    }),
    Section(tabs, {
        "tab": "Modeļi",
        "add_title": "Pievienot modeli",
        "edit_title": "Labot modeli",
        "fields": [
            ("nosaukums", "Modeļa nosaukums *", 0, 0, 1, "text",
             None),
            ("razotajs", "Ražotājs", 0, 1, 1, "text",
             None),
            ("ietilpiba", "Ietilpība", 1, 0, 1, "text",
             None),
            ("maksimalais_atrums", "Maksimālais ātrums (km/h)", 1, 1, 1, "text",
             None),
        ],
        "headings": ("ID", "Modelis", "Ražotājs", "Ietilpība", "Max km/h", "Vilcienu skaits"),
        "widths": (45, 200, 250, 100, 100, 110),
        "list": f.get_modeli, "get": f.get_modelis,
        "add": f.add_modelis, "update": f.update_modelis,
        "delete": f.delete_modelis,
        "delete_q": "Vai tiešām dzēst izvēlēto modeli?",
        "added_msg": "Modelis pievienots!",
        "updated_msg": "Modelis atjaunināts!",
        "deleted_msg": "Modelis izdzēsts!",
    }),
    Section(tabs, {
        "tab": "Kategorijas",
        "add_title": "Pievienot kategoriju",
        "edit_title": "Labot kategoriju",
        "fields": [
            ("nosaukums", "Kategorijas nosaukums *", 0, 0, 2, "text",
             None),
            ("apraksts", "Apraksts", 1, 0, 2, "text",
             None),
        ],
        "headings": ("ID", "Kategorija", "Apraksts", "Vilcienu skaits"),
        "widths": (45, 250, 450, 110),
        "list": f.get_kategorijas, "get": f.get_kategorija,
        "add": f.add_kategorija, "update": f.update_kategorija,
        "delete": f.delete_kategorija,
        "delete_q": "Vai tiešām dzēst izvēlēto kategoriju?",
        "added_msg": "Kategorija pievienota!",
        "updated_msg": "Kategorija atjaunināta!",
        "deleted_msg": "Kategorija izdzēsta!",
    }),
    Section(tabs, {
        "tab": "Depo",
        "add_title": "Pievienot depo",
        "edit_title": "Labot depo",
        "fields": [
            ("nosaukums", "Depo nosaukums *", 0, 0, 1, "text",
             None),
            ("adrese", "Adrese", 0, 1, 1, "text",
             None),
            ("ietilpiba", "Ietilpība", 1, 0, 1, "text",
             None),
        ],
        "headings": ("ID", "Depo", "Adrese", "Ietilpība", "Vilcienu skaits"),
        "widths": (45, 250, 350, 100, 110),
        "list": f.get_depo_saraksts, "get": f.get_depo,
        "add": f.add_depo, "update": f.update_depo,
        "delete": f.delete_depo,
        "delete_q": "Vai tiešām dzēst izvēlēto depo?",
        "added_msg": "Depo pievienots!",
        "updated_msg": "Depo atjaunināts!",
        "deleted_msg": "Depo izdzēsts!",
    }),
    Section(tabs, {
        "tab": "Līnijas",
        "add_title": "Pievienot līniju",
        "edit_title": "Labot līniju",
        "fields": [
            ("nosaukums", "Līnijas nosaukums *", 0, 0, 2, "text",
             None),
            ("sakuma_stacija", "Sākuma stacija", 1, 0, 1, "text",
             None),
            ("beigu_stacija", "Beigu stacija", 1, 1, 1, "text",
             None),
            ("garums_km", "Garums (km)", 2, 0, 1, "text",
             None),
        ],
        "headings": ("ID", "Līnija", "Sākuma stacija", "Beigu stacija", "Garums km"),
        "widths": (45, 250, 200, 200, 100),
        "list": f.get_linijas, "get": f.get_linija,
        "add": f.add_linija, "update": f.update_linija,
        "delete": f.delete_linija,
        "delete_q": "Vai tiešām dzēst izvēlēto līniju?",
        "added_msg": "Līnija pievienota!",
        "updated_msg": "Līnija atjaunināta!",
        "deleted_msg": "Līnija izdzēsta!",
    }),
    Section(tabs, {
        "tab": "Sastāvi",
        "add_title": "Pievienot sastāvu",
        "edit_title": "Labot sastāvu",
        "fields": [
            ("vilciens_id", "Vilciens *", 0, 0, 1, "choice",
             f.get_vilcienu_izvele),
            ("linija_id", "Līnija", 0, 1, 1, "choice_opt",
             f.get_linijas_izvele),
            ("vagonu_skaits", "Vagonu skaits", 1, 0, 1, "text",
             None),
            ("ietilpiba", "Ietilpība", 1, 1, 1, "text",
             None),
        ],
        "headings": ("ID", "Vilciens", "Līnija", "Vagonu skaits", "Ietilpība"),
        "widths": (45, 200, 250, 110, 100),
        "list": f.get_sastavi, "get": f.get_sastavs,
        "add": f.add_sastavs, "update": f.update_sastavs,
        "delete": f.delete_sastavs,
        "delete_q": "Vai tiešām dzēst izvēlēto sastāvu?",
        "added_msg": "Sastāvs pievienots!",
        "updated_msg": "Sastāvs atjaunināts!",
        "deleted_msg": "Sastāvs izdzēsts!",
    }),
    Section(tabs, {
        "tab": "Laiki",
        "add_title": "Pievienot laiku",
        "edit_title": "Labot laiku",
        "fields": [
            ("vilciens_id", "Vilciens *", 0, 0, 1, "choice",
             f.get_vilcienu_izvele),
            ("linija_id", "Līnija *", 0, 1, 1, "choice",
             f.get_linijas_izvele),
            ("atiesanas_laiks", "Atiešanas laiks (GGGG-MM-DD HH:MM)", 1, 0, 1, "text",
             None),
            ("pienaksanas_laiks", "Pienākšanas laiks (GGGG-MM-DD HH:MM)", 1, 1, 1, "text",
             None),
        ],
        "headings": ("ID", "Vilciens", "Līnija", "Atiešana", "Pienākšana"),
        "widths": (45, 200, 250, 170, 170),
        "list": f.get_laiki, "get": f.get_laiks,
        "add": f.add_laiks, "update": f.update_laiks,
        "delete": f.delete_laiks,
        "delete_q": "Vai tiešām dzēst izvēlēto laiku?",
        "added_msg": "Laiks pievienots!",
        "updated_msg": "Laiks atjaunināts!",
        "deleted_msg": "Laiks izdzēsts!",
    }),
    Section(tabs, {
        "tab": "Vadītāji",
        "add_title": "Pievienot vilciena vadītāju",
        "edit_title": "Labot vilciena vadītāju",
        "fields": [
            ("vards", "Vārds *", 0, 0, 1, "text",
             None),
            ("uzvards", "Uzvārds *", 0, 1, 1, "text",
             None),
            ("personas_kods", "Personas kods", 1, 0, 1, "text",
             None),
            ("telefons", "Telefons", 1, 1, 1, "text",
             None),
            ("epasts", "E-pasts", 2, 0, 1, "text",
             None),
            ("alga_id", "Alga", 2, 1, 1, "choice_opt",
             f.get_algu_izvele),
        ],
        "headings": ("ID", "Vārds", "Uzvārds", "Personas kods", "Telefons", "E-pasts", "Alga", "Izveidots"),
        "widths": (45, 110, 130, 120, 110, 180, 120, 140),
        "list": f.get_vaditaji, "get": f.get_vaditajs,
        "add": f.add_vaditajs, "update": f.update_vaditajs,
        "delete": f.delete_vaditajs,
        "delete_q": "Vai tiešām dzēst izvēlēto vadītāju?",
        "added_msg": "Vadītājs pievienots!",
        "updated_msg": "Vadītājs atjaunināts!",
        "deleted_msg": "Vadītājs izdzēsts!",
    }),
    Section(tabs, {
        "tab": "Algas",
        "add_title": "Pievienot algu",
        "edit_title": "Labot algu",
        "fields": [
            ("vaditajs_id", "Vadītājs *", 0, 0, 1, "choice",
             f.get_vaditaju_izvele),
            ("summa", "Summa *", 0, 1, 1, "text",
             None),
            ("valuta", "Valūta", 1, 0, 1, "text",
             None),
            ("datums", "Datums (GGGG-MM-DD)", 1, 1, 1, "text",
             None),
        ],
        "headings": ("ID", "Vadītājs", "Summa", "Valūta", "Datums"),
        "widths": (45, 250, 120, 80, 120),
        "list": f.get_algas, "get": f.get_alga,
        "add": f.add_alga, "update": f.update_alga,
        "delete": f.delete_alga,
        "delete_q": "Vai tiešām dzēst izvēlēto algu?",
        "added_msg": "Alga pievienota!",
        "updated_msg": "Alga atjaunināta!",
        "deleted_msg": "Alga izdzēsta!",
    }),
    Section(tabs, {
        "tab": "Darba grafiks",
        "add_title": "Pievienot darba grafiku",
        "edit_title": "Labot darba grafiku",
        "fields": [
            ("vaditajs_id", "Vadītājs *", 0, 0, 1, "choice",
             f.get_vaditaju_izvele),
            ("vilciens_id", "Vilciens", 0, 1, 1, "choice_opt",
             f.get_vilcienu_izvele),
            ("linija_id", "Līnija", 1, 0, 1, "choice_opt",
             f.get_linijas_izvele),
            ("darba_sakums", "Darba sākums (GGGG-MM-DD HH:MM)", 1, 1, 1, "text",
             None),
            ("darba_beigas", "Darba beigas (GGGG-MM-DD HH:MM)", 2, 0, 1, "text",
             None),
        ],
        "headings": ("ID", "Vadītājs", "Vilciens", "Līnija", "Darba sākums", "Darba beigas"),
        "widths": (45, 200, 120, 200, 150, 150),
        "list": f.get_grafiki, "get": f.get_grafiks,
        "add": f.add_grafiks, "update": f.update_grafiks,
        "delete": f.delete_grafiks,
        "delete_q": "Vai tiešām dzēst izvēlēto darba grafiku?",
        "added_msg": "Darba grafiks pievienots!",
        "updated_msg": "Darba grafiks atjaunināts!",
        "deleted_msg": "Darba grafiks izdzēsts!",
    }),
    Section(tabs, {
        "tab": "Vadītāju vilcieni",
        "add_title": "Piesaistīt vadītāju vilcienam",
        "edit_title": "Labot piesaisti",
        "fields": [
            ("vaditajs_id", "Vadītājs *", 0, 0, 1, "choice",
             f.get_vaditaju_izvele),
            ("vilciens_id", "Vilciens *", 0, 1, 1, "choice",
             f.get_vilcienu_izvele),
        ],
        "headings": ("ID", "Vadītājs", "Vilciens", "Piesaistīts"),
        "widths": (45, 250, 250, 160),
        "list": f.get_vaditaju_vilcieni, "get": f.get_vaditaja_vilciens,
        "add": f.add_vaditaja_vilciens, "update": f.update_vaditaja_vilciens,
        "delete": f.delete_vaditaja_vilciens,
        "delete_q": "Vai tiešām noņemt izvēlēto piesaisti?",
        "added_msg": "Vadītājs piesaistīts vilcienam!",
        "updated_msg": "Piesaiste atjaunināta!",
        "deleted_msg": "Piesaiste noņemta!",
    }),
    Section(tabs, {
        "tab": "Remonti",
        "add_title": "Pievienot remontu",
        "edit_title": "Labot remontu",
        "fields": [
            ("vilciens_id", "Vilciens *", 0, 0, 1, "choice",
             f.get_vilcienu_izvele),
            ("remontdarbu_veids", "Remontdarbu veids", 0, 1, 1, "text",
             None),
            ("sakuma_datums", "Sākuma datums (GGGG-MM-DD)", 1, 0, 1, "text",
             None),
            ("beigu_datums", "Beigu datums (GGGG-MM-DD)", 1, 1, 1, "text",
             None),
            ("izmaksas", "Izmaksas", 2, 0, 1, "text",
             None),
            ("statuss", "Statuss", 2, 1, 1, "text",
             None),
        ],
        "headings": ("ID", "Vilciens", "Remontdarbu veids", "Sākums", "Beigas", "Izmaksas", "Statuss"),
        "widths": (45, 130, 300, 100, 100, 100, 130),
        "list": f.get_remonti, "get": f.get_remonts,
        "add": f.add_remonts, "update": f.update_remonts,
        "delete": f.delete_remonts,
        "delete_q": "Vai tiešām dzēst izvēlēto remontu?",
        "added_msg": "Remonts pievienots!",
        "updated_msg": "Remonts atjaunināts!",
        "deleted_msg": "Remonts izdzēsts!",
    }),
]

# Mainot cilni, izvēlnes atjaunojas (piem., jauni modeļi parādās vilcienu formā)
tabs.bind("<<NotebookTabChanged>>", lambda event: refresh_all())

refresh_all()
if f.PAREJAS_PAZINOJUMS:
    result.config(text=f.PAREJAS_PAZINOJUMS)

if __name__ == "__main__":
    window.mainloop()
