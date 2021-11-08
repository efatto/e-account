Sale date usability
===================
Questo modulo:
* rende visibile il campo data conferma, che è la data effettiva di conferma
* imposta la data richiesta modificabile anche se l'ordine è in corso
* crea un parametro 'gg di default richiesta'
* la data richiesta, se non inserita dall'utente, viene impostata alla conferma
  dell'ordine con la 'data conferma + gg di default richiesta'
* modifica la vista calendario degli ordini per basarsi sulla data di richiesta
* evidenzia nel calendario gli ordini in base alla differenza della data di
  richiesta dalla data odierna: rosso<=0gg, arancione<=4gg, giallo<=7gg,
  verde>7gg
* possibilità di creare degli alert per gli ordini in scadenza
  (da decidere: a -4gg? altri?): creato modulo reminder_saleorder
TODO: da creare modulo per auto-aggiungere i reminder agli ordini e poi
  rimuoverli dopo il completamento

* TODO rendere stampabile il calendario: non c'è nulla, da creare report da zero!
* TODO avere una promemoria via mail a scadenze predefinite:
    1. dalla data richiesta -4gg con un massimo di 7 gg. ogni venerdì mattina
    2. lista di tutti gli ordini segnalati e non per la produzione (vedi ordini
       per natale / pre fiera)
