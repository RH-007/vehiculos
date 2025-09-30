
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
import json


## Extraccion de Informacion de segun el tipo de Vehicuklo y Condicion

def get_user_choice(prompt, choices):
    """Función para obtener una elección válida del usuario a partir de un diccionario."""
    while True:
        print(prompt)
        for key, (desc, val) in choices.items():
            print(f"  {desc} ({key})")
        choice = input("Su elección: ")
        if choice in choices:
            return choices[choice][1]
        else:
            print("\nOpción no válida. Por favor, intente de nuevo.\n")

# Definimos las opciones para que sea más fácil de mantener
TIPO_VEHICULO_CHOICES = {
    "1": ("autos", "autos"),
    "2": ("motos", "motos"),
    "3": ("camiones", "camiones")
}
CATEGORIA_CHOICES = {
    "1": ("camioneta", "camionetas-suv"),
    "2": ("sedan", "sedan"),
    "3": ("hatchback", "hatchback"),
    "4": ("pick-up", "pick-up"),
    "5": ("vans", "vans"),
    "6": ("deportivo", "deportivo")
}
UNIDAD_CHOICES = {
    "1": ("nuevo", "nuevos"),
    "2": ("usados", "usados"),
    "3": ("seminuevos", "seminuevos")
}

tipo_vehiculo = get_user_choice("¿Qué tipo de unidad quiere extraer?", TIPO_VEHICULO_CHOICES)
categoria = get_user_choice("¿Qué categoría de auto desea?", CATEGORIA_CHOICES)
unidad = get_user_choice("¿Qué condición de unidad busca?", UNIDAD_CHOICES)

print(f"\nSe extraerán datos de: {tipo_vehiculo} - {categoria}- {unidad}")

print("\nGenerando URLs a extraer...")
## Generacion de URLs a extraer


url = f"https://neoauto.com/venta-de-{tipo_vehiculo}-{unidad}--{categoria}"
print(url)


options = webdriver.ChromeOptions()
# options.add_argument("--headless")   # modo oculto
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options = options)
driver.get(url)

resultados = driver.find_element(By.CLASS_NAME, "s-results__count")

paginas_consulta = int(re.sub(r'[^\d]', '', resultados.text.split()[0]))

print("\nNumero de Anuncios a extraer:", paginas_consulta)

numero_paginas = (paginas_consulta // 20) + 1

print("\nNumero de paginas a extraer:", numero_paginas)

paginas = []

# Este bucle debe ejecutarse siempre, no solo para "usados".
for i in  range(1, numero_paginas+1):
    url_pagina = f"https://neoauto.com/venta-de-{tipo_vehiculo}-{unidad}--{categoria}?page={i}"
    paginas.append({
        "url": url_pagina,
        "tipo": unidad,
        "tipo_vehiculo": tipo_vehiculo,
        "categoria": categoria
    })

print("\nInicio de Extraccion de datos...")

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
        "Lincoln","Ram","Tesla",
    
        # China (muy usados en Latam)
        "BAIC","BYD","Changan","Chery","DFSK","Dongfeng","FAW","Foton","Geely","Great Wall",
        "Haval","JAC","Jetour","Maxus","MG","Omoda","Zotye", "JMC",
    
        # India
        "Mahindra","Tata",
    
        # Reino Unido
        "Lotus","Morgan","Noble","Vauxhall",
    
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
            
        img_urls = []
        imgs = card.find_elements(By.CSS_SELECTOR, "img.c-results-slider__img-inside, img.c-results__image, img.c-results-slider__img")  # varios selectores por si cambian

        for im in imgs:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", im)
            except:
                pass
            time.sleep(0.05)
            u = im.get_attribute("data-src") or im.get_attribute("src")
            if not u:
                srcset = im.get_attribute("data-srcset") or im.get_attribute("srcset")
                if srcset:
                    u = srcset.split(",")[0].strip().split()[0]
            if u and u not in img_urls:
                img_urls.append(u)

        img_url_primaria = img_urls[0] if img_urls else None
        
        neo_autos.append({
            "titulo": titulo,
            "tipo_vehiculo": pagina["tipo_vehiculo"],
            "categoria": pagina["categoria"],
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
            "pagina": pagina["url"],
            ## Imagenes
            "img_urls": img_urls,
        })
    

print(f"\nSe extrajeorn informacion de {len(neo_autos)} unidades\n")

## Guardando el Archivo.

ruta_salida_json = rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\7.Analisis_Autos\vehiculos\data\categoria\neo_autos_{tipo_vehiculo}_{categoria}_{unidad}.json"

print("\nGenerando archivo JSON...\n")

with open(ruta_salida_json, "w", encoding="utf-8") as f:
    json.dump(neo_autos, f, ensure_ascii=False, indent=2)

print("\nGenerando archivo CSV...\n")

neo_autos_df = pd.DataFrame(neo_autos)


ruta_salida = rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\7.Analisis_Autos\vehiculos\data\categoria\neo_autos_{tipo_vehiculo}_{categoria}_{unidad}.csv"

neo_autos_df.to_csv(ruta_salida
                    , index=False
                    , sep="|"
                    , encoding="utf-8-sig"
                    )

driver.quit() # Es una buena práctica cerrar el driver al final.

print("\nArchivo CSV generado con exito! Fin :D\n")
print(f"\nArchivo Creado: neo_autos_{tipo_vehiculo}_{categoria}_{unidad}.csv\n")
