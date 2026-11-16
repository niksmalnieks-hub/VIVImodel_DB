Programma vilcienu informācijas glabāšanai un pārvaldīšanai (SQLite + Tkinter).

Datubāzē ir 12 savstarpēji saistītas tabulas (shēma: shema_12_tabulas.png / shema_12_tabulas.dbml,
to var ielīmēt dbdiagram.io):

  Vilciens, Modelis, Kategorija, Depo, Linija, Sastavs, Laiks, Remonti,
  Vilciena_vaditajs, Alga, Darba_grafiks, Vilciena_vaditajs_vilciens

Programmas logā katrai tabulai ir sava cilne, kurā var pievienot, labot un dzēst ierakstus.
Dzēšanu apstiprina ar jā/nē logu ar VIVI logo un piezīmes lauku.

Palaišana: python app.py
Sākuma dati (tukšai bāzei): python main.py
Teksta versija: python terminal.py

Ja tiek atrasta vecāka datubāze, pirmajā palaišanā dati automātiski tiek pārnesti uz jauno
struktūru (numurs ir unikāls, tāpēc dublikāti tiek izlaisti), un vecā bāze tiek saglabāta kā
vilcieni_vecais_backup.db.
