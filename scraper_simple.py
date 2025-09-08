#!/usr/bin/env python3
"""
Simple Tinder Scraper ES - Versión Simplificada
Basado exactamente en el scraper_final.py funcional
"""

import time
import json
import random
import os
import re
import argparse
from datetime import datetime, timedelta

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import undetected_chromedriver as uc

# OCR imports
import cv2
import pytesseract
import numpy as np


def load_config(config_path="config_simple.json"):
    """Carga la configuración desde archivo JSON"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo de configuración: {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error al leer el archivo de configuración: {config_path}")
        return None


def extract_name_and_age_from_image(image_path):
    """Extrae cualquier texto de la imagen usando OCR."""
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ No se pudo abrir la imagen: {image_path}")
        return False, None
    
    # Aumentar resolución para mejorar OCR
    image_resized = cv2.resize(image, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LINEAR)

    # OCR preprocessing
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (1, 1), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # OCR config
    config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(thresh, config=config)
    print("🧾 OCR crudo:", repr(text))

    # Verificar si hay cualquier carácter en el texto (incluso un punto)
    has_any_text = bool(re.search(r'[A-Za-zÀ-ÿ0-9\.]', text))
    
    if has_any_text:
        print("✅ OCR detectó algún carácter en la imagen")
    else:
        print("❌ OCR no detectó ningún carácter")
    
    return has_any_text, image


def detect_verification_icon(image, template_path, threshold=0.75):
    """
    Detecta si el perfil está verificado buscando el icono de verificación en la imagen.
    Retorna "Yes" si se encuentra el icono, "No" si no, o "NA" si hay un error.
    """
    if not os.path.exists(template_path):
        print(f"❌ No se encontró la plantilla de verificación: {template_path}")
        return "NA"
    
    template = cv2.imread(template_path)
    if template is None:
        print(f"❌ No se pudo cargar la plantilla de verificación: {template_path}")
        return "NA"
    
    # Convertir a escala de grises tanto la imagen como la plantilla
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Realizar template matching
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    
    is_verified = "Yes" if len(locations[0]) > 0 else "No"
    print(f"🔍 Verificación de perfil: {is_verified}")
    
    return is_verified


def check_profile_verified(screenshot_path, config):
    """
    Comprueba si un perfil está verificado a partir de su captura de pantalla.
    """
    template_path = os.path.join(config['output']['template_directory'], "tick_icon.png")
    
    if not os.path.exists(template_path):
        print(f"❌ Plantilla de verificación no encontrada en {template_path}")
        print("⚠️ Creando directorio para plantillas...")
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        print("⚠️ Por favor, añade una imagen del icono de verificación en", template_path)
        return "NA"
    
    image = cv2.imread(screenshot_path)
    if image is None:
        print(f"❌ No se pudo abrir la imagen: {screenshot_path}")
        return "NA"
        
    return detect_verification_icon(image, template_path, config['ocr']['verification_threshold'])


def take_screenshot(driver, name, config):
    """
    Toma una captura de pantalla de un elemento específico y la guarda con nombre y timestamp.
    Retorna el ID del elemento y la ruta del archivo.
    """
    try:
        # XPath del elemento que quieres capturar (predefinido)
        xpath = "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div/div[1]/div[1]/div[1]/div"
        
        # Crear directorio si no existe
        screenshots_dir = config['output']['screenshots_directory']
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)

        # Buscar el elemento por XPath
        element = driver.find_element(By.XPATH, xpath)

        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        element_id = f"{name}_{timestamp}"
        filename = f"{screenshots_dir}/{element_id}.png"

        # Capturar solo el elemento
        element.screenshot(filename)
        print(f"📸 Captura de elemento guardada: {filename}")
        return element_id, filename
    except Exception as e:
        print(f"❌ Error al guardar captura del elemento: {str(e)}")
        return None, None


class ScrapingStats:
    def __init__(self):
        self.start_time = datetime.now()
        self.profiles_scraped = 0
        self.likes = 0
        self.nopes = 0
        
    def add_action(self, action):
        if action == Keys.ARROW_RIGHT:
            self.likes += 1
        else:
            self.nopes += 1
        self.profiles_scraped += 1
    
    def get_elapsed_time(self):
        elapsed = datetime.now() - self.start_time
        return str(timedelta(seconds=int(elapsed.total_seconds())))
    
    def print_stats(self):
        os.system('clear')  # Limpia la terminal
        print("=" * 50)
        print(f"🕒 Tiempo transcurrido: {self.get_elapsed_time()}")
        print(f"👥 Perfiles procesados: {self.profiles_scraped}")
        print(f"💚 Likes dados: {self.likes}")
        print(f"❌ Nopes dados: {self.nopes}")
        print("=" * 50)


def save_profiles(new_profiles, config):
    """Guarda los perfiles en formato JSON"""
    filename = config['output']['filename']
    
    try:
        # Validate and clean profiles before saving
        cleaned_profiles = []
        for profile in new_profiles:
            cleaned_profile = {}
            for key, value in profile.items():
                # Convert any WebElement to string
                if hasattr(value, 'text'):
                    cleaned_profile[key] = value.text.strip()
                # Handle lists and convert to pipe-separated string
                elif isinstance(value, list):
                    if value:
                        if all(isinstance(item, str) for item in value):
                            cleaned_profile[key] = " | ".join(value)
                        else:
                            cleaned_profile[key] = " | ".join([str(item) for item in value])
                    else:
                        cleaned_profile[key] = "NA"
                else:
                    cleaned_profile[key] = value

            # Clean specific fields that should always be strings
            fields_to_join = ["intereses", "otros", "horoscopo", "educacion", "hijos", 
                            "vacunacion", "personalidad", "comunicacion", "amor"]
            
            for field in fields_to_join:
                if field in cleaned_profile:
                    if isinstance(cleaned_profile[field], list):
                        if cleaned_profile[field]:
                            cleaned_profile[field] = " | ".join(cleaned_profile[field])
                        else:
                            cleaned_profile[field] = "NA"

            cleaned_profiles.append(cleaned_profile)

        # Create file if it doesn't exist
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

        # Read existing profiles
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_profiles = json.load(f)
                if not isinstance(existing_profiles, list):
                    existing_profiles = []
            except json.JSONDecodeError:
                existing_profiles = []

        # Add new profiles
        existing_profiles.extend(cleaned_profiles)

        # Save all profiles
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_profiles, f, indent=4, ensure_ascii=False)
            print(f"✅ Guardados {len(cleaned_profiles)} perfiles. Total: {len(existing_profiles)}")

    except Exception as e:
        print(f"❌ Error al guardar los perfiles: {str(e)}")


def setup_driver():
    """Configura e inicializa el driver de Chrome"""
    options = webdriver.ChromeOptions() 
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        # First attempt: Try with Chromium driver
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Error with Chromium driver: {e}")
        try:
            # Second attempt: Use default Chrome driver with force option
            service = Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Error with Google Chrome driver: {e}")
            # Third attempt: Use direct download
            import subprocess
            
            # Download the latest ChromeDriver directly
            print("Attempting to download ChromeDriver manually...")
            os.system("pip install --upgrade chromedriver-binary-auto")
            
            # Use the path from chromedriver-binary
            from chromedriver_binary import chromedriver_filename
            service = Service(executable_path=chromedriver_filename)
            driver = webdriver.Chrome(service=service, options=options)

    # Add stealth JS to make it harder for sites to detect automation
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """
    })
    
    return driver


