# Simple Tinder Scraper ES

🔍 Herramienta simple para extraer perfiles de Tinder con fines de investigación académica.

## ✅ Estado: COMPLETAMENTE FUNCIONAL

- ✅ **Scraper operativo** - `scraper_simple.py` funcionando al 100%
- ✅ **Verificación configurada** - Detección automática de perfiles verificados
- ✅ **OCR integrado** - Verificación de nombres con Tesseract
- ✅ **Configuración simple** - Un solo archivo JSON

## ⚠️ Aviso Legal

Esta herramienta está destinada únicamente para fines de investigación académica y educativos. El uso debe cumplir con:
- Los términos de servicio de Tinder
- Las leyes locales de privacidad y protección de datos
- Los principios éticos de investigación

## 🚀 Uso Rápido

### Instalación
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Las dependencias ya están instaladas
```

### Comandos Básicos
```bash
# Modo básico (10 perfiles)
./venv/bin/python scraper_simple.py

# Extraer 5 perfiles
./venv/bin/python scraper_simple.py --profiles 5

# Personalizar probabilidad de likes
./venv/bin/python scraper_simple.py --profiles 3 --like-rate 0.2

# Ver ayuda
./venv/bin/python scraper_simple.py --help
```

## ⚙️ Configuración

Edita `config_simple.json` para personalizar:

```json
{
    "num_profiles": 10,
    "like_probability": 0.151,
    "output_file": "val_HbM.json",
    "save_screenshots": true,
    "template_path": "template/tick_icon.png"
}
```

## 📊 Datos Extraídos

- **Información básica**: Nombre, edad, verificación, bio
- **Detalles**: Altura, distancia, ubicación, idiomas
- **Preferencias**: Orientación, género, tipo de relación
- **Estilo de vida**: Educación, trabajo, mascotas, hábitos
- **Personalidad**: Horóscopo, MBTI, intereses
- **Multimedia**: URLs de imágenes, canción favorita

## 📁 Estructura

```
├── scraper_simple.py      # Archivo principal
├── config_simple.json     # Configuración
├── requirements.txt       # Dependencias Python
├── template/             # Iconos para verificación
├── screenshots/          # Capturas temporales (se limpian automáticamente)
├── output/              # Archivos JSON de salida
└── venv/               # Entorno virtual Python
```

## 🔧 Requisitos

- Python 3.8+
- Chrome/Chromium browser
- Tesseract OCR instalado

### Instalación de Tesseract
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
```

## 📋 Antes de Usar

1. **Inicia sesión en Tinder** manualmente en Chrome
2. **Acepta cookies** y permisos necesarios
3. **Cierra popups** si los hay
4. **Opcional**: Añade `template/tick_icon.png` para detectar verificaciones

## 🎯 Tareas de VS Code

- `Run Simple Scraper (Basic)`: Ejecuta con configuración por defecto
- `Run Simple Scraper (5 profiles)`: Extrae 5 perfiles
- `Run Simple Scraper (10 profiles)`: Extrae 10 perfiles
- `Help - Simple Scraper`: Muestra ayuda

## 📄 Salida

Los perfiles se guardan en `val_HbM.json` con estructura:

```json
{
  "id": "nombre_20241207_143022",
  "nombre": "Ana",
  "edad": "25",
  "verificado": "Yes",
  "bio": "Estudiante de medicina...",
  "altura": "165 cm",
  "distancia": "5 km",
  "intereses": ["Música", "Viajes"],
  "imagenes": ["https://..."]
}
```

## ⚖️ Consideraciones Éticas

- Respeta la privacidad de los usuarios
- No uses los datos para hostigamiento
- Cumple con regulaciones locales
- Uso únicamente para investigación legítimaer Scraper ES

**El usuario es responsable del uso ético y legal de esta herramienta.**

## 🚀 Características

- ✅ Extracción automatizada de perfiles de Tinder
- 🖼️ Captura y análisis de screenshots con OCR
- ✅ Detección de perfiles verificados
- 📊 Estadísticas en tiempo real de scraping
- 💾 Guardado automático en formato JSON
- 🔧 Configuración flexible
- 🛡️ Manejo robusto de errores

## 📋 Requisitos del Sistema

- Python 3.8 o superior
- Google Chrome instalado
- Tesseract OCR instalado

### Instalación de Tesseract

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Descarga e instala desde: https://github.com/UB-Mannheim/tesseract/wiki

