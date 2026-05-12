========================
Italy - Account XMLID Fix
========================

Questo modulo serve a prevenire la duplicazione dei conti contabili durante
l'installazione del modulo di localizzazione italiana (`l10n_it`).

Funzionamento
=============

Prima dell'installazione del modulo, viene eseguito un `pre_init_hook` che:
1. Legge i file CSV (`account.account-it.csv`, `account.tax-it.csv`,
   `account.tax.group-it.csv`, `account.fiscal.position-it.csv`) dal modulo
   `l10n_it`.
2. Cerca nel database i record esistenti che corrispondono ai dati definiti
   nei CSV (per codice o nome).
3. Gestisce i journal standard di Odoo (`sale`, `purchase`, `general`,
   `exch`, `caba`, `bank`, `cash`, `stj`) assegnando loro l'XMLID
   standard di Odoo 18 (`account.IDCOMPAGNIA_XMLID`) se non già presente.
4. Se trova un match per conti, tasse o posizioni fiscali e il record non ha
   ancora un XMLID per il modulo `l10n_it`, glielo assegna.

In questo modo, quando `l10n_it` verrà installato o caricato, Odoo
riconoscerà i record esistenti tramite l'XMLID e aggiornerà quelli invece
di crearne di nuovi duplicati.