def extraer_urls(driver):
    """Extrae URLs de imágenes de perfil"""
    elements = driver.find_elements(By.XPATH, "//*[contains(@style, 'background-image')]")
    urls = set()
    for el in elements:
        style = el.get_attribute("style")
        match = re.search(r'url\("?(https:[^)"]+)"?\)', style)
        if (match):
            url = match.group(1)
            if ".webp" in url and len(url) > 250: 
                urls.add(url)
    return urls


def cerrar_ventanas_emergentes(driver):
    """Intenta cerrar ventanas emergentes, botones 'No me interesa', etc."""
    try:
        cerrar_buttons = [
            '//*[@id="c478825258"]/div/div/div[1]/div/div[3]/button',
            "//button[@title='Volver a intentarlo' or .//span[text()='Cerrar']]",
            "//img[contains(@src, 'https://tinder.com/static/build')]",
            "//span[text()='VAMOS ALLÁ']/ancestor::button"
        ]
        
        for xpath in cerrar_buttons:
            try:
                button = driver.find_element(By.XPATH, xpath)
                if button.is_displayed():
                    button.click()
                    time.sleep(0.2)
                    print(f"✅ Botón cerrado con XPath: {xpath}")
            except:
                continue

        # Intentar con botones "No me interesa", "No, gracias", etc.
        button_selectors = [
            "//div[contains(text(), 'No me interesa')]",
            "/html/body/div[2]/div/div/button[2]/div[2]/div[2]/div",
            "//div[@class='lxn9zzn' and contains(text(), 'No, gracias')]",
            "//div[contains(text(), 'No, gracias')]",
            "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div/div/div[1]/div/div/div[1]/a/div/svg",
            "/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div/div/div[1]/div/div/div[1]/a"
        ]
        
        for selector in button_selectors:
            try:
                button = driver.find_element(By.XPATH, selector)
                if button.is_displayed():
                    button.click()
                    print(f"✅ Botón 'No me interesa' pulsado con XPath: {selector}")
                    time.sleep(0.2)
                    break
            except:
                continue

    except Exception as e:
        print(f"⚠️ Error al cerrar ventanas emergentes: {str(e)}")


