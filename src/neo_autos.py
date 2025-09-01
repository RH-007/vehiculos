
## Extraccion de datos de neoclasicos.com
## ======================================:

## Librerias
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from tqdm import tqdm  # pip install tqdm
import datetime as dt
import re, time


## Extraccion de Informacion de segun el tipo de Vehicuklo y Condicion

while True:
    tipo = input("Es necesario preguntar que tipo de unidad quiere extraer: autos (1), motos (2) o camiones (3): ")

    if tipo == "1":
        tipo_vehiculo = "autos"
        break
    elif tipo == "2":
        tipo_vehiculo = "motos"
        break
    elif tipo == "3":
        tipo_vehiculo = "camiones"  
        break  
    
while True:
    tipo = input("Es necesario preguntar si quiere una unidad: nuevo (1), usados (2) o seminuevos (3): ")

    unidad = ""
    if tipo == "1":
        unidad = "nuevos"
        break
    elif tipo == "2":
        unidad = "usados"
        break
    elif tipo == "3":
        unidad = "seminuevos"
        break  

print(f"\nSe extraerán datos de: {tipo_vehiculo} - {unidad}")

print("\nGenerando URLs a extraer...")
## Generacion de URLs a extraer

paginas = []

if unidad == "usados":
    for i in  range(1, 182):
        url = f"https://neoauto.com/venta-de-{tipo_vehiculo}-{unidad}?page={i}"
        paginas.append({
            "url": url,
            "tipo": unidad,
            "tipo_vehiculo": tipo_vehiculo
        })

if unidad == "nuevos":
    for i in  range(1, 7):
        url = f"https://neoauto.com/venta-de-{tipo_vehiculo}-{unidad}?page={i}"
        paginas.append({
            "url": url,
            "tipo": unidad,
            "tipo_vehiculo": tipo_vehiculo
        })

if unidad == "seminuevos":
    for i in  range(1, 44):
        url = f"https://neoauto.com/venta-de-{tipo_vehiculo}-{unidad}?page={i}"
        paginas.append({
            "url": url,
            "tipo": unidad,
            "tipo_vehiculo": tipo_vehiculo
        })

print("\nInicio de Extraccion de datos...")

options = webdriver.ChromeOptions()
# options.add_argument("--headless")   # modo oculto
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options = options)
# driver.minimize_window()

# --- Config mínimo ---
YEAR_RX  = re.compile(r'\b(19[8-9]\d|20[0-3]\d)\b')
NOISE_RX = re.compile(r'\bauto\s+nuev[oa]s?\b', re.I)
BRANDS = sorted([
        # Europa
        "Alfa Romeo","Aston Martin","Audi","Bentley","BMW","Bugatti","Citroen","Cupra",
        "Dacia","Ferrari","Fiat","Jaguar","Lamborghini","Land Rover","Maserati","Maybach",
        "McLaren","Mercedes Benz","Mini","Opel","Peugeot","Porsche","Renault","Rolls Royce",
        "Seat","Skoda","Smart","Volkswagen","Volvo",
    
        # Japón
        "Acura","Daihatsu","Honda","Infiniti","Isuzu","Lexus","Mazda","Mitsubishi",
        "Nissan","Subaru","Suzuki","Toyota",
    
        # Corea
        "Hyundai","Genesis","Kia","SsangYong",
    
        # Estados Unidos
        "Buick","Cadillac","Chevrolet","Chrysler","Dodge","Ford","GMC","Hummer","Jeep",
        "Lincoln","Ram","Tesla","Plymouth",
    
        # China (muy usados en Latam)
        "BAIC","BYD","Changan","Chery","DFSK","Dongfeng","FAW","Foton","Geely","Great Wall",
        "Haval","JAC","Jetour","Maxus","MG","Omoda","Zotye", "JMC", "Gac", "Soueast"
    
        # India
        "Mahindra","Tata",
    
        # Reino Unido
        "Lotus","Morgan","Noble","Vauxhall", "Mc Laren", "Lancia",
    
        # Otros/Exóticos
        "Abarth","Apollo","Arash","Arrinera","Artega","Brilliance","Caterham","DeLorean",
        "Denza","Fisker","Koenigsegg","Lucid","Pagani","Polestar","Rimac","Rover","Saab",
        "Scion","Spyker","Weismann","Zenvo"
    ], key=len, reverse=True)

def clean_title(s):  # quita "AUTO NUEVO", espacios dobles
    return re.sub(r'\s+', ' ', NOISE_RX.sub('', s)).strip()

