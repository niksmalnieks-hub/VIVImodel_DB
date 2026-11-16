from funkcijas import (
    add_vilciens,
    get_vilcieni,
    get_modeli_izvele,
    get_kategoriju_izvele,
    STATUSI,
)


def izvelies(nosaukums, varianti):
    """Parāda sarakstu un atgriež izvēlēto ID (vai None, ja tukšs)."""
    print(f"{nosaukums}:")
    for variants_id, teksts in varianti:
        print(f"  {variants_id} - {teksts}")
    ievade = input(f"{nosaukums} ID (var atstāt tukšu): ").strip()
    return int(ievade) if ievade else None


while True:
    print("\nVILCIENU DATUBĀZE")
    print("1 - Pievienot vilcienu")
    print("2 - Parādīt vilcienus")
    print("0 - Iziet")

    choice = input("Izvēle: ")

    if choice == "1":
        try:
            numurs = input("Numurs: ")
            modelis_id = izvelies("Modelis", get_modeli_izvele())
            kategorija_id = izvelies("Kategorija", get_kategoriju_izvele())
            izlaiduma_gads = input("Izlaiduma gads (var atstāt tukšu): ")
            print("Statuss: 1 - Ekspluatācijā, 2 - Nestrādā")
            statuss = STATUSI[1] if input("Statuss: ") == "2" else STATUSI[0]

            vilciens_id = add_vilciens(
                numurs=numurs,
                modelis_id=modelis_id,
                kategorija_id=kategorija_id,
                statuss=statuss,
                izlaiduma_gads=izlaiduma_gads,
            )
            print("Vilciens pievienots. ID:", vilciens_id)
        except ValueError as error:
            print("Kļūda:", error)

    elif choice == "2":
        for vilciens in get_vilcieni():
            print(tuple(vilciens))

    elif choice == "0":
        print("Programma beidz darbu!")
        break

    else:
        print("Nepareiza izvēle!")
