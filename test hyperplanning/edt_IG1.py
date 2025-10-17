import sys
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.service import Service
except Exception as e:
    print("\n⚠️ Selenium n'est pas installé ou introuvable dans cet environnement.")
    print("Installe-le via: pip install selenium webdriver-manager")
    print("Ou installe seulement selenium: pip install selenium")
    print("Ensuite assure-toi que chromedriver/Chrome sont installés et compatibles.")
    sys.exit(1)
import time
import json
import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import uuid

json_save_path = r"/home/aurelien/Bureau/test hyperplanning/edt_IG1.json"
ics_save_path = r"/home/aurelien/Bureau/test hyperplanning/edt_IG1.ics"

options = Options()
# Allow forcing headless via environment variable
force_headless = os.environ.get("FORCE_HEADLESS") or os.environ.get("HPESGT_FORCE_HEADLESS")
display = os.environ.get("DISPLAY")
if force_headless:
    try:
        options.add_argument("--headless=new")
    except Exception:
        options.add_argument("--headless")
    print("→ FORCE_HEADLESS set: running Chrome in headless mode")
elif not display:
    try:
        options.add_argument("--headless=new")
    except Exception:
        options.add_argument("--headless")
    print("→ No DISPLAY found: running Chrome in headless mode")
else:
    print("→ DISPLAY found: running Chrome with window (window-size set)")
# Set window size in all modes to stabilize layout
options.add_argument("--window-size=1400,900")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")

driver = webdriver.Chrome(options=options)

def trouver_jour_par_colonnes(blocs):
    """Détecte dynamiquement les positions 'left' des colonnes et renvoie une fonction
    qui, donnée une valeur style, renvoie le jour correspondant.

    Méthode : on récupère toutes les valeurs 'left' trouvées dans les blocs, on
    en déduit une liste triée unique puis on mappe chaque colonne à un jour
    (Lundi..Vendredi) dans l'ordre gauche->droite.
    """
    lefts = []
    for b in blocs:
        s = b.get_attribute("style") or ""
        m = re.search(r"left:\s*(-?\d+)px", s)
        if m:
            lefts.append(int(m.group(1)))

    if not lefts:
        # fallback to default map if nothing found
        ordered_days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        def _trouve_fallback(style):
            return "Inconnu"
        return _trouve_fallback, ordered_days

    unique_lefts = sorted({int(round(x)) for x in lefts})

    # Keep at most 5 columns (workdays)
    unique_lefts = unique_lefts[:5]

    ordered_weekdays = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
    # If fewer columns found, truncate weekdays accordingly
    mapped_days = ordered_weekdays[: len(unique_lefts)]

    mapping = {pos: day for pos, day in zip(unique_lefts, mapped_days)}

    def _trouve(style):
        m = re.search(r"left:\s*(-?\d+)px", style)
        if not m:
            return "Inconnu"
        val = int(m.group(1))
        # find nearest mapped left within a reasonable threshold
        nearest = min(mapping.keys(), key=lambda k: abs(k - val))
        if abs(nearest - val) <= 30:  # tolerance in px
            return mapping[nearest]
        return "Inconnu"

    return _trouve, mapped_days