def verificar_nombre_con_ocr(nombre_selenium, ruta_imagen, config, max_intentos=3):
    """
    Verifica si el OCR detecta cualquier texto (incluso un punto).
    Retorna True si se detecta cualquier carácter, False en caso contrario.
    También verifica si el perfil está verificado.
    """
    is_verified = "NA"
    
    for intento in range(max_intentos):
        has_text, imagen = extract_name_and_age_from_image(ruta_imagen)
        
        # Verificar si el perfil está verificado (solo en el primer intento o si no se ha detectado)
        if is_verified == "NA" and imagen is not None:
            template_path = os.path.join(config['output']['template_directory'], "tick_icon.png")
            is_verified = detect_verification_icon(imagen, template_path, config['ocr']['verification_threshold'])
        
        print(f"📊 Obtenido: '{nombre_selenium}' (Selenium)")
        print(f"✓ Perfil verificado: {is_verified}")
        
        # Verificar simplemente si el OCR detectó cualquier carácter
        if has_text:
            print("✅ Verificación exitosa: OCR detectó caracteres")
            # Eliminar la imagen después de la verificación exitosa
            if config['output']['clean_screenshots_after_verification']:
                try:
                    if os.path.exists(ruta_imagen):
                        os.remove(ruta_imagen)
                except Exception:
                    pass
            return True, is_verified
        
        # Si no se detectó texto, intentar cerrar ventanas y volver a capturar
        if intento < max_intentos - 1:
            print(f"⚠️ Intento {intento + 1} fallido, reintentando...")
            time.sleep(0.2)
    
    print("❌ Verificación fallida: OCR no detectó ningún carácter")
    # Eliminar la imagen tras verificación fallida
    if config['output']['clean_screenshots_after_verification']:
        try:
            if os.path.exists(ruta_imagen):
                os.remove(ruta_imagen)
        except Exception:
            pass
    return False, is_verified


