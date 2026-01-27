"""
Script / funzione per cercare un CODICE e una QUANTITÀ all'interno di un documento
(pdf, jpg, png, eml, ecc.).

Funzione principale: check_code_and_qty(file_path, target_code, target_qty)
- Restituisce una tupla (bool, message) dove bool=True indica "TUTTO CORRETTO"
  e False indica "VALORI ERRATI".

Dipendenze (installare via pip):
- pytesseract
- pdf2image
- Pillow

Nota: è necessario installare il binario Tesseract-OCR (es. su Windows
"Tesseract-OCR\tesseract.exe").
Se necessario impostare pytesseract.pytesseract.tesseract_cmd con il path corretto.

Uso:
# from check_code_quantity import check_code_and_qty
# ok, msg = check_code_and_qty('allegato.pdf', 'JPM09', 100)
# print(msg)

"""

import logging
import os
import re
import tempfile
from typing import Dict, Union

from odoo import _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from PIL import Image
except Exception:
    raise ValidationError(_("Pillow not installed. Resolve with: pip install Pillow"))

try:
    import pytesseract
except Exception:
    raise ValidationError(
        _("pytesseract not installed. Resolve with: pip install pytesseract")
    )

# pdf2image è opzionale (usato per convertire PDF in immagini)
try:
    from pdf2image import convert_from_path

    _has_pdf2image = True
except Exception as e:
    _logger.info(
        f"Error {str(e)} trying to open pdf2image. Resolve with: pip install pdf2image"
    )
    _has_pdf2image = False

# ---------------------------------------------------------
# Helper: normalizzazione e ricerca
# ---------------------------------------------------------


def _normalize_code(s: str) -> str:
    """Rimuove spazi e caratteri non alfanumerici e mette in maiuscolo."""
    return re.sub(r"[^A-Za-z0-9]", "", s).upper()


def _extract_numbers(text: str) -> list:
    """Restituisce tutti i numeri interi presenti nel testo come int."""
    nums = re.findall(r"\b\d+[\d,.]*\b", text)
    cleaned = []
    for n in nums:
        n2 = n.replace(".", "").replace(",", "")  # rimuove separatori
        try:
            cleaned.append(int(n2))
        except Exception as e:
            _logger.info(f"Error {str(e)} converting number {n} to int")
    return cleaned


# ---------------------------------------------------------
# Estrazione testo da immagini / pdf / eml
# ---------------------------------------------------------


def _ocr_image(image: Union[str, Image.Image]) -> str:
    """Esegue OCR su immagine (path o PIL.Image).
    Ritorna il testo OCR come stringa."""
    if isinstance(image, str):
        img = Image.open(image)
    else:
        img = image
    # convert to RGB to avoid problemi con immagini monotone
    try:
        img = img.convert("RGB")
    except Exception as e:
        _logger.info(f"Error {str(e)} converting image to RGB")
    text = pytesseract.image_to_string(img)
    return text


def _extract_text_from_pdf(path: str) -> str:
    """Converti ogni pagina PDF in immagine e fai OCR.
    Richiede pdf2image + poppler installato (sistema)."""
    if not _has_pdf2image:
        raise ValidationError(
            _("Install pdf2image to read pdf files (pip install pdf2image)")
        )
    texts = []
    # convert_from_path usa poppler. Se non è installato, fallirà.
    pages = convert_from_path(path)
    for p in pages:
        texts.append(_ocr_image(p))
    return "\n".join(texts)


def _extract_text_from_eml(path: str) -> str:  # noqa C901
    """Estrae testo (body) da file .eml. Se ci sono allegati immagine/pdf li OCRa anche.
    Usa la libreria email (inclusa in Python)."""
    import email
    from email import policy

    texts = []
    with open(path, "rb") as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    # testo corpo
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain" or ctype == "text/html":
                try:
                    texts.append(part.get_content())
                except Exception:
                    try:
                        texts.append(
                            part.get_payload(decode=True).decode(errors="ignore")
                        )
                    except Exception:
                        _logger.info("Error decoding part content")
            # allegati
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                payload = part.get_payload(decode=True)
                if not payload:
                    continue
                # salva temporaneamente
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=("_" + (filename or "att"))
                ) as tf:
                    tf.write(payload)
                    tf.flush()
                    tfname = tf.name
                # tenta OCR se immagine o pdf
                ext = os.path.splitext(filename or "")[1].lower()
                try:
                    if ext in (".jpg", ".jpeg", ".png", ".tif", ".tiff"):
                        texts.append(_ocr_image(tfname))
                    elif ext == ".pdf":
                        texts.append(_extract_text_from_pdf(tfname))
                    else:
                        # tenta OCR comunque
                        try:
                            texts.append(_ocr_image(tfname))
                        except Exception:
                            pass
                finally:
                    try:
                        os.unlink(tfname)
                    except Exception:
                        pass
    else:
        # messaggio singolo
        try:
            texts.append(msg.get_content())
        except Exception:
            texts.append(msg.get_payload(decode=True).decode(errors="ignore"))

    return "\n".join(t for t in texts if t)


