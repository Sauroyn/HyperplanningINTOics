from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import os
import re

save_path = r"/home/aurelien/Bureau/test hyperplanning/edt_IG1.json"

options = Options()
# options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# === correspondance entre "left" et le jour ===
jours_map = {
    -1: "Lundi",
    161: "Mardi",
    323: "Mercredi",
    485: "Jeudi",
    647: "Vendredi"
}

def trouver_jour(style):
    """Extrait la valeur 'left' du style et renvoie le jour correspondant"""
    match = re.search(r"left:\s*(-?\d+)px", style)
    if match:
        left_val = int(match.group(1))
        # on cherche le jour le plus proche (parfois +/- 1 px d'écart)
        for val, jour in jours_map.items():
            if abs(left_val - val) <= 5:
                return jour
    return "Inconnu"

try:
    print("-> Ouverture du site...")
    driver.get("https://hpesgt.cnam.fr/hp/invite")
    time.sleep(5)

    # === Sélection de la classe IG1 ===
    print("-> Sélection de la classe IG1...")
    champ = driver.find_element(By.ID, "GInterface.Instances[1].Instances[1].bouton_Edit")
    champ.clear()
    champ.send_keys("IG1")
    time.sleep(1)
    champ.send_keys(Keys.ENTER)
    time.sleep(5)

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

    for bloc in cours_elements:
        try:
            cours_simple = bloc.find_element(By.CSS_SELECTOR, "div.cours-simple")
            horaire = cours_simple.get_attribute("title").strip()
            style = bloc.get_attribute("style")
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

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(edt, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Emploi du temps complet sauvegardé dans :\n{save_path}")

finally:
    driver.quit()