def scrape_profile(driver, config):
    """Función principal para extraer un perfil completo"""
    MAX_RETRIES = config['scraping']['max_retries']
    match_close_attempts = 0

    for attempt in range(MAX_RETRIES):
        try:
            # Cerrar ventanas emergentes
            while True:
                try:
                    cerrar_button = driver.find_element(By.XPATH, '//*[@id="c478825258"]/div/div/div[1]/div/div[3]/button')
                    cerrar_button.click()
                    time.sleep(0.2)
                    match_close_attempts += 1

                    if match_close_attempts >= 4:
                        print("⚠️ Demasiados intentos de cerrar match. Recargando página...")
                        driver.refresh()
                        time.sleep(10)
                        match_close_attempts = 0
                        continue

                except:
                    try:
                        cerrar_button_alt = driver.find_element(By.XPATH, "//button[@title='Volver a intentarlo' or .//span[text()='Cerrar']]")
                        cerrar_button_alt.click()
                        time.sleep(0.2)
                        match_close_attempts += 1

                        if match_close_attempts >= 4:
                            print("⚠️ Demasiados intentos de cerrar match. Recargando página...")
                            driver.refresh()
                            time.sleep(10)
                            match_close_attempts = 0
                            continue

                    except:
                        try:
                            boton_imagen = driver.find_element(By.XPATH, "//img[contains(@src, 'https://tinder.com/static/build')]")
                            boton_imagen.click()
                            time.sleep(0.2)
                        except:
                            try:
                                vamos_alla_button = driver.find_element(By.XPATH, "//span[text()='VAMOS ALLÁ']/ancestor::button")
                                vamos_alla_button.click()
                                time.sleep(0.2)
                            except:
                                pass
                        match_close_attempts = 0

                # Navegación básica
                try:
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
                    time.sleep(0.4)
                    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_UP)
                    time.sleep(0.4)
                except:
                    print("⚠ No se pudo presionar las teclas de flecha.")

                # Obtener nombre y edad
                try:
                    name = driver.find_element(By.XPATH, "//span[contains(@class, 'Pend(8px)')]").text.strip()
                except:
                    try:
                        name = driver.find_element(By.XPATH, "//h1[contains(@aria-label, 'años')]").get_attribute("aria-label").split()[0]
                    except:
                        name = ""
                
                try:
                    age = driver.find_element(By.XPATH, "//span[contains(@class, 'Whs(nw)') and contains(@class, 'Typs(display-2-regular)')]").text.strip()
                except:
                    age = ""

                # Tomar captura y verificar con OCR
                if name:
                    profile_id, screenshot_path = take_screenshot(driver, name, config)
                    
                    if screenshot_path:
                        # Verificar nombre usando OCR y verificación de perfil
                        nombre_verificado, perfil_verificado = verificar_nombre_con_ocr(name, screenshot_path, config, max_intentos=3)
                        
                        if not nombre_verificado:
                            print("⚠️ OCR no pudo verificar el nombre. Continuando...")
                            # No hacer refresh, continuar con el scraping
                        
                        break
                    else:
                        cerrar_ventanas_emergentes(driver)
                        time.sleep(1)
                else:
                    cerrar_ventanas_emergentes(driver)
                    time.sleep(1)

            # Extraer URLs de imágenes
            urls_encontradas = set()
            scrolls_sin_cambios = 0
            MAX_SCROLLS_SIN_CAMBIOS = config['scraping']['max_scrolls_sin_cambios']

            while scrolls_sin_cambios < MAX_SCROLLS_SIN_CAMBIOS:
                try:
                    nuevas = extraer_urls(driver)
                    nuevas_en_esta_iteracion = nuevas - urls_encontradas

                    if nuevas_en_esta_iteracion:
                        urls_encontradas.update(nuevas_en_esta_iteracion)
                        scrolls_sin_cambios = 0
                    else:
                        scrolls_sin_cambios += 1

                    time.sleep(0.2)
                    driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.SPACE)
                    time.sleep(random.uniform(0.1, 0.4))
                    
                except Exception as e:
                    print(f"⚠️ Error durante el scroll: {str(e)}")
                    break

            images_urls = list(urls_encontradas)

            # Abrir secciones adicionales
            try:
                button = driver.find_element(By.XPATH, "//div[contains(@class, 'focus-button-style') and @role='button']")
                button.click()
                time.sleep(0.2)
            except:
                print("No se encontró el botón de estilos de vida")

            try:
                second_button = driver.find_element(By.XPATH, "//div[contains(@class, 'Px(16px)')]")
                second_button.click()
                time.sleep(0.2)
            except:
                print("No se encontró el botón sobre mí")

            # Extraer datos del perfil usando las categorías del config
            categories = config['categories']
            extracted_texts = []
            otros = []

            try:
                extracted_terms = driver.find_elements(By.XPATH, "//div[contains(@class, 'Typs(body-1-regular)')]")
                extracted_texts = [term.text.strip() for term in extracted_terms if term.text.strip()]
            except:
                otros = []

            classified_data = {category: [] for category in ['horoscopo', 'educacion', 'hijos', 'vacunacion', 'personalidad', 'comunicacion', 'amor']}

            for text in extracted_texts:
                found = False
                for category in ['horoscopo', 'educacion', 'hijos', 'vacunacion', 'personalidad', 'comunicacion', 'amor']:
                    if text in categories[category]:
                        classified_data[category].append(text)
                        found = True
                        break
                if not found:
                    otros.append(text)
            
            # Convertir listas vacías a "NA"
            for key in ['horoscopo', 'educacion', 'hijos', 'vacunacion', 'personalidad', 'comunicacion', 'amor']:
                if not classified_data[key]:
                    classified_data[key] = "NA"

            # Extraer campos específicos
            # Altura
            try:
                height_element = driver.find_element(By.XPATH, "//div[contains(@class, 'Typs(body-1-regular)') and contains(@class, 'C($c-ds-text-primary)') and contains(text(), 'cm')]")
                height_text = height_element.text.strip()
                height_parts = height_text.split()
                
                if len(height_parts) == 2 and height_parts[0].isdigit() and height_parts[1] == "cm":
                    height = f"{height_parts[0]} cm"
                else:
                    height = "NA"
            except:
                height = "NA"

            # Distancia
            try:
                distance = driver.find_element(By.XPATH, "//div[contains(@class, 'Typs(body-1-regular)') and contains(@class, 'C($c-ds-text-primary)') and contains(text(), 'kilómetros')]").text
            except:
                distance = "NA"

            # Bio
            try:
                bio = driver.find_element(By.XPATH, "//h2[contains(text(), 'Acerca de mí')]/following::div[contains(@class, 'Typs(body-1-regular)')][1]").text.strip()
            except:
                bio = "NA"

            # Busco
            try:
                busco_section = driver.find_element(By.XPATH, "//h2[contains(text(), 'Busco')]")
                parent_div = busco_section.find_element(By.XPATH, "./../../..")
                busco_text = parent_div.find_element(By.XPATH, ".//span[contains(@class, 'Typs(display-3-strong)')]").text.strip()
            except:
                busco_text = "NA"

            # Idiomas
            try:
                languages = driver.find_element(By.XPATH, "//div[contains(text(), 'Inglés') or contains(text(), 'Español')]").text.strip()
            except:
                languages = "NA"
            
            # Mascotas
            try:
                pets_section = driver.find_element(By.XPATH, "//h3[contains(text(), 'Mascotas')]/following-sibling::div//div[contains(@class, 'Typs(body-1-regular)')]")
                pets_text = pets_section.text.strip()
            except:
                pets_text = "NA"

            # Otros campos (beber, fumar, deporte, etc.)
            additional_fields = {
                'drinking_text': "//h3[contains(text(), 'Beber')]/following-sibling::div//div[contains(@class, 'Typs(body-1-regular)')]",
                'smoking_text': "//h3[contains(text(), '¿Con qué frecuencia fumas?')]/following-sibling::div//div[contains(@class, 'Typs(body-1-regular)')]",
                'exercise_text': "//h3[contains(text(), '¿Haces deporte?')]/following-sibling::div//div[contains(@class, 'Typs(body-1-regular)')]",
                'sleep_text': "//h3[contains(text(), 'Hábitos de sueño')]/following-sibling::div//div[contains(@class, 'Typs(body-1-regular)')]",
                'social_text': "//h3[contains(text(), 'Redes sociales')]/following-sibling::div//div[contains(@class, 'Typs(body-1-regular)')]",
                'food_text': "//h3[contains(text(), 'Preferencias alimentarias')]/following-sibling::div//div[contains(@class, 'Typs(body-1-regular)')]"
            }

            extracted_additional = {}
            for field, xpath in additional_fields.items():
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    extracted_additional[field] = element.text.strip()
                except:
                    extracted_additional[field] = "NA"

            # Orientación sexual
            try:
                orientation_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'Typs(body-1-regular)')]")
                orientation_texts = []
                for el in orientation_elements:
                    texto = el.text.strip()
                    for opcion in categories['orientation_options']:
                        if opcion in texto and opcion not in orientation_texts:
                            orientation_texts.append(opcion)
                orientation_text = " | ".join(orientation_texts) if orientation_texts else "NA"
            except:
                orientation_text = "NA"

            # Género
            try:
                gender_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'Typs(body-1-regular)')]")
                gender_texts = []
                for el in gender_elements:
                    texto = el.text.strip()
                    for opcion in categories['gender_options']:
                        if opcion in texto and opcion not in gender_texts:
                            gender_texts.append(opcion)
                gender_text = " | ".join(gender_texts) if gender_texts else "NA"
            except:
                gender_text = "NA"

            # Tipo de relación
            try:
                terms_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'Bdrs(30px)') and contains(@class, 'W(maxc)') and contains(@class, 'Typs(body-1-regular)') and contains(@class, 'Bgc($c-ds-background-passions-sparks-inactive)')]")
                if not terms_elements:
                    terms_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'background-passions-sparks-inactive')]")
                if not terms_elements:
                    terms_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'Bdrs(30px)') and contains(@class, 'Typs(body-1-regular)')]")

                extracted_terms = [el.text.strip() for el in terms_elements if el.text.strip()]
                relationship_types = [term for term in extracted_terms if term in categories['relationship_terms']]
                relationship_types = " | ".join(relationship_types) if relationship_types else "NA"
            except:
                relationship_types = "NA"

            # Ubicación
            try:
                location = driver.find_element(By.XPATH, "//div[contains(@class, 'Typs(body-1-regular)') and contains(@class, 'C($c-ds-text-primary)') and contains(text(), 'Vive en')]").text.strip()
            except:
                location = "NA"

            # Intereses
            try:
                interests_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'Typs(body-1-regular)') and contains(@class, 'C($c-ds-text-passions-shared)')]")
                interests = [elem.text for elem in interests_elements]
            except:
                interests = []

            # Campos adicionales de personalidad
            personality_fields = {
                'salir_text': "//h3[contains(text(), 'Cuando salgo me verás')]/following::div[contains(@class, 'Mstart')][1]",
                'me_gusta_text': "//h3[contains(text(), 'Me gusta')]/following::div[contains(@class, 'Mstart')][1]",
                'puntualidad_text': "//h3[contains(text(), 'Suelo llegar')]/following::div[contains(@class, 'Mstart')][1]",
                'bombas_text': "//h3[contains(text(), 'Mis bombas de humo son')]/following::div[contains(@class, 'Mstart')][1]",
                'respuesta_text': "//h3[contains(text(), 'Contesto los mensajes')]/following::div[contains(@class, 'Mstart')][1]",
                'preferencia_text': "//h3[contains(text(), 'Prefiero recibir')]/following::div[contains(@class, 'Mstart')][1]",
                'bateria_text': "//h3[contains(text(), 'La batería de mi móvil')]/following::div[contains(@class, 'Mstart')][1]",
                'findes_text': "//h3[contains(text(), 'Los findes son para')]/following::div[contains(@class, 'Mstart')][1]",
                'sabado_text': "//h3[contains(text(), 'Mi sábado noche típico')]/following::div[contains(@class, 'Mstart')][1]",
                'domingos_text': "//h3[contains(text(), 'Mis domingos')]/following::div[contains(@class, 'Mstart')][1]"
            }

            extracted_personality = {}
            for field, xpath in personality_fields.items():
                try:
                    element = driver.find_element(By.XPATH, xpath)
                    extracted_personality[field] = element.text.strip()
                except:
                    extracted_personality[field] = "NA"

            # Canción favorita
            try:
                culto_section = driver.find_element(By.XPATH, "//h2[contains(text(), 'Mi canción de culto')]/ancestor::section")
                spans = culto_section.find_elements(By.XPATH, ".//span[contains(@class, 'Va(m)')]")
                if len(spans) >= 2:
                    artista = spans[0].text.strip()
                    cancion = spans[1].text.strip()
                else:
                    artista = "NA"
                    cancion = "NA"
            except:
                artista = "NA"
                cancion = "NA"

            # Limpiar otros datos ya incluidos
            contenido_ya_recogido = set()
            for valores in classified_data.values():
                if isinstance(valores, list):
                    contenido_ya_recogido.update(valores)

            for valor in [height, distance, bio, busco_text, languages, pets_text] + list(extracted_additional.values()) + [orientation_text, gender_text, relationship_types, location]:
                if valor != "NA":
                    if isinstance(valor, str):
                        contenido_ya_recogido.add(valor)

            contenido_ya_recogido.update(interests)
            otros = [item for item in otros if item not in contenido_ya_recogido]

            # Crear el perfil completo
            profile_data = {
                "id": profile_id if 'profile_id' in locals() else f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "nombre": name,
                "edad": age,
                "verificado": perfil_verificado if 'perfil_verificado' in locals() else "NA",
                "busco": busco_text,
                "bio": bio,
                **classified_data,
                "altura": height,
                "distancia": distance,
                "idiomas": languages,
                "mascotas": pets_text,
                "beber": extracted_additional.get('drinking_text', 'NA'),
                "fumar": extracted_additional.get('smoking_text', 'NA'),
                "deporte": extracted_additional.get('exercise_text', 'NA'),
                "sueño": extracted_additional.get('sleep_text', 'NA'),
                "redes_sociales": extracted_additional.get('social_text', 'NA'),
                "alimentacion": extracted_additional.get('food_text', 'NA'),
                "orientacion_sexual": orientation_text,
                "genero": gender_text,
                "relacion_tipo": relationship_types,
                "ubicacion": location,
                "intereses": interests,
                "salir": extracted_personality.get('salir_text', 'NA'),
                "me_gusta": extracted_personality.get('me_gusta_text', 'NA'),
                "puntualidad": extracted_personality.get('puntualidad_text', 'NA'),
                "bombas_humo": extracted_personality.get('bombas_text', 'NA'),
                "respuesta": extracted_personality.get('respuesta_text', 'NA'),
                "preferencia": extracted_personality.get('preferencia_text', 'NA'),
                "bateria": extracted_personality.get('bateria_text', 'NA'),
                "findes": extracted_personality.get('findes_text', 'NA'),
                "sabado": extracted_personality.get('sabado_text', 'NA'),
                "domingos": extracted_personality.get('domingos_text', 'NA'),
                "cancion": cancion,
                "artista": artista,
                "otros": otros,
                "imagenes": images_urls
            }

            return profile_data

        except Exception as e:
            print(f"⚠️ Error en intento {attempt + 1}/{MAX_RETRIES}: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                print("❌ No se pudo extraer el perfil después de varios intentos")
                return None
            time.sleep(1)

    return None


def main():
    """Función principal del scraper"""
    parser = argparse.ArgumentParser(description='Simple Tinder Scraper ES - Versión Simplificada')
    parser.add_argument('--config', '-c', default='config_simple.json', help='Archivo de configuración')
    parser.add_argument('--profiles', '-p', type=int, help='Número de perfiles a extraer')
    parser.add_argument('--like-rate', '-l', type=float, help='Probabilidad de dar like (0.0-1.0)')
    
    args = parser.parse_args()
    
    # Cargar configuración
    config = load_config(args.config)
    if not config:
        return
    
    # Sobrescribir configuración con argumentos de línea de comandos
    if args.profiles:
        config['scraping']['num_profiles'] = args.profiles
    if args.like_rate:
        config['scraping']['like_probability'] = args.like_rate

    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                      🔍 SIMPLE TINDER SCRAPER ES 🔍                        ║")
    print("║                                                                              ║")
    print("║                  Herramienta Simple de Extracción de Perfiles               ║")
    print("║                           Solo para Fines de Investigación                  ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()
    print("⚠️  AVISO LEGAL:")
    print("   • Esta herramienta está destinada únicamente para investigación académica")
    print("   • Respeta los Términos de Servicio de Tinder y la privacidad de los usuarios")
    print("   • Eres responsable del uso ético y legal")
    print("   • Considera las regulaciones de protección de datos en tu jurisdicción")
    print()

    print("📋 RESUMEN DE CONFIGURACIÓN:")
    print("--" * 25)
    print(f"🎯 Perfiles a extraer: {config['scraping']['num_profiles']}")
    print(f"💚 Probabilidad de like: {config['scraping']['like_probability']*100}%")
    print(f"💾 Intervalo de guardado: {config['scraping']['save_interval']} perfiles")
    print(f"📁 Archivo de salida: {config['output']['filename']}")
    print(f"📸 Guardar capturas: {'Sí' if config['output']['save_screenshots'] else 'No'}")
    print("--" * 25)
    print()

    print("🚨 RECORDATORIOS IMPORTANTES:")
    print("   • Asegúrate de haber iniciado sesión en Tinder en tu navegador")
    print("   • Cierra otras instancias de Chrome/Chromium")
    print("   • Este proceso puede tomar tiempo dependiendo del número de perfiles")
    print("   • Puedes parar en cualquier momento con Ctrl+C")
    print()

    response = input("🤔 ¿Listo para comenzar la extracción? (s/N): ")
    if response.lower() != 's':
        print("👋 Operación cancelada.")
        return

    # Crear directorios necesarios
    os.makedirs(config['output']['screenshots_directory'], exist_ok=True)
    os.makedirs(config['output']['template_directory'], exist_ok=True)
    os.makedirs(config['output']['output_directory'], exist_ok=True)

    print("🚀 Inicializando scraper...")
    
    # Configurar driver
    driver = setup_driver()
    
    # Navegar a Tinder
    driver.get("https://tinder.com/")
    time.sleep(10)

    input("\U0001f511 Inicia sesión en Tinder manualmente y presiona ENTER para continuar... ")
    print("✅ Listo para hacer scraping.")

    # Variables para tracking
    last_profile_time = time.time()
    num_profiles = config['scraping']['num_profiles']
    profiles = []
    stats = ScrapingStats()
    last_save = 0

    try:
        for i in range(1, num_profiles + 1):
            # Verificar timeout
            current_time = time.time()
            if current_time - last_profile_time > 60:  # 60 segundos = 1 minuto
                print("⚠️ Ha pasado más de un minuto sin agregar un perfil. Navegando a la página de recomendaciones...")
                driver.get("https://tinder.com/app/recs")
                time.sleep(10)
                last_profile_time = time.time()
                continue
                
            profile = scrape_profile(driver, config)
            
            # Verificar si el perfil tiene imágenes
            if profile:
                # Comprobar si la lista de imágenes está vacía o es NA
                if not profile.get("imagenes") or profile.get("imagenes") == "NA" or len(profile.get("imagenes", [])) == 0:
                    print("⚠️ Perfil sin imágenes detectado. Navegando a la página de recomendaciones...")
                    driver.get("https://tinder.com/app/recs")
                    time.sleep(10)
                    continue
                
                # Si tiene imágenes, lo agregamos a la lista
                profiles.append(profile)
                print(f"✅ Perfil de '{profile['nombre']}' guardado con {len(profile['imagenes'])} imágenes")
                
                # Actualizar el tiempo del último perfil agregado
                last_profile_time = time.time()
                
            # Acción de like/nope
            action = Keys.ARROW_LEFT if random.random() > config['scraping']['like_probability'] else Keys.ARROW_RIGHT
            try:
                driver.find_element(By.TAG_NAME, "body").send_keys(action)
                stats.add_action(action)
                stats.print_stats()
            except Exception as e:
                print(f"Error al deslizar en el intento {i}: {str(e)}")
                
            # Guardar cada intervalo configurado
            if len(profiles) - last_save >= config['scraping']['save_interval']:
                save_profiles(profiles[last_save:], config)
                last_save = len(profiles)
                
            time.sleep(random.uniform(0.2, 0.4))

    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante el scraping: {str(e)}")
    finally:
        # Guardar los perfiles restantes antes de cerrar
        if profiles[last_save:]:
            save_profiles(profiles[last_save:], config)
        
        print(f"\n✅ Scraping finalizado. Total de perfiles extraídos: {len(profiles)}")
        print(f"📁 Perfiles guardados en: {config['output']['filename']}")
        driver.quit()


if __name__ == "__main__":
    main()