# ---------------------------------------------------------
# Funzione principale
# ---------------------------------------------------------


def check_code_and_qty(
    file_path: str, file_ext: str, target_data: dict
) -> Dict[str, list]:
    """Controlla che in file_path siano presenti il codice e la quantità.

    - file_path: percorso locale verso file (pdf, jpg, png, eml, ecc.)
    - target_data: dict con:
        id della riga e dict con:
            stringa del codice da cercare (es. 'JPM09', se nel documento ci sono spazi
             tra i caratteri, la funzione li ignora)
            quantità intera da cercare (es. 100)
            codice del prodotto del partner (cliente o fornitore)
            prezzo totale

    Ritorna (True, 'TUTTO CORRETTO') o (False, 'VALORI ERRATI').
    """
    if not os.path.isfile(file_path):
        return {"Undefined": [False, f"File non trovato: {file_path}"]}

    ext = "." + file_ext.lower()
    full_text = ""
    _logger.debug(f"Checking file {file_path} with extension {ext}")
    try:
        if ext in (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"):
            full_text = _ocr_image(file_path)
        elif ext == ".pdf":
            full_text = _extract_text_from_pdf(file_path)
        elif ext in (".eml",):
            full_text = _extract_text_from_eml(file_path)
        else:
            # prova a leggere come immagine
            try:
                full_text = _ocr_image(file_path)
            except Exception:
                # fallback: leggi come testo semplice
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        full_text = f.read()
                except Exception:
                    full_text = ""
    except Exception as exc:
        _logger.info(f"Error extracting text from file {file_path}: {exc}")
        return {"Undefined": [False, f"Errore durante estrazione testo: {exc}"]}

    if not full_text:
        return {"Undefined": [False, "Nessun testo estratto dal documento"]}

    target_results = {}
    for target in target_data:
        # Normalizza codice: rimuove spazi e caratteri non alfanumerici
        norm_target = _normalize_code(target_data[target].get("default_code"))
        target_qty = target_data[target].get("quantity")
        target_partner_code = _normalize_code(target_data[target].get("partner_code"))
        target_price = target_data[target].get("price_total")
        # Normalizza testo: rimuovi caratteri non alfanumerici per ricerca codice
        # "compatta"
        compact_text = _normalize_code(full_text)

        code_found = norm_target in compact_text
        if not code_found:
            # try using O instead of 0
            norm_target = norm_target.replace("0", "O")
            code_found = norm_target in compact_text

        partner_code_found = target_partner_code in compact_text
        if not partner_code_found:
            # try using O instead of 0
            target_partner_code = target_partner_code.replace("0", "O")
            partner_code_found = target_partner_code in compact_text

        # Cerca la quantità: controllo più permissivo
        # - cerca il numero come parola isolata
        qty_pattern = re.compile(
            r"\b" + re.escape(str(target_qty)) + r"\b",
            flags=re.IGNORECASE,
        )
        qty_found = bool(qty_pattern.search(full_text))

        # Se non trovato direttamente, prova a trovare numeri e confrontarli
        if not qty_found:
            nums = _extract_numbers(full_text)
            qty_found = target_qty in nums

        # Cerca il prezzo: controllo più permissivo
        # - cerca il numero come parola isolata
        price_pattern = re.compile(
            r"\b" + re.escape(str(target_price)) + r"\b",
            flags=re.IGNORECASE,
        )
        price_found = bool(price_pattern.search(full_text))

        # Se non trovato direttamente, prova a trovare numeri e confrontarli
        if not price_found:
            nums = _extract_numbers(full_text)
            price_found = target_price in nums

        result_msg = "{code}, {partner_code}, {qty}, {price}.".format(
            code=(
                f"Code {'not' if not code_found else ''} found: "
                + target_data[target].get("default_code")
            ),
            partner_code=(
                f"Partner product code {'not' if not partner_code_found else ''} found: "
                + target_data[target].get("partner_code")
            ),
            qty=f"Quantity {'not' if not qty_found else ''} found: " + str(target_qty),
            price=f"Price {'not' if not price_found else ''} found: "
            + str(target_price),
        )

        target_results[target] = {
            (code_found or partner_code_found) and qty_found and price_found: result_msg
        }
    return target_results
