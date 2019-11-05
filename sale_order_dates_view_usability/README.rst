Sale date usability
===================
Questo modulo:
* rende visibile il campo data conferma, che è la data effettiva di conferma
* imposta la data richiesta modificabile anche se l'ordine è in corso**
* crea un parametro 'gg di default richiesta'
* non modifica la data richiesta se viene inserita dall'utente, altrimenti la
  imposta alla conferma dell'ordine con la 'data conferma + gg di default richiesta'
* modifica la vista calendario degli ordini per basarsi sulla data di richiesta

**questo comporta che se la data richiesta viene modificata successivamente alla
  conferma, sarà diversa dalle date nelle righe dell'SO e negli OUT, ma non ci
  interessano le righe d'ordine né gli OUT

Quindi in pratica:
1. se l'utente non fa nulla, alla conferma dell'ordine la data richiesta verrà
   automaticamente compilata con 'data conferma + gg default'
2. se l'utente indica una data, verrà mantenuta quella

* TODO rendere stampabile il calendario
* TODO avere una promemoria via mail a scadenze predefinite:
    1. dalla data richiesta -4gg con un massimo di 7 gg. ogni venerdì mattina
    2. lista di tutti gli ordini segnalati e non per la produzione (vedi ordini
       per natale / pre fiera)
* TODO segnalare nel calendario gli ordini in scadenza
* TODO avere degli alert che 'saltino fuori' solo per quelli in scadenza (da
  decidere: a -4gg? altri?): creare un modulo sulla base di reminder_phonecall


