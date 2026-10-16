
from funkcijas import connect, create_table

create_table()

vilcieni = [
    ("ER2M", "605", None, "Elektrovilciens", "Latvija"),
]

for numurs in [
    "964", "989", "1300", "1300R", "1307",
    "1310", "1310R", "1317", "1317R",
    "1341", "1342", "1342R", "3034", "8004", "8029"
]:
    vilcieni.append(
        ("ER2", numurs, None, "Elektrovilciens", "Latvija")
    )

for numurs in [
    "2207", "2206", "2008R",
    "7113", "7113R", "7114", "7114R",
    "7115", "7115R", "7116", "7116R",
    "7117", "7117R", "7118", "7118R"
]:
    vilcieni.append(
        ("ER2T", numurs, None, "Elektrovilciens", "Latvija")
    )

for i in range(1, 33):
    vilcieni.append(
        ("Škoda 16Ev", f"{i:04d}", None,
         "Elektrovilciens", "Latvija")
    )

for numurs in [
    "172", "198", "210", "227", "240",
    "243", "252", "311", "405"
]:
    vilcieni.append(
        ("DR1A", numurs, None, "Dīzeļvilciens", "Latvija")
    )

for numurs in ["185", "187", "219", "290"]:
    vilcieni.append(
        ("DR1AC", numurs, None, "Dīzeļvilciens", "Latvija")
    )

for numurs in ["222", "246", "254", "267", "291"]:
    vilcieni.append(
        ("DR1AM", numurs, None, "Dīzeļvilciens", "Latvija")
    )

with connect() as database:
    skaits = database.execute(
        "SELECT COUNT(*) FROM vilcieni"
    ).fetchone()[0]

    if skaits == 0:
        database.executemany("""
            INSERT INTO vilcieni
                (modelis, numurs, built, category, info)
            VALUES (?, ?, ?, ?, ?)
        """, vilcieni)

        print("Sākotnējie vilcieni pievienoti:", len(vilcieni))
    else:
        print("Datubāzē jau ir vilcieni. Dati netika dublēti.")
