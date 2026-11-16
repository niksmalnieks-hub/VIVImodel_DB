import os
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "vilcieni.db")

STATUSI = ("Ekspluatācijā", "Nestrādā")

# Ziņojums, ko programma parāda pēc pārejas no vecās datubāzes
PAREJAS_PAZINOJUMS = ""

# 12 tabulas (shēma: shema_12_tabulas.dbml)
SHEMA = """
CREATE TABLE IF NOT EXISTS Kategorija (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT NOT NULL,
    apraksts TEXT
);

CREATE TABLE IF NOT EXISTS Modelis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT NOT NULL,
    razotajs TEXT,
    ietilpiba INTEGER,
    maksimalais_atrums INTEGER
);

CREATE TABLE IF NOT EXISTS Depo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT NOT NULL,
    adrese TEXT,
    ietilpiba INTEGER
);

CREATE TABLE IF NOT EXISTS Linija (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nosaukums TEXT NOT NULL,
    sakuma_stacija TEXT,
    beigu_stacija TEXT,
    garums_km NUMERIC
);

CREATE TABLE IF NOT EXISTS Vilciens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numurs TEXT NOT NULL UNIQUE,
    modelis_id INTEGER REFERENCES Modelis(id),
    depo_id INTEGER REFERENCES Depo(id),
    kategorija_id INTEGER REFERENCES Kategorija(id),
    statuss TEXT,
    izlaiduma_gads INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Vilciena_vaditajs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vards TEXT NOT NULL,
    uzvards TEXT NOT NULL,
    personas_kods TEXT UNIQUE,
    telefons TEXT,
    epasts TEXT,
    alga_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Alga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vaditajs_id INTEGER NOT NULL REFERENCES Vilciena_vaditajs(id),
    summa NUMERIC NOT NULL,
    valuta TEXT,
    datums DATE
);

CREATE TABLE IF NOT EXISTS Sastavs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vilciens_id INTEGER NOT NULL REFERENCES Vilciens(id),
    linija_id INTEGER REFERENCES Linija(id),
    vagonu_skaits INTEGER,
    ietilpiba INTEGER
);

CREATE TABLE IF NOT EXISTS Laiks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vilciens_id INTEGER NOT NULL REFERENCES Vilciens(id),
    linija_id INTEGER NOT NULL REFERENCES Linija(id),
    atiesanas_laiks TIMESTAMP,
    pienaksanas_laiks TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Darba_grafiks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vaditajs_id INTEGER NOT NULL REFERENCES Vilciena_vaditajs(id),
    vilciens_id INTEGER REFERENCES Vilciens(id),
    linija_id INTEGER REFERENCES Linija(id),
    darba_sakums TIMESTAMP,
    darba_beigas TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Vilciena_vaditajs_vilciens (
    vaditajs_id INTEGER NOT NULL
        REFERENCES Vilciena_vaditajs(id) ON DELETE CASCADE,
    vilciens_id INTEGER NOT NULL
        REFERENCES Vilciens(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (vaditajs_id, vilciens_id)
);

CREATE TABLE IF NOT EXISTS Remonti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vilciens_id INTEGER NOT NULL REFERENCES Vilciens(id),
    remontdarbu_veids TEXT,
    sakuma_datums DATE,
    beigu_datums DATE,
    izmaksas NUMERIC,
    statuss TEXT
);
"""


# ---------------------------------------------------------------
#  Pamata palīgfunkcijas
# ---------------------------------------------------------------
def connect():
    database = sqlite3.connect(DB_PATH)
    database.execute("PRAGMA foreign_keys = ON")
    database.row_factory = sqlite3.Row
    return database


def _run(sql, params=(), fk_kluda=None):
    """Izpilda INSERT/UPDATE/DELETE un pārvērš DB kļūdas par ValueError."""
    try:
        with closing(connect()) as database:
            with database:
                return database.execute(sql, params).lastrowid
    except sqlite3.IntegrityError as error:
        teksts = str(error)
        if "UNIQUE" in teksts or "PRIMARY KEY" in teksts:
            raise ValueError("Tāds ieraksts jau eksistē (numurs, personas "
                             "kods vai piesaiste atkārtojas)!")
        if "FOREIGN KEY" in teksts:
            raise ValueError(
                fk_kluda or "Ieraksts ir saistīts ar citiem ierakstiem!"
            )
        raise ValueError(teksts)


