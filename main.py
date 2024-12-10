# Importe für Zeitverwaltung und zufällige Operationen.
import logging
import uuid 
import schedule  # Für zeitgesteuerte Aufgaben
import time  # Zeitverzögerungen, Zufälligkeit und eindeutige IDs.
import random
import uuid
# Selenium-Bibliotheken für Webautomatisierung und Fehlerbehandlung.
from selenium.webdriver.support.ui import WebDriverWait  # Bedingungen abwarten
from selenium.webdriver.support import expected_conditions as EC  # Konkrete Wartebedingungen
from selenium.webdriver.common.by import By  # Elemente selektieren.
from selenium import webdriver # Browser steuern
from selenium.common.exceptions import  WebDriverException  # Fehler behandeln.
from selenium.webdriver.chrome.options import Options  # Browseroptionen einstellen.
from selenium.webdriver.chrome.service import Service  # Dienst verwalten
from webdriver_manager.chrome import ChromeDriverManager  # Treiberverwaltung. 
from pymongo import MongoClient  # MongoDB-Operationen 
import requests  # HTTP-Anfragen
from urllib.parse import urlparse  # URL-Parsing

def setup_driver(proxy=None):
# Auswahl und Konfiguration des WebDriver, einschließlich Proxy und User-Agent.
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
    ]# Erstellen einer Liste von User-Agents, um Blocking zu vermeiden.

    user_agent = random.choice(user_agents)
    options = Options()
    options.headless = False # Browser im sichtbaren Modus laufen lassen 
    options.add_argument("--no-sandbox") # Sandbox für den Chrome Driver deaktivieren.
    options.add_argument("--disable-infobars")# Infobalken im Browser deaktivieren.
    options.add_argument("--disable-extensions")# Browser-Erweiterungen deaktivieren.
    options.add_argument('--disable-gpu-sandbox')# GPU-Sandbox im Browser deaktivieren.
    options.add_argument('--window-size=1920,1080')# Fenstergröße festlegen.
    options.add_argument('--disable-dev-shm-usage')# Beschränkung des shared memory deaktivieren.
    options.add_argument(f'user-agent={user_agent}')# Festlegen des User-Agents.
    try:
        service = Service(ChromeDriverManager().install())# ChromeDriver installieren.
        driver = webdriver.Chrome(service=service, options=options)# WebDriver instanzieren.
    except Exception as e:
        print(f"Fehler beim Initialisieren des WebDrivers: {e}")
        return None

    return driver 

def check_robots_txt(base_url):
    # Parsen der URL, um die Basis-Domain zu extrahieren 
    parsed_url = urlparse(base_url) # Startzeit
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    try:
        response = requests.get(f"{base_domain}/robots.txt")
        if response.status_code == 200 and "Disallow: /" not in response.text:
            print("Scraping is allowed by robots.txt")
            return True
        else: 
            print("Scraping is disallowed by robots.txt")
        # Überprüfung des Statuscodes der Antwort und des Inhalts der robots.txt
            return False
    except requests.RequestException:
        # Fehlerbehandlung, falls die Anfrage fehlschlägt
        print("Failed to access robots.txt")
        return False

def load_url_with_retry(driver, url, max_attempts=5):
    attempt = 0 # Initialisierung des Zählers für die Versuche
    while attempt < max_attempts: 
        try:
            driver.get(url)# Versuch, die URL zu laden
            break  # Bei Erfolg die Schleife verlassen
        except WebDriverException as e:
            print(f"Fehler beim Laden der Seite: {e}, Versuch {attempt + 1} von {max_attempts}")
            time.sleep(5)  # Kurze Pause, bevor erneut versucht wird
            attempt += 1 # Inkrement des Versuchszählers

