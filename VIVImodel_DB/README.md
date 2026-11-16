# Vilcienu informācijas pārvaldības sistēma

## Projekta apraksts

Vilcienu informācijas pārvaldības sistēma ir Python programma vilcienu informācijas glabāšanai, apskatei un pārvaldīšanai, izmantojot SQLite datubāzi un Tkinter grafisko lietotāja saskarni.

## Datubāzes struktūra

Datubāzē ir 12 savstarpēji saistītas tabulas:

1. Vilciens
2. Modelis
3. Kategorija
4. Depo
5. Linija
6. Sastavs
7. Laiks
8. Remonti
9. Vilciena_vaditajs
10. Alga
11. Darba_grafiks
12. Vilciena_vaditajs_vilciens

Datubāzes shēma pieejama šādos failos:

- `shema_12_tabulas.png` – datubāzes shēmas attēls.
- `shema_12_tabulas.dbml` – datubāzes shēma DBML formātā, kuru iespējams importēt vietnē [dbdiagram.io](https://dbdiagram.io/).

## Programmas funkcionalitāte

Programmas grafiskajā logā katrai datubāzes tabulai ir sava cilne, kurā iespējams:

- Pievienot jaunus ierakstus.
- Rediģēt esošos ierakstus.
- Dzēst ierakstus.
- Apskatīt tabulā saglabāto informāciju.

Ierakstu dzēšana tiek apstiprināta ar dialoga logu, kurā pieejamas izvēles Jā/Nē.

Dialoga logā izmantots VIVI logo un piezīmes lauks.

## Programmas palaišana

Lai palaistu programmas grafisko versiju:

```bash
python app.py
```

Lai izveidotu sākuma datus tukšai datubāzei:

```bash
python main.py
```

Lai palaistu programmas teksta versiju:

```bash
python terminal.py
```

## Datubāzes migrācija un rezerves kopija

Ja programma atrod vecāku datubāzes versiju, pirmajā palaišanas reizē dati tiek automātiski pārnesti uz jauno datubāzes struktūru.

- Ieraksta numurs ir unikāls.
- Dublikāti migrācijas laikā tiek izlaisti.
- Vecā datubāze tiek saglabāta kā rezerves kopija ar nosaukumu `vilcieni_vecais_backup.db`.

## Izmantotās tehnoloģijas

- **Python** – programmas izstrādei.
- **SQLite** – datu glabāšanai un pārvaldīšanai.
- **Tkinter** – grafiskās lietotāja saskarnes izveidei.
- **DBML** – datubāzes struktūras aprakstīšanai.

[alt text](image.png)