def _query(sql, params=()):
    with closing(connect()) as database:
        return database.execute(sql, params).fetchall()


def _one(sql, params=()):
    rows = _query(sql, params)
    return dict(rows[0]) if rows else None


def _izvele(sql):
    """Saraksts (id, teksts); atkārtotiem tekstiem pieliek (ID n)."""
    rindas = [(r[0], r[1] or "") for r in _query(sql)]
    skaits = {}
    for _id, teksts in rindas:
        skaits[teksts] = skaits.get(teksts, 0) + 1
    return [(i, t if skaits[t] == 1 else f"{t} (ID {i})")
            for i, t in rindas]


# ---------------------------------------------------------------
#  Lauku pārbaudes (katra atgriež sakārtotu vērtību vai met ValueError)
# ---------------------------------------------------------------
def _teksts(vertiba):
    return "" if vertiba is None else str(vertiba).strip()


def txt(vertiba):
    return _teksts(vertiba) or None


def txt_req(kas):
    def parbaude(vertiba):
        vertiba = _teksts(vertiba)
        if not vertiba:
            raise ValueError(f"{kas} ir obligāts!")
        return vertiba
    return parbaude


def int_(kas):
    def parbaude(vertiba):
        vertiba = _teksts(vertiba)
        if not vertiba:
            return None
        try:
            return int(vertiba)
        except ValueError:
            raise ValueError(f"{kas}: jāievada vesels skaitlis!")
    return parbaude


def dec(kas, obligats=False):
    def parbaude(vertiba):
        vertiba = _teksts(vertiba).replace(",", ".")
        if not vertiba:
            if obligats:
                raise ValueError(f"{kas} ir obligāta!")
            return None
        try:
            return float(vertiba)
        except ValueError:
            raise ValueError(f"{kas}: jāievada skaitlis (piem., 125.50)!")
    return parbaude


def fk_req(kas):
    def parbaude(vertiba):
        if vertiba in (None, ""):
            raise ValueError(f"Izvēlies: {kas}!")
        return vertiba
    return parbaude


def fk(vertiba):
    return vertiba or None


def datums(kas):
    def parbaude(vertiba):
        vertiba = _teksts(vertiba)
        if not vertiba:
            return None
        try:
            return datetime.strptime(vertiba, "%Y-%m-%d").date().isoformat()
        except ValueError:
            raise ValueError(f"{kas}: formāts GGGG-MM-DD (piem., 2026-11-01)!")
    return parbaude


def laiks(kas):
    def parbaude(vertiba):
        vertiba = _teksts(vertiba).replace("T", " ")
        if not vertiba:
            return None
        for formats in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(vertiba, formats).strftime(
                    "%Y-%m-%d %H:%M")
            except ValueError:
                pass
        raise ValueError(
            f"{kas}: formāts GGGG-MM-DD HH:MM (piem., 2026-11-01 08:30)!")
    return parbaude


def statuss(vertiba):
    vertiba = _teksts(vertiba) or STATUSI[0]
    if vertiba not in STATUSI:
        raise ValueError("Statuss: Ekspluatācijā vai Nestrādā!")
    return vertiba


class Tabula:
    """Vienkārša tabula: pievienot / labot / nolasīt / dzēst."""

    def __init__(self, tabula, kolonnas, fk_kluda=None, id_kol="id"):
        self.tabula = tabula
        self.kolonnas = kolonnas          # [(kolonna, pārbaude), ...]
        self.fk_kluda = fk_kluda
        self.id_kol = id_kol              # savienojuma tabulai: "rowid"

    def _vertibas(self, dati):
        return tuple(parbaude(dati.get(nos))
                     for nos, parbaude in self.kolonnas)

    def add(self, **dati):
        vertibas = self._vertibas(dati)
        nosaukumi = ", ".join(n for n, _ in self.kolonnas)
        jautajumi = ", ".join("?" * len(self.kolonnas))
        return _run(
            f"INSERT INTO {self.tabula} ({nosaukumi}) "
            f"VALUES ({jautajumi})", vertibas, self.fk_kluda)

    def update(self, ieraksta_id, **dati):
        vertibas = self._vertibas(dati)
        sets = ", ".join(f"{n} = ?" for n, _ in self.kolonnas)
        _run(f"UPDATE {self.tabula} SET {sets} WHERE {self.id_kol} = ?",
             (*vertibas, ieraksta_id), self.fk_kluda)

    def get(self, ieraksta_id):
        nosaukumi = ", ".join(n for n, _ in self.kolonnas)
        return _one(f"SELECT {nosaukumi} FROM {self.tabula} "
                    f"WHERE {self.id_kol} = ?", (ieraksta_id,))

    def delete(self, ieraksta_id):
        _run(f"DELETE FROM {self.tabula} WHERE {self.id_kol} = ?",
             (ieraksta_id,), self.fk_kluda)


