
from funkcijas import (
    create_table,
    add_kategorija,
    add_modelis,
    add_vilciens,
    get_vilcieni,
    get_modeli,
    STATUSI,
)

create_table()

# (modelis, kategorija, numuri)
sakuma_dati = [
    ("ER2M", "Elektrovilciens", ["605"]),
    ("ER2", "Elektrovilciens", [
        "964", "989", "1300", "1300R", "1307",
        "1310", "1310R", "1317", "1317R",
        "1341", "1342", "1342R", "3034", "8004", "8029",
    ]),
    ("ER2T", "Elektrovilciens", [
        "2207", "2206", "2008R",
        "7113", "7113R", "7114", "7114R",
        "7115", "7115R", "7116", "7116R",
        "7117", "7117R", "7118", "7118R",
    ]),
    ("Škoda 16Ev", "Elektrovilciens", [f"{i:04d}" for i in range(1, 33)]),
    ("DR1A", "Dīzeļvilciens", [
        "172", "198", "210", "227", "240",
        "243", "252", "311", "405",
    ]),
    ("DR1AC", "Dīzeļvilciens", ["185", "187", "219", "290"]),
    ("DR1AM", "Dīzeļvilciens", ["222", "246", "254", "267", "291"]),
]

if get_vilcieni() or get_modeli():
    print("Datubāzē jau ir dati. Dati netika dublēti.")
else:
    kategorijas = {}
    skaits = 0

    for modelis, kategorija, numuri in sakuma_dati:
        if kategorija not in kategorijas:
            kategorijas[kategorija] = add_kategorija(nosaukums=kategorija)

        modelis_id = add_modelis(nosaukums=modelis)

        for numurs in numuri:
            add_vilciens(
                numurs=numurs,
                modelis_id=modelis_id,
                kategorija_id=kategorijas[kategorija],
                statuss=STATUSI[0],
            )
            skaits += 1

    print("Sākotnējie vilcieni pievienoti:", skaits)