def parse_brand_model_year(t):
    t = clean_title(t)
    # año: último match si hay varios
    ys = YEAR_RX.findall(t); anio = ys[-1] if ys else None
    # marca: primera que aparezca (BRANDS ya está ordenado por longitud desc)
    tl = t.lower()
    marca = next((b for b in BRANDS if b.lower() in tl), "Otra Marca")
    # modelo: t sin marca ni año
    modelo = re.sub(re.escape(marca), '', t, flags=re.I).strip() if marca != "Otra Marca" else t
    if anio: modelo = re.sub(rf'\b{anio}\b', '', modelo).strip()
    return t, marca, modelo, anio

neo_autos = []

for pagina in paginas:  # pagina = {"url": ..., "tipo": ..., "tipo_vehiculo": ...}
    driver.get(pagina["url"])

    # 1) espera a que aparezcan resultados
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.c-results__link")))

    # 2) scroll simple (3–4 bajadas) para forzar lazy-load
    prev = 0
    for _ in range(4):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)
        n = len(driver.find_elements(By.CSS_SELECTOR, "a.c-results__link"))
        if n == prev: break
        prev = n

    # 3) recorre por tarjeta (evita desalineaciones)
    cards = driver.find_elements(By.CSS_SELECTOR, "a.c-results__link")
    vistos = set()

    for a in cards:
        url = a.get_attribute("href")
        if not url or url in vistos: 
            continue
        vistos.add(url)

        # sube al contenedor de la card (si falla, usamos el link como fallback)
        try:
            card = a.find_element(By.XPATH, "./ancestor::*[self::li or self::article][1]")
        except:
            card = a

        # título
        try:
            titulo_raw = card.find_element(By.CSS_SELECTOR, ".c-results__header").text
        except:
            titulo_raw = ""

        titulo, marca, modelo, anio = parse_brand_model_year(titulo_raw)

        # precio (si no hay, None)
        try:
            precio = card.find_element(By.CSS_SELECTOR, ".c-results-mount__price").text

        except:
            precio = None

        # detalle (opcional)
        try:
            detalle = card.find_element(By.CSS_SELECTOR, ".c-results-details__description").text

            # normaliza y separa líneas no vacías
            t = re.sub(r'[\r\xa0]', ' ', detalle).strip()
            lines = [l.strip() for l in t.splitlines() if l.strip()]

            # 1) combustible y transmisión (vienen en la 1ra línea separados por "|")
            combustible = transmision_raw = None
            if lines:
                p0 = re.split(r'\s*\|\s*', lines[0])  # acepta con o sin espacios: "Gasolina|Automática - Secuencial"
                combustible = p0[0].title() if p0 else None
                transmision_raw = p0[1] if len(p0) > 1 else None

            # 1.1) separa transmisión en tipo y caja si viene "Automática - Secuencial"
            tipo_transmision = caja = None
            if transmision_raw:
                parts = [p.strip() for p in transmision_raw.split("-")]
                tipo_transmision = parts[0]
                caja = parts[1] if len(parts) > 1 else None

            # 2) kilometraje (busca en todo el texto)
            km_m = re.search(r'(\d[\d.,]*)\s*kms?', t, flags=re.I)
            kilometraje_km = int(re.sub(r'[^\d]', '', km_m.group(1))) if km_m else None

            # 3) ubicación (primera línea con coma que no sea "Kms")
            ubicacion = next((l for l in lines if ',' in l and 'km' not in l.lower()), None)
            
        except:
            detalle = ""
            

        # tags (opcionales)
        tags = [e.text.strip() for e in card.find_elements(By.CSS_SELECTOR, ".c-results-tag__stick") if e.text.strip()]

        if len(tags) == 1:
            tags = tags[0]
        

        neo_autos.append({
            "titulo": titulo,
            "tipo_vehiculo": pagina["tipo_vehiculo"],
            "marca": marca,
            "modelo": modelo,
            "año": anio,
            "precio": precio,
            "detalle": detalle,
            "combustible": combustible,
            "tipo_transmision": tipo_transmision,
            "caja": caja,
            "kilometraje_km": kilometraje_km,
            "ubicacion": ubicacion, 
            "tags": tags,
            "url_auto": url,
            "tipo": pagina["tipo"],
            "pagina": pagina["url"]
        })
    

driver.quit()

print(f"\nSe extrajeorn informacion de {len(neo_autos)} unidades\n")

## Guardando el Archivo.

print("\nGenerando archivo CSV...\n")

neo_autos_df = pd.DataFrame(neo_autos)


ruta_salida = rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\7.Analisis_Autos\vehiculos\data\neo_autos_{tipo_vehiculo}_{unidad}.csv"

neo_autos_df.to_csv(ruta_salida
                    , index=False
                    , sep="|"
                    , encoding="utf-8-sig"
                    )

print("\nArchivo CSV generado con exito! Fin :D\n")