# ---------------------------------------------------------------
#  Datubāzes izveide un pāreja no vecākām struktūrām
# ---------------------------------------------------------------
# Vecās (1.–3. versijas) tabulas; bērni pirms vecākiem (dzēšanas secība)
VECAS_TABULAS = ("remonti", "vilcienu_linijas", "vilcieni", "lietotaji",
                 "linijas", "depo", "modeli", "rupnicas", "statusi",
                 "kategorijas")


def _tabulu_nosaukumi():
    if not os.path.exists(DB_PATH):
        return set()
    with closing(sqlite3.connect(DB_PATH)) as database:
        return {r[0].lower() for r in database.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'")}


def _backup():
    mape = os.path.dirname(DB_PATH)
    mervis = os.path.join(mape, "vilcieni_vecais_backup.db")
    nr = 2
    while os.path.exists(mervis):
        mervis = os.path.join(mape, f"vilcieni_vecais_backup_{nr}.db")
        nr += 1
    shutil.copyfile(DB_PATH, mervis)
    return os.path.basename(mervis)


def _get_or_create(database, tabula, nosaukums, papildu=None):
    rinda = database.execute(
        f"SELECT id FROM {tabula} WHERE nosaukums = ?", (nosaukums,)
    ).fetchone()
    if rinda:
        return rinda[0]
    papildu = papildu or {}
    kolonnas = ", ".join(["nosaukums", *papildu])
    jautajumi = ", ".join("?" * (1 + len(papildu)))
    return database.execute(
        f"INSERT INTO {tabula} ({kolonnas}) VALUES ({jautajumi})",
        (nosaukums, *papildu.values())
    ).lastrowid


def _veco_vilcienu_rindas(database):
    """Atgriež vecos vilcienus vienotā formā (neatkarīgi no versijas)."""
    kolonnas = {r[1] for r in
                database.execute("PRAGMA table_info(old_vilcieni)")}

    if "modelis" in kolonnas:                        # 1. versija
        rindas = []
        for r in database.execute(
                "SELECT * FROM old_vilcieni ORDER BY vilciens_id"):
            d = dict(r)
            rindas.append({
                "id": d["vilciens_id"], "numurs": d["numurs"],
                "modelis": d["modelis"], "kategorija": d.get("category"),
                "rupnica": d.get("rupnica"),
                "max_atrums": d.get("max_atrums"),
                "statuss": d.get("ekspluatacija"), "built": d.get("built"),
                "depo": None, "created_at": None,
            })
        return rindas

    if "statuss_id" in kolonnas:                     # 3. versija
        statuss = "s.nosaukums"
        depo = "d.nosaukums"
        joins = ("LEFT JOIN old_statusi s ON s.statuss_id = v.statuss_id "
                 "LEFT JOIN old_depo d ON d.depo_id = v.depo_id")
    else:                                            # 2. versija
        statuss, depo, joins = "v.statuss", "NULL", ""

    created = "v.created_at" if "created_at" in kolonnas else "NULL"
    sql = f"""
        SELECT v.vilciens_id AS id, v.numurs, m.nosaukums AS modelis,
               k.nosaukums AS kategorija, r.nosaukums AS rupnica,
               m.max_atrums, {statuss} AS statuss, v.built,
               {depo} AS depo, {created} AS created_at
        FROM old_vilcieni v
        JOIN old_modeli m ON m.modelis_id = v.modelis_id
        JOIN old_kategorijas k ON k.kategorija_id = m.kategorija_id
        LEFT JOIN old_rupnicas r ON r.rupnica_id = m.rupnica_id
        {joins}
        ORDER BY v.vilciens_id
    """
    return [dict(r) for r in database.execute(sql)]


def _parnest(database, veco_tabulas):
    """Pārnes datus no vecajām tabulām (old_*) uz jaunajām."""
    depo_ids, linijas_ids, modeli, kategorijas, vilcieni = {}, {}, {}, {}, {}
    izlaisti = 0

    if "depo" in veco_tabulas:
        for r in database.execute("SELECT * FROM old_depo ORDER BY depo_id"):
            depo_ids[r["nosaukums"]] = database.execute(
                "INSERT INTO Depo (nosaukums, adrese) VALUES (?, ?)",
                (r["nosaukums"], r["pilseta"])).lastrowid

    if "linijas" in veco_tabulas:
        for r in database.execute(
                "SELECT * FROM old_linijas ORDER BY linija_id"):
            linijas_ids[r["linija_id"]] = database.execute(
                "INSERT INTO Linija (nosaukums) VALUES (?)",
                (r["nosaukums"],)).lastrowid

    seen = {}   # numurs -> jaunais id
    for r in _veco_vilcienu_rindas(database):
        numurs = _teksts(r["numurs"])
        if numurs in seen:                 # numurs ir unikāls -> dublikāts
            vilcieni[r["id"]] = seen[numurs]
            izlaisti += 1
            continue

        modelis = _teksts(r["modelis"])
        rupnica = _teksts(r["rupnica"]) or None
        if modelis not in modeli:
            modeli[modelis] = _get_or_create(
                database, "Modelis", modelis,
                {"razotajs": rupnica, "ietilpiba": None,
                 "maksimalais_atrums": r["max_atrums"]})
        else:
            database.execute("""
                UPDATE Modelis
                SET razotajs = COALESCE(razotajs, ?),
                    maksimalais_atrums = COALESCE(maksimalais_atrums, ?)
                WHERE id = ?
            """, (rupnica, r["max_atrums"], modeli[modelis]))

        kategorija = _teksts(r["kategorija"]) or "Nav norādīta"
        if kategorija not in kategorijas:
            kategorijas[kategorija] = _get_or_create(
                database, "Kategorija", kategorija)

        depo_nosaukums = _teksts(r["depo"])
        statuss_teksts = _teksts(r["statuss"])
        if statuss_teksts not in STATUSI:
            statuss_teksts = STATUSI[0]

        database.execute("""
            INSERT INTO Vilciens
                (id, numurs, modelis_id, depo_id, kategorija_id,
                 statuss, izlaiduma_gads, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
        """, (r["id"], numurs, modeli[modelis],
              depo_ids.get(depo_nosaukums), kategorijas[kategorija],
              statuss_teksts, r["built"], r["created_at"]))
        seen[numurs] = r["id"]
        vilcieni[r["id"]] = r["id"]

    if "vilcienu_linijas" in veco_tabulas:
        for r in database.execute("SELECT * FROM old_vilcienu_linijas"):
            if r["vilciens_id"] in vilcieni and r["linija_id"] in linijas_ids:
                database.execute(
                    "INSERT INTO Sastavs (vilciens_id, linija_id) "
                    "VALUES (?, ?)",
                    (vilcieni[r["vilciens_id"]],
                     linijas_ids[r["linija_id"]]))

    if "remonti" in veco_tabulas:
        for r in database.execute("SELECT * FROM old_remonti"):
            if r["vilciens_id"] in vilcieni:
                database.execute("""
                    INSERT INTO Remonti
                        (vilciens_id, remontdarbu_veids, sakuma_datums)
                    VALUES (?, ?, ?)
                """, (vilcieni[r["vilciens_id"]], r["apraksts"],
                      r["datums"]))

    return len(seen), izlaisti


def create_table():
    global PAREJAS_PAZINOJUMS
    esosas = _tabulu_nosaukumi()
    veco_tabulas = [] if "vilciens" in esosas else [
        t for t in VECAS_TABULAS if t in esosas]
    jauna_pareja = "vilcieni" in veco_tabulas

    backup = _backup() if veco_tabulas else None

    with closing(connect()) as database:
        database.execute("BEGIN")
        try:
            for tabula in veco_tabulas:
                database.execute(
                    f"ALTER TABLE {tabula} RENAME TO old_{tabula}")

            for komanda in SHEMA.split(";"):
                if komanda.strip():
                    database.execute(komanda)

            pienemti = izlaisti = 0
            if jauna_pareja:
                pienemti, izlaisti = _parnest(database, veco_tabulas)

            for tabula in veco_tabulas:
                database.execute(f"DROP TABLE old_{tabula}")

            database.commit()
        except Exception:
            database.rollback()
            raise

    if jauna_pareja:
        PAREJAS_PAZINOJUMS = (
            f"Dati pārnesti uz jauno struktūru: {pienemti} vilcieni."
        )
        if izlaisti:
            PAREJAS_PAZINOJUMS += (
                f" Izlaisti {izlaisti} dublikāti (numurs ir unikāls)."
            )
        PAREJAS_PAZINOJUMS += f" Vecā bāze: {backup}"
        print(PAREJAS_PAZINOJUMS)


# ---------------------------------------------------------------
#  Tabulu apraksti (kolonnu pārbaudes)
# ---------------------------------------------------------------
KATEGORIJA = Tabula("Kategorija", [
    ("nosaukums", txt_req("Nosaukums")),
    ("apraksts", txt),
], "Kategoriju nevar dzēst — tai ir piesaistīti vilcieni!")

MODELIS = Tabula("Modelis", [
    ("nosaukums", txt_req("Nosaukums")),
    ("razotajs", txt),
    ("ietilpiba", int_("Ietilpība")),
    ("maksimalais_atrums", int_("Maksimālais ātrums")),
], "Modeli nevar dzēst — tam ir piesaistīti vilcieni!")

DEPO = Tabula("Depo", [
    ("nosaukums", txt_req("Nosaukums")),
    ("adrese", txt),
    ("ietilpiba", int_("Ietilpība")),
], "Depo nevar dzēst — tam ir piesaistīti vilcieni!")

LINIJA = Tabula("Linija", [
    ("nosaukums", txt_req("Nosaukums")),
    ("sakuma_stacija", txt),
    ("beigu_stacija", txt),
    ("garums_km", dec("Garums")),
], "Līniju nevar dzēst — tai ir piesaistīti sastāvi, laiki vai grafiki!")

VILCIENS = Tabula("Vilciens", [
    ("numurs", txt_req("Numurs")),
    ("modelis_id", fk),
    ("depo_id", fk),
    ("kategorija_id", fk),
    ("statuss", statuss),
    ("izlaiduma_gads", int_("Izlaiduma gads")),
], "Vilcienu nevar dzēst — tam ir piesaistīti remonti, sastāvi, laiki "
   "vai darba grafiki!")

VADITAJS = Tabula("Vilciena_vaditajs", [
    ("vards", txt_req("Vārds")),
    ("uzvards", txt_req("Uzvārds")),
    ("personas_kods", txt),
    ("telefons", txt),
    ("epasts", txt),
    ("alga_id", fk),
], "Vadītāju nevar dzēst — viņam ir piesaistītas algas vai darba grafiki!")

ALGA = Tabula("Alga", [
    ("vaditajs_id", fk_req("vadītāju")),
    ("summa", dec("Summa", obligats=True)),
    ("valuta", txt),
    ("datums", datums("Datums")),
])

SASTAVS = Tabula("Sastavs", [
    ("vilciens_id", fk_req("vilcienu")),
    ("linija_id", fk),
    ("vagonu_skaits", int_("Vagonu skaits")),
    ("ietilpiba", int_("Ietilpība")),
])

LAIKS = Tabula("Laiks", [
    ("vilciens_id", fk_req("vilcienu")),
    ("linija_id", fk_req("līniju")),
    ("atiesanas_laiks", laiks("Atiešanas laiks")),
    ("pienaksanas_laiks", laiks("Pienākšanas laiks")),
])

GRAFIKS = Tabula("Darba_grafiks", [
    ("vaditajs_id", fk_req("vadītāju")),
    ("vilciens_id", fk),
    ("linija_id", fk),
    ("darba_sakums", laiks("Darba sākums")),
    ("darba_beigas", laiks("Darba beigas")),
])

VADITAJA_VILCIENS = Tabula("Vilciena_vaditajs_vilciens", [
    ("vaditajs_id", fk_req("vadītāju")),
    ("vilciens_id", fk_req("vilcienu")),
], id_kol="rowid")

REMONTI = Tabula("Remonti", [
    ("vilciens_id", fk_req("vilcienu")),
    ("remontdarbu_veids", txt),
    ("sakuma_datums", datums("Sākuma datums")),
    ("beigu_datums", datums("Beigu datums")),
    ("izmaksas", dec("Izmaksas")),
    ("statuss", txt),
])

# ---- vienkāršoti nosaukumi (izmanto app.py, main.py, terminal.py) ----
add_kategorija, get_kategorija = KATEGORIJA.add, KATEGORIJA.get
update_kategorija, delete_kategorija = KATEGORIJA.update, KATEGORIJA.delete
add_modelis, get_modelis = MODELIS.add, MODELIS.get
update_modelis, delete_modelis = MODELIS.update, MODELIS.delete
add_depo, get_depo = DEPO.add, DEPO.get
update_depo, delete_depo = DEPO.update, DEPO.delete
add_linija, get_linija = LINIJA.add, LINIJA.get
update_linija, delete_linija = LINIJA.update, LINIJA.delete
add_vilciens, get_vilciens = VILCIENS.add, VILCIENS.get
update_vilciens, delete_vilciens = VILCIENS.update, VILCIENS.delete
add_vaditajs, get_vaditajs = VADITAJS.add, VADITAJS.get
update_vaditajs, delete_vaditajs = VADITAJS.update, VADITAJS.delete
add_alga, get_alga, update_alga = ALGA.add, ALGA.get, ALGA.update
add_sastavs, get_sastavs = SASTAVS.add, SASTAVS.get
update_sastavs, delete_sastavs = SASTAVS.update, SASTAVS.delete
add_laiks, get_laiks = LAIKS.add, LAIKS.get
update_laiks, delete_laiks = LAIKS.update, LAIKS.delete
add_grafiks, get_grafiks = GRAFIKS.add, GRAFIKS.get
update_grafiks, delete_grafiks = GRAFIKS.update, GRAFIKS.delete
add_vaditaja_vilciens = VADITAJA_VILCIENS.add
get_vaditaja_vilciens = VADITAJA_VILCIENS.get
update_vaditaja_vilciens = VADITAJA_VILCIENS.update
delete_vaditaja_vilciens = VADITAJA_VILCIENS.delete
add_remonts, get_remonts = REMONTI.add, REMONTI.get
update_remonts, delete_remonts = REMONTI.update, REMONTI.delete


def delete_alga(alga_id):
    """Izdzēš algu un notīra atsauci vadītāja ierakstā (alga_id)."""
    with closing(connect()) as database:
        with database:
            database.execute(
                "UPDATE Vilciena_vaditajs SET alga_id = NULL "
                "WHERE alga_id = ?", (alga_id,))
            database.execute("DELETE FROM Alga WHERE id = ?", (alga_id,))


# ---------------------------------------------------------------
#  Saraksti tabulām (pirmā kolonna vienmēr ir ID)
# ---------------------------------------------------------------
def get_kategorijas():
    return _query("""
        SELECT k.id, k.nosaukums, k.apraksts, COUNT(v.id)
        FROM Kategorija k LEFT JOIN Vilciens v ON v.kategorija_id = k.id
        GROUP BY k.id ORDER BY k.id
    """)


def get_modeli():
    return _query("""
        SELECT m.id, m.nosaukums, m.razotajs, m.ietilpiba,
               m.maksimalais_atrums, COUNT(v.id)
        FROM Modelis m LEFT JOIN Vilciens v ON v.modelis_id = m.id
        GROUP BY m.id ORDER BY m.id
    """)


def get_depo_saraksts():
    return _query("""
        SELECT d.id, d.nosaukums, d.adrese, d.ietilpiba, COUNT(v.id)
        FROM Depo d LEFT JOIN Vilciens v ON v.depo_id = d.id
        GROUP BY d.id ORDER BY d.id
    """)


def get_linijas():
    return _query("""
        SELECT id, nosaukums, sakuma_stacija, beigu_stacija, garums_km
        FROM Linija ORDER BY id
    """)


def get_vilcieni():
    return _query("""
        SELECT v.id, v.numurs, m.nosaukums, m.razotajs, k.nosaukums,
               m.maksimalais_atrums, v.izlaiduma_gads, v.statuss,
               d.nosaukums
        FROM Vilciens v
        LEFT JOIN Modelis m ON m.id = v.modelis_id
        LEFT JOIN Kategorija k ON k.id = v.kategorija_id
        LEFT JOIN Depo d ON d.id = v.depo_id
        ORDER BY v.id
    """)


def get_sastavi():
    return _query("""
        SELECT s.id, v.numurs, l.nosaukums, s.vagonu_skaits, s.ietilpiba
        FROM Sastavs s
        JOIN Vilciens v ON v.id = s.vilciens_id
        LEFT JOIN Linija l ON l.id = s.linija_id
        ORDER BY s.id
    """)


def get_laiki():
    return _query("""
        SELECT t.id, v.numurs, l.nosaukums, t.atiesanas_laiks,
               t.pienaksanas_laiks
        FROM Laiks t
        JOIN Vilciens v ON v.id = t.vilciens_id
        JOIN Linija l ON l.id = t.linija_id
        ORDER BY t.id
    """)


def get_vaditaji():
    return _query("""
        SELECT p.id, p.vards, p.uzvards, p.personas_kods, p.telefons,
               p.epasts,
               CASE WHEN a.id IS NULL THEN NULL
                    ELSE a.summa || ' ' || COALESCE(a.valuta, '') END,
               p.created_at
        FROM Vilciena_vaditajs p LEFT JOIN Alga a ON a.id = p.alga_id
        ORDER BY p.id
    """)


def get_algas():
    return _query("""
        SELECT a.id, p.vards || ' ' || p.uzvards, a.summa, a.valuta,
               a.datums
        FROM Alga a JOIN Vilciena_vaditajs p ON p.id = a.vaditajs_id
        ORDER BY a.id
    """)


def get_grafiki():
    return _query("""
        SELECT g.id, p.vards || ' ' || p.uzvards, v.numurs, l.nosaukums,
               g.darba_sakums, g.darba_beigas
        FROM Darba_grafiks g
        JOIN Vilciena_vaditajs p ON p.id = g.vaditajs_id
        LEFT JOIN Vilciens v ON v.id = g.vilciens_id
        LEFT JOIN Linija l ON l.id = g.linija_id
        ORDER BY g.id
    """)


def get_vaditaju_vilcieni():
    return _query("""
        SELECT x.rowid, p.vards || ' ' || p.uzvards, v.numurs,
               x.created_at
        FROM Vilciena_vaditajs_vilciens x
        JOIN Vilciena_vaditajs p ON p.id = x.vaditajs_id
        JOIN Vilciens v ON v.id = x.vilciens_id
        ORDER BY x.rowid
    """)


def get_remonti():
    return _query("""
        SELECT r.id, v.numurs, r.remontdarbu_veids, r.sakuma_datums,
               r.beigu_datums, r.izmaksas, r.statuss
        FROM Remonti r JOIN Vilciens v ON v.id = r.vilciens_id
        ORDER BY r.id
    """)


# ---------------------------------------------------------------
#  Izvēlņu saraksti formām: (id, teksts)
# ---------------------------------------------------------------
def get_kategoriju_izvele():
    return _izvele("SELECT id, nosaukums FROM Kategorija "
                   "ORDER BY nosaukums")


def get_modeli_izvele():
    return _izvele("SELECT id, nosaukums FROM Modelis ORDER BY nosaukums")


def get_depo_izvele():
    return _izvele("SELECT id, nosaukums FROM Depo ORDER BY nosaukums")


def get_linijas_izvele():
    return _izvele("SELECT id, nosaukums FROM Linija ORDER BY nosaukums")


def get_vilcienu_izvele():
    return _izvele("""
        SELECT v.id, TRIM(COALESCE(m.nosaukums, '') || ' ' || v.numurs)
        FROM Vilciens v LEFT JOIN Modelis m ON m.id = v.modelis_id
        ORDER BY m.nosaukums, v.numurs
    """)


def get_vaditaju_izvele():
    return _izvele("SELECT id, vards || ' ' || uzvards "
                   "FROM Vilciena_vaditajs ORDER BY uzvards, vards")


def get_algu_izvele():
    return _izvele("""
        SELECT a.id, 'Alga ' || a.summa || ' ' || COALESCE(a.valuta, '') ||
                     ' (' || p.vards || ' ' || p.uzvards || ')'
        FROM Alga a JOIN Vilciena_vaditajs p ON p.id = a.vaditajs_id
        ORDER BY a.id
    """)


create_table()


create_table()