try:
    print("-> Ouverture du site...")
    driver.get("https://hpesgt.cnam.fr/hp/invite")
    time.sleep(2)

    # === Sélection de la classe IG1 ===
    print("-> Sélection de la classe IG1...")
    champ = driver.find_element(By.ID, "GInterface.Instances[1].Instances[1].bouton_Edit")
    champ.clear()
    champ.send_keys("IG1")
    time.sleep(1)
    champ.send_keys(Keys.ENTER)
    time.sleep(3)

    # === Défilement pour forcer le chargement ===
    print("-> Défilement de la page pour charger tous les cours...")
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(5):
        ActionChains(driver).move_to_element(body).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(1.5)

    # === Extraction des cours ===
    cours_elements = driver.find_elements(By.CSS_SELECTOR, "div.EmploiDuTemps_Element")
    edt = []

    print(f"-> {len(cours_elements)} blocs de cours détectés")

    # construire la fonction de mapping jour <- colonne
    trouver_jour, colonnes_detectees = trouver_jour_par_colonnes(cours_elements)

    for bloc in cours_elements:
        try:
            cours_simple = bloc.find_element(By.CSS_SELECTOR, "div.cours-simple")
            # horaire peut être en title ou dans le texte du bloc; récupérer style du parent ou de l'enfant
            horaire = (cours_simple.get_attribute("title") or "").strip()
            style = bloc.get_attribute("style") or cours_simple.get_attribute("style")
            jour = trouver_jour(style)

            contenus = cours_simple.find_elements(By.CSS_SELECTOR, "div.contenu")
            labels = cours_simple.find_elements(By.TAG_NAME, "label")

            nom_cours = labels[0].text.strip() if labels else ""
            prof = ""
            salle = ""

            for c in contenus:
                txt = c.text.strip()
                if not txt or txt == nom_cours:
                    continue
                if re.search(r"\b(Salle|Amphi)\b", txt, re.I):
                    salle = txt
                elif not prof:
                    prof = txt

            edt.append({
                "jour": jour,
                "horaire": horaire,
                "cours": nom_cours,
                "professeur": prof,
                "salle": salle
            })

        except Exception as e:
            print("⚠️ Erreur sur un cours :", e)
            continue

    # --- Sauvegarde JSON ---
    os.makedirs(os.path.dirname(json_save_path), exist_ok=True)
    with open(json_save_path, "w", encoding="utf-8") as f:
        json.dump(edt, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Emploi du temps JSON sauvegardé dans :\n{json_save_path}")

    # --- Génération ICS pour les 2 prochaines semaines ---
    try:
        tz_name = os.environ.get("TZ", "Europe/Paris")
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")

    day_name_to_weekday = {
        "Lundi": 0,
        "Mardi": 1,
        "Mercredi": 2,
        "Jeudi": 3,
        "Vendredi": 4,
        "Samedi": 5,
        "Dimanche": 6,
    }

    def parse_horaire(h):
        if not h:
            return None, None

        # Quick approach: find all time-like substrings (08:00, 8h00, 0800)
        times = re.findall(r"\d{1,2}[:h]\d{2}", h)
        if len(times) >= 2:
            start = times[0].replace("h", ":")
            end = times[1].replace("h", ":")
            return start, end

        # fallback to other patterns (e.g., 0800-1000)
        m = re.search(r"(\d{2})(\d{2})\s*[-–/]\s*(\d{2})(\d{2})", h)
        if m:
            start = f"{m.group(1)}:{m.group(2)}"
            end = f"{m.group(3)}:{m.group(4)}"
            return start, end

        # try richer pattern including 'à' and 'a'
        m = re.search(r"(\d{1,2}[:h]\d{2})\s*(?:[-–/]|à|a|au)\s*(\d{1,2}[:h]\d{2})", h)
        if m:
            start = m.group(1).replace("h", ":")
            end = m.group(2).replace("h", ":")
            return start, end

        return None, None

    def to_utc_str(dt_local):
        dt_utc = dt_local.astimezone(ZoneInfo("UTC"))
        return dt_utc.strftime("%Y%m%dT%H%M%SZ")

    today = datetime.now(tz).date()
    end_date = today + timedelta(days=13)  # next 14 days inclusive

    ics_lines = [
        "BEGIN:VCALENDAR",
        "PRODID:-//edt_IG1//EN",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
    ]

    for ev in edt:
        jour = ev.get("jour")
        if not jour or jour == "Inconnu":
            continue
        wk = day_name_to_weekday.get(jour)
        if wk is None:
            continue
        horaire = ev.get("horaire", "")
        start_s, end_s = parse_horaire(horaire)
        # If no horaire in title, try to extract from description fields
        if not start_s or not end_s:
            # try to look into 'cours' or 'salle' or 'professeur' fields for times
            combined_text = " ".join([ev.get('cours',''), ev.get('salle',''), ev.get('professeur','')])
            start_s, end_s = parse_horaire(combined_text)

        if not start_s or not end_s:
            # We'll create an all-day event on the matching weekday as fallback
            create_all_day = True
        else:
            create_all_day = False

        # for each date in next 14 days matching weekday
        d = today
        while d <= end_date:
            if d.weekday() == wk:
                try:
                    uid = f"{uuid.uuid4()}"
                    dtstamp = datetime.now(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")
                    if create_all_day:
                        print(f"→ Création all-day pour {ev.get('cours')} le {d} (jour={jour})")
                        # All day event: DTSTART;VALUE=DATE
                        dtstr = d.strftime("%Y%m%d")
                        ics_lines += [
                            "BEGIN:VEVENT",
                            f"UID:{uid}",
                            f"DTSTAMP:{dtstamp}",
                            f"DTSTART;VALUE=DATE:{dtstr}",
                            f"DTEND;VALUE=DATE:{(d+timedelta(days=1)).strftime('%Y%m%d')}",
                            f"SUMMARY:{ev.get('cours', '').replace('\n',' ')}",
                            f"LOCATION:{ev.get('salle','').replace('\n',' ')}",
                            f"DESCRIPTION:Professeur: {ev.get('professeur','').replace('\n',' ')}\\nSource: hpesgt.cnam.fr",
                            "END:VEVENT",
                        ]
                    else:
                        print(f"→ Création horaire pour {ev.get('cours')} le {d} : {start_s} - {end_s} (jour={jour})")
                        if not start_s or not end_s:
                            # should not happen, but skip defensively
                            continue
                        sh, sm = [int(x) for x in start_s.split(":")]
                        eh, em = [int(x) for x in end_s.split(":")]
                        dt_start_local = datetime(d.year, d.month, d.day, sh, sm, tzinfo=tz)
                        dt_end_local = datetime(d.year, d.month, d.day, eh, em, tzinfo=tz)
                        ics_lines += [
                            "BEGIN:VEVENT",
                            f"UID:{uid}",
                            f"DTSTAMP:{dtstamp}",
                            f"DTSTART:{to_utc_str(dt_start_local)}",
                            f"DTEND:{to_utc_str(dt_end_local)}",
                            f"SUMMARY:{ev.get('cours', '').replace('\n',' ')}",
                            f"LOCATION:{ev.get('salle','').replace('\n',' ')}",
                            f"DESCRIPTION:Professeur: {ev.get('professeur','').replace('\n',' ')}\\nSource: hpesgt.cnam.fr",
                            "END:VEVENT",
                        ]
                except Exception as e:
                    print("⚠️ Erreur génération ICS pour ", ev, e)
            d = d + timedelta(days=1)

    ics_lines.append("END:VCALENDAR")

    try:
        with open(ics_save_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ics_lines))
        print(f"\n✅ Fichier ICS généré :\n{ics_save_path}")
    except Exception as e:
        print("⚠️ Erreur lors de la sauvegarde ICS:", e)

finally:
    driver.quit()