def scrape_page(driver, url, jobs_collection):
    # Navigiere zur URL
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "body")))
    time.sleep(6)  # Zusätzliches Warten, um sicherzustellen, dass alle Skripte vollständig geladen sind
  
    try:# Versuch, alle Joblinks auf der Seite zu finden
        job_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.ergebnisliste-item[href]"))
        )
        job_urls = [je.get_attribute("href") for je in job_elements]
    except Exception as e:
        print(f"Error locating job elements on page {url}: {e}")
        return []
    # Verarbeite jede gefundene Job-URL
    for job_url in job_urls:
        driver.get(job_url)
        time.sleep(3)   # Wartet, bis die Detailseite geladen ist.
 
        job_id = uuid.uuid4().hex # Generiere eine eindeutige UUID basierend auf der URL
        job_data = {  
            "url": job_url,
            "title": "",
            "employer": "",
            "location": "",
            "entry_date": "", 
            "description": "",
            "contract_type": ""
        }
        # Versuche, die Jobdaten zu extrahieren ()
        try:
            job_data["title"] = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "#detail-kopfbereich-titel"))
            ).text
            job_data["employer"] = driver.find_element(By.CSS_SELECTOR, "#--").text
            job_data["location"] = driver.find_element(By.CSS_SELECTOR, "#--").text
            job_data["entry_date"] = driver.find_element(By.CSS_SELECTOR, "#--").text 
            job_data["description"] = driver.find_element(By.CSS_SELECTOR, "#--").get_attribute("textContent")
            job_data["contract_type"] = driver.find_element(By.CSS_SELECTOR, "#--").text
        except Exception as e:
            print(f"Failed to extract complete data for job due to: {e}") 
            continue # Überspringe diesen Job, wenn ein Problem auftritt

        #Aktualisiere MongoDB: Aktualisiere vorhandenen Eintrag oder füge neuen ein, falls nicht vorhanden
        jobs_collection.update_one(
            {"url": job_url},  # Verwende die URL als eindeutigen Identifikator
            {"$set": job_data},   # Aktualisiere das Dokument mit den Jobdaten
            upsert=True # Füge das Dokument hinzu, falls es nicht existiert
        ) 
        print(f"Processed job: {job_url} (ID: {job_id})")

    return job_urls

def find_valid_proxy():
    # Öffne die Datei, die die Proxy-Liste enthält
    with open("proxy_list.txt", "r") as file:
        for line in file:
            proxy = line.strip() 
            # Überprüft, ob der Proxy gültig ist
            if check_proxy(proxy):
                print(f"Valid proxy found: {proxy}")
                return proxy
    return None# Gib None zurück, wenn kein gültiger Proxy gefunden wurde

def check_proxy(proxy):

    try:
        # Versuche, eine HTTP-Anfrage über den Proxy zu senden
        res = requests.get('https://httpbin.org/ip', proxies={"http": proxy, "https": proxy}, 
                           timeout=5)# Setze ein Timeout von 5 Sekunden
        res.raise_for_status()
        return True# Der Proxy ist gültig, wenn keine Ausnahme ausgelöst wird
    except requests.RequestException:
        return False# Der Proxy ist ungültig, wenn eine Ausnahme auftritt

def setup_logging():
     # Logger für die Anwendung 'Webscraper' erstellen und konfigurieren
    logger = logging.getLogger('Webscraper') 
    logger.setLevel(logging.INFO)  # Setze das Log-Level auf INFO
    # Formatter erstellen, der angibt, wie die Log-Nachrichten formatiert werden
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # File Handler erstellen, der in die Datei schreibt
    file_handler = logging.FileHandler('webscraper.log')
    file_handler.setFormatter(formatter)
    # Stream Handler erstellen, der die Logs in die Konsole schreibt
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    # Handler zum Logger hinzufügen
    logger.addHandler(file_handler) 
    logger.addHandler(stream_handler)

    return logger
    
def main():
    logger = setup_logging()
    base_url = "https://wwww."#Yourwebsite for scraping
    logger.info("Enter the number of pages you want to scrape:")
    num_pages_to_scrape = int(input())
# Verbindung zu MongoDB herstellen
    client = MongoClient('mongodb://localhost:27017/')
    db = client['Flask-app']
    jobs_collection = db['jobs']
 # Überprüfen, ob das Scraping durch robots.txt erlaunt ist
    if not check_robots_txt(base_url):
        logger.warning("Scraping disallowed by robots.txt")
        return
# Einen gültigen Proxy für den Scraping-Prozess finden 
    valid_proxy = find_valid_proxy() 
    driver = setup_driver(proxy=valid_proxy)
# Benutzer auffordern, die Zeit für das Scraping einzugeben, oder sofort zu beginnen
    logger.info("Enter the scraping time (HH:MM format), or type 'now' to start immediately:")
    schedule_time = input().strip()
    if schedule_time.lower() == 'now':
        for page in range(1, num_pages_to_scrape + 1):
            url = f"{base_url}&page={page}"
            scrape_page(driver, url, jobs_collection)
            logger.info(f"Scraped page {page} immediately.")
    else: 
        # Zeitgesteuertes Scraping einrichten.
        def scheduled_scraping():
            for page in range(1, num_pages_to_scrape + 1):
                url = f"{base_url}&page={page}"
                scrape_page(driver, url, jobs_collection)
                logger.info(f"Scraped page {page} at scheduled time.")
        schedule.every().day.at(schedule_time).do(scheduled_scraping)
        logger.info(f"Scheduled scraping with proxy {valid_proxy} at {schedule_time}.")
        try: 
            while True:
                schedule.run_pending()
                time.sleep(60) # Pausiert das Programm für eine Minute.
        except KeyboardInterrupt:
            logger.info("User interrupted the process.")

    driver.quit()
    logger.info("WebDriver closed.")

if __name__ == '__main__':
    main()