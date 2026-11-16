Vilcienu informācijas pārvaldības sistēma
Projekta apraksts
Programma vilcienu informācijas glabāšanai un pārvaldīšanai, izmantojot SQLite datubāzi un Tkinter grafisko lietotāja saskarni.

Datubāzes struktūra
Datubāzē ir 12 savstarpēji saistītas tabulas:

Vilciens
Modelis
Kategorija
Depo
Linija
Sastavs
Laiks
Remonti
Vilciena_vaditajs
Alga
Darba_grafiks
Vilciena_vaditajs_vilciens

Datubāzes shēma pieejama failos:

-shema_12_tabulas.png – datubāzes shēmas attēls.
-shema_12_tabulas.dbml – datubāzes shēma DBML formātā, kuru iespējams importēt dbdiagram.io.

Programmas funkcionalitāte
Programmas grafiskajā logā katrai datubāzes tabulai ir sava cilne, kurā iespējams:
-Pievienot jaunus ierakstus.
-Rediģēt esošos ierakstus.
-Dzēst ierakstus.
-Apskatīt tabulā saglabāto informāciju.
Ierakstu dzēšana tiek apstiprināta ar dialoga logu, kurā pieejamas izvēles Jā/Nē. Dialoga logā izmantots VIVI logo un piezīmes lauks.

Programmas palaišana
Lai palaistu programmas grafisko versiju, izmanto komandu:

bash
python app.py
Lai izveidotu sākuma datus tukšai datubāzei:

bash
python main.py
Lai palaistu programmas teksta versiju:

bash
python terminal.py

Datubāzes migrācija un rezerves kopija:
Ja programma atrod vecāku datubāzes versiju, pirmajā palaišanas reizē dati tiek automātiski pārnesti uz jauno datubāzes struktūru.

-Ierakstu numurs ir unikāls.
-Dublikāti migrācijas laikā tiek izlaisti.
-Vecā datubāze tiek saglabāta kā rezerves kopija ar nosaukumu vilcieni_vecais_backup.db.

Izmantotās tehnoloģijas
Python – programmas izstrādei.
SQLite – datu glabāšanai un pārvaldīšanai.
Tkinter – grafiskās lietotāja saskarnes izveidei.
DBML – datubāzes struktūras aprakstīšanai.
