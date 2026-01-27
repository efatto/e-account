Guida alla funzione check_code_and_qty
Questa funzione in Python permette di verificare, all'interno di un documento (PDF, immagine come
PNG/JPG, o file EML), la presenza di un **codice prodotto** e di una **quantità** specificata. Se
entrambi i valori vengono trovati, la funzione restituisce "TUTTO CORRETTO", altrimenti "VALORI
ERRATI".

Utilizzo della funzione
La funzione principale è: check_code_and_qty(file_path, target_code, target_qty)
- file_path: percorso del documento da analizzare (es. "allegato.pdf").
- target_code: il codice da cercare, ad esempio "JPM09".
- target_qty: la quantità da cercare, ad esempio 100.

Esempio pratico
Se vogliamo verificare che nel file ordine.pdf sia presente il codice "JPM09" con quantità 100 pezzi:
from check_code_quantity import check_code_and_qty
ok, msg = check_code_and_qty("ordine.pdf", "JPM09", 100)
print(msg) # --> 'TUTTO CORRETTO' o 'VALORI ERRATI'

Output della funzione
Condizione                          Risultato
Codice e quantità trovati           TUTTO CORRETTO
Codice mancante o quantità diversa  VALORI ERRATI
Errore di lettura o file mancante   Messaggio di errore

Requisiti
Python 3.x
Librerie: Pillow, pytesseract, pdf2image
Installazione del software Tesseract-OCR sul sistema
Per i PDF: installazione del pacchetto poppler

La funzione è pensata per controlli rapidi di documenti ricevuti da clienti o fornitori, automatizzando
la verifica della corrispondenza tra ordine e quantità dichiarata.
