
## Extraccion de datos de neoclasicos.com
## ======================================:

## Librerias
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from tqdm import tqdm  # pip install tqdm
import datetime as dt
import re


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
options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options = options)
# driver.minimize_window()


neo_autos = []

for enlace in tqdm(paginas, desc="Páginas procesadas", unit="vehiculo"):
    
    tipo = enlace["tipo"]
    link_pagina = enlace["url"]
    tipo_vehiculo = enlace["tipo_vehiculo"]
    
    driver.get(link_pagina)
    
    BRANDS = sorted([
        "Alfa Romeo","Aston Martin","Land Rover","Mercedes Benz","Great Wall",
        "Volkswagen","Chevrolet","Toyota","Hyundai","Kia","Nissan","BMW","Audi",
        "Peugeot","Renault","Mazda","Subaru","Mitsubishi","Suzuki","Haval","JAC",
        "Changan","Geely","DFSK","Chery","Volvo","Porsche","Jaguar","Jeep","Ram",
        "Dodge","Ford","Seat","Skoda","Mini","BYD","MG","GMC","Lexus","Citroën","Citroen"
    ], key=len, reverse=True)


    ## NOMBRE, MARCA, MODELO, AÑO
    
    encabezado = driver.find_elements(By.CLASS_NAME, "c-results__header")

    titulo_auto = []
    marca_auto = []
    modelo_auto = []
    año_auto = []

    for enc in encabezado:
        titulo = enc.text
        titulo_ = titulo.split("\n", 1)[0].strip()
        for brand in BRANDS:
            if brand in titulo_:
                año = titulo_.split()[-1]
                modelo = titulo_.replace(brand, "").replace(año, "").strip()

                titulo_auto.append(titulo_)
                marca_auto.append(brand)    
                modelo_auto.append(modelo)
                año_auto.append(año)
                
    ## PRECIO
    precio = driver.find_elements(By.CLASS_NAME, "c-results-mount__price")
    precio_auto = []
    for prec in precio:
        costo = prec.text
        precio_auto.append(costo)

    precio_auto[0]
    
    ## TAGS
    tag =  driver.find_elements(By.CLASS_NAME, "c-results-tag__stick")
    tags = []
    for det in tag:
        descripcion = det.text
        tags.append(descripcion)
    
    ## DETALLE DE AUTO
    detalles = driver.find_elements(By.CLASS_NAME, "c-results-details__description")

    detalle_auto = []
    combustible_auto = []
    transmision_auto = []
    caja_auto = []
    kilometraje_auto = []
    ubicacion_auto = []

    for detalle in detalles:

        detalle_text = detalle.text

        # normaliza y separa líneas no vacías
        t = re.sub(r'[\r\xa0]', ' ', detalle_text).strip()
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

        # 4) “modelo/etiqueta” (última línea)
        modelo_line = lines[-1] if lines else None

        detalle_auto.append(detalle_text)
        combustible_auto.append(combustible)
        transmision_auto.append(tipo_transmision)
        caja_auto.append(caja)
        kilometraje_auto.append(kilometraje_km)
        ubicacion_auto.append(ubicacion)
    
    ## URL DE AUTO
    url_auto = []
    enlace = driver.find_elements(By.CLASS_NAME, "c-results__link")   
    for link in enlace:
        url = link.get_attribute("href")    
        url_auto.append(url)
    
    ## ALMACENAMIENTO DE DATOS
    
    zip_list = zip(titulo_auto, marca_auto, modelo_auto, año_auto, precio_auto, tags, detalle_auto, combustible_auto, transmision_auto, caja_auto, kilometraje_auto, ubicacion_auto, url_auto)
    
    data_auto_page = []
    for titulo_auto_, marca_auto_, modelo_auto_, año_auto_, precio_auto_, tags_, detalle_auto_, combustible_auto_, transmision_auto_, caja_auto_, kilometraje_auto_, ubicacion_auto_, url_auto_ in zip_list:
        data_auto_page.append({
            "titulo": titulo_auto_,
            "tipo_vehiculo": tipo_vehiculo,
            "marca": marca_auto_,
            "modelo": modelo_auto_,
            "año": año_auto_,
            "precio": precio_auto_,
            "detalle": detalle_auto_,
            "combustible": combustible_auto_,
            "transmision": transmision_auto_,
            "caja": caja_auto_,
            "kilometraje": kilometraje_auto_,
            "ubicacion": ubicacion_auto_,
            "url_auto":url_auto_,
            "tags": tags_,
            "tipo": tipo,
            "pagina": link_pagina
        })
        
    neo_autos.extend(data_auto_page)
    

driver.quit()

print(f"\nSe extrajeorn informacion de {len(neo_autos)} unidades\n")

## Guardando el Archivo.

print("\nGenerando archivo CSV...\n")

neo_autos_df = pd.DataFrame(neo_autos)


ruta_salida = rf"C:\Users\PC\Desktop\Proyectos\Proyectos_Py\7.Analisis_Autos\data\neo_autos_{tipo_vehiculo}_{unidad}.csv"

neo_autos_df.to_csv(ruta_salida
                    , index=False
                    , sep="|"
                    , encoding="utf-8-sig"
                    )

print("\nArchivo CSV generado con exito! Fin :D\n")