## 🛠️ Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/PortelaEmilio/simple-tinder-scraper-es.git
cd simple-tinder-scraper-es
```

2. **Ejecutar script de instalación automatizada:**
```bash
chmod +x setup.sh
./setup.sh
```

O manualmente:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configurar plantillas de verificación:**
```bash
# Copiar una imagen del icono de verificación de Tinder a:
cp tu_imagen_tick.png templates/tick_icon.png
```

## 🎯 Uso Rápido

### Modo Básico
```bash
python main.py
```

### Modo Avanzado con Configuración
```bash
python main.py --profiles 50 --like-rate 0.2 --headless
```

### Todas las Opciones Disponibles
```bash
python main.py --help
```

**Opciones principales:**
- `--profiles N`: Número de perfiles a extraer (por defecto: 10)
- `--like-rate 0.X`: Probabilidad de dar like (por defecto: 0.151)
- `--config archivo.json`: Archivo de configuración personalizado
- `--headless`: Ejecutar en modo sin interfaz gráfica
- `--log-level DEBUG`: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

## ⚙️ Configuración

El archivo `config/default_config.json` contiene todas las opciones configurables:

```json
{
  "scraping": {
    "num_profiles": 10,
    "like_probability": 0.151,
    "save_interval": 10,
    "max_retries": 3
  },
  "browser": {
    "headless": false,
    "window_size": "maximized",
    "disable_automation_flags": true
  },
  "ocr": {
    "max_attempts": 3,
    "verification_threshold": 0.75
  },
  "output": {
    "filename": "profiles.json",
    "save_screenshots": true,
    "clean_screenshots_after_verification": true
  }
}
```

## 📁 Estructura del Proyecto

```
simple-tinder-scraper-es/
├── src/                   # Código fuente modular
│   ├── __init__.py
│   ├── scraper.py          # Coordinación principal
│   ├── browser_manager.py  # Gestión robusta del navegador
│   ├── ocr_processor.py    # Procesamiento OCR optimizado
│   ├── data_extractor.py   # Extracción de datos de perfiles
│   ├── config_manager.py   # Sistema de configuración
│   └── utils.py           # Utilidades y estadísticas
├── config/
│   └── default_config.json # Configuración por defecto
├── templates/
│   └── tick_icon.png      # Plantilla del icono de verificación
├── output/                # Archivos JSON de salida
├── screenshots/           # Capturas temporales
├── main.py               # Punto de entrada CLI
├── setup.sh              # Script de instalación automatizada
├── requirements.txt      # Dependencias Python
└── README.md            # Esta documentación
```

## 📊 Formato de Salida

Los perfiles extraídos se guardan en formato JSON con la siguiente estructura:

```json
{
  "id": "nombre_20241207_143022",
  "nombre": "Ana",
  "edad": "25",
  "verificado": "Yes",
  "bio": "Estudiante de medicina, me encanta viajar...",
  "altura": "165 cm",
  "distancia": "5 km",
  "intereses": ["Música", "Viajes", "Fotografía"],
  "imagenes": ["https://tinder.com/...", "https://tinder.com/..."],
  "ubicacion": "Madrid, España"
}
```

## 🔧 Resolución de Problemas

### Error: "ChromeDriver not found"
El script intenta múltiples métodos de instalación automáticamente. Si falla:
```bash
./setup.sh  # Reinstalar dependencias
```

### Error: "Tesseract not found"
```bash
# Verificar instalación
tesseract --version

# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```

### Problema: Capturas de pantalla vacías
- Asegúrate de haber iniciado sesión en Tinder manualmente
- Verifica que no haya popups bloqueando la vista
- Aumenta los tiempos de espera en la configuración

### Error de permisos en Linux/macOS
```bash
chmod +x setup.sh
sudo chown -R $USER:$USER .
```

## 📚 Documentación Adicional

- **[QUICKSTART.md](QUICKSTART.md)** - Guía rápida de 5 minutos
- **[DEVELOPER.md](DEVELOPER.md)** - Guía para desarrolladores
- **[CHANGELOG.md](CHANGELOG.md)** - Historial de cambios
- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** - Resumen ejecutivo

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📬 Contacto

Para preguntas o sugerencias, puedes contactar a través de [GitHub Issues](https://github.com/PortelaEmilio/simple-tinder-scraper-es/issues).

---

**Nota:** Este proyecto no está afiliado con Tinder ni con Match Group.
