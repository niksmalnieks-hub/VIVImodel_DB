from funkcijas import add_vilciens, get_vilcieni

while True:
    print("\nVILCIENU DATUBĀZE")
    print("1 - Pievienot vilcienu")
    print("2 - Parādīt vilcienus")
    print("0 - Iziet")

    choice = input("Izvēle: ")

    if choice == "1":
        modelis = input("Modelis: ")
        numurs = input("Numurs: ")
        built = input("Uzbūves gads (var atstāt tukšu): ")
        category = input("Kategorija: ")
        info = input("Informācija: ")

        try:
            vilciens_id = add_vilciens(modelis, numurs, built, category, info)
            print("Vilciens pievienots. ID:", vilciens_id)
        except ValueError as error:
            print("Kļūda:", error)

    elif choice == "2":
        for vilciens in get_vilcieni():
            print(vilciens)

    elif choice == "0":
        print("Programma beidz darbu!")
        break

    else:
        print("Nepareiza izvēle!")