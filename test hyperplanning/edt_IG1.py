"""Scraper for HPesgt timetable and ICS generator.

Provides a function scrape_and_generate(output_json, output_ics, class_name).
"""
import os
import re
import json
import time
import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Default output paths
JSON_DEFAULT = os.path.join(os.path.dirname(__file__), "edt_IG1.json")
ICS_DEFAULT = os.path.join(os.path.dirname(__file__), "edt_IG1.ics")


def scrape_and_generate(output_json=JSON_DEFAULT, output_ics=ICS_DEFAULT, class_name="IG1"):
    """Scrape the hyperplanning site and write JSON + ICS files.

    Returns (json_path, ics_path, stats)
    """
    # Lazy import to avoid import-time dependency
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.chrome.service import Service
    except Exception:
        raise RuntimeError("Selenium is required. Install with: pip install selenium webdriver-manager")

    options = Options()
    if os.environ.get("FORCE_HEADLESS") or not os.environ.get("DISPLAY"):
        try:
            options.add_argument("--headless=new")
        except Exception:
            options.add_argument("--headless")
    options.add_argument("--window-size=1400,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # start driver
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception:
        driver = webdriver.Chrome(options=options)

    def parse_horaire(h):
        if not h:
            return None, None
        m = re.search(r"(?:de\s*)?(\d{1,2}[:h]\d{2})\s*(?:[-–/]|à|a|au)\s*(\d{1,2}[:h]\d{2})", h)
        if m:
            return m.group(1).replace("h", ":"), m.group(2).replace("h", ":")
        times = re.findall(r"\d{1,2}[:h]\d{2}", h)
        if len(times) >= 2:
            return times[0].replace("h", ":"), times[1].replace("h", ":")
        m = re.search(r"(\d{2})(\d{2})\s*[-–/]\s*(\d{2})(\d{2})", h)
        if m:
            return f"{m.group(1)}:{m.group(2)}", f"{m.group(3)}:{m.group(4)}"
        return None, None

    def trouver_jour_par_colonnes(blocs):
        lefts = []
        for b in blocs:
            s = b.get_attribute("style") or ""
            m = re.search(r"left:\s*(-?\d+)px", s)
            if m:
                lefts.append(int(m.group(1)))
        if not lefts:
            def _f(style):
                return "Inconnu"
            return _f, ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
        unique = sorted({int(round(x)) for x in lefts})[:5]
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"][:len(unique)]
        mapping = {pos: day for pos, day in zip(unique, days)}
        def _map(style):
            m = re.search(r"left:\s*(-?\d+)px", style or "")
            if not m:
                return "Inconnu"
            val = int(m.group(1))
            nearest = min(mapping.keys(), key=lambda k: abs(k - val))
            if abs(nearest - val) <= 30:
                return mapping[nearest]
            return "Inconnu"
        return _map, days

    try:
        driver.get("https://hpesgt.cnam.fr/hp/invite")
        time.sleep(5)
        champ = driver.find_element(By.ID, "GInterface.Instances[1].Instances[1].bouton_Edit")
        champ.clear()
        champ.send_keys(class_name)
        time.sleep(1)
        champ.send_keys(Keys.ENTER)
        time.sleep(5)

        body = driver.find_element(By.TAG_NAME, "body")
        for _ in range(5):
            ActionChains(driver).move_to_element(body).send_keys(Keys.PAGE_DOWN).perform()
            time.sleep(1.0)

        blocs = driver.find_elements(By.CSS_SELECTOR, "div.EmploiDuTemps_Element")
        trouver_jour, _ = trouver_jour_par_colonnes(blocs)

        edt = []
        for bloc in blocs:
            try:
                cours_simple = bloc.find_element(By.CSS_SELECTOR, "div.cours-simple")
                horaire = (cours_simple.get_attribute("title") or "").strip()
                style = bloc.get_attribute("style") or cours_simple.get_attribute("style")
                jour = trouver_jour(style)
                labels = cours_simple.find_elements(By.TAG_NAME, "label")
                nom = labels[0].text.strip() if labels else ""
                prof = ""
                salle = ""
                for c in cours_simple.find_elements(By.CSS_SELECTOR, "div.contenu"):
                    txt = c.text.strip()
                    if not txt or txt == nom:
                        continue
                    if re.search(r"\b(Salle|Amphi)\b", txt, re.I):
                        salle = txt
                    elif not prof:
                        prof = txt
                edt.append({
                    "jour": jour,
                    "horaire": horaire,
                    "cours": nom,
                    "professeur": prof,
                    "salle": salle,
                })
            except Exception as e:
                print("Erreur bloc:", e)
                continue

        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(edt, f, ensure_ascii=False, indent=2)

        try:
            tz = ZoneInfo(os.environ.get("TZ", "Europe/Paris"))
        except Exception:
            tz = ZoneInfo("UTC")

        day_map = {"Lundi":0, "Mardi":1, "Mercredi":2, "Jeudi":3, "Vendredi":4, "Samedi":5, "Dimanche":6}
        today = datetime.now(tz).date()
        end_date = today + timedelta(days=13)

        ics = ["BEGIN:VCALENDAR", "PRODID:-//edt_IG1//EN", "VERSION:2.0", "CALSCALE:GREGORIAN"]
        cnt_hour = 0
        cnt_all = 0

        for ev in edt:
            jour = ev.get("jour")
            if not jour or jour == "Inconnu":
                continue
            wk = day_map.get(jour)
            if wk is None:
                continue
            start_s, end_s = parse_horaire(ev.get("horaire", ""))
            if not (start_s and end_s):
                start_s, end_s = parse_horaire(" ".join([ev.get('cours',''), ev.get('salle',''), ev.get('professeur',''), ev.get('horaire','')]))
            is_all = not (start_s and end_s)

            d = today
            while d <= end_date:
                if d.weekday() == wk:
                    uid = str(uuid.uuid4())
                    dtstamp = datetime.now(ZoneInfo("UTC")).strftime("%Y%m%dT%H%M%SZ")
                    if is_all:
                        cnt_all += 1
                        ics += [
                            "BEGIN:VEVENT",
                            f"UID:{uid}",
                            f"DTSTAMP:{dtstamp}",
                            f"DTSTART;VALUE=DATE:{d.strftime('%Y%m%d')}",
                            f"DTEND;VALUE=DATE:{(d+timedelta(days=1)).strftime('%Y%m%d')}",
                            f"SUMMARY:{ev.get('cours','').replace('\n',' ')} (horaire inconnu)",
                            f"LOCATION:{ev.get('salle','').replace('\n',' ')}",
                            f"DESCRIPTION:Professeur: {ev.get('professeur','').replace('\n',' ')}\\nSource: hpesgt.cnam.fr",
                            "END:VEVENT",
                        ]
                    else:
                        sh, sm = [int(x) for x in start_s.split(":")]
                        eh, em = [int(x) for x in end_s.split(":")]
                        dt_start = datetime(d.year, d.month, d.day, sh, sm, tzinfo=tz)
                        dt_end = datetime(d.year, d.month, d.day, eh, em, tzinfo=tz)
                        cnt_hour += 1
                        ics += [
                            "BEGIN:VEVENT",
                            f"UID:{uid}",
                            f"DTSTAMP:{dtstamp}",
                            f"DTSTART:{dt_start.astimezone(ZoneInfo('UTC')).strftime('%Y%m%dT%H%M%SZ')}",
                            f"DTEND:{dt_end.astimezone(ZoneInfo('UTC')).strftime('%Y%m%dT%H%M%SZ')}",
                            f"SUMMARY:{ev.get('cours','').replace('\n',' ')}",
                            f"LOCATION:{ev.get('salle','').replace('\n',' ')}",
                            f"DESCRIPTION:Professeur: {ev.get('professeur','').replace('\n',' ')}\\nSource: hpesgt.cnam.fr",
                            "END:VEVENT",
                        ]
                d += timedelta(days=1)

        ics.append("END:VCALENDAR")
        with open(output_ics, "w", encoding="utf-8") as f:
            f.write("\n".join(ics))

        return output_json, output_ics, {"hour_events": cnt_hour, "all_day": cnt_all}
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == '__main__':
    scrape_and_generate()
