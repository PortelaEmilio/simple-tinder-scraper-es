# 🛫 Developer Guide

## Arquitectura del Proyecto

### Estructura de Módulos

```
src/
├── __init__.py              # Package initialization
├── scraper.py              # Main scraper orchestration
├── browser_manager.py      # Browser setup and management
├── ocr_processor.py        # OCR and image processing
├── data_extractor.py       # Profile data extraction
├── config_manager.py       # Configuration management
└── utils.py               # Utilities and helper functions
```

### Flujo de Datos

```
main.py → ConfigManager → TinderScraper → BrowserManager
                                      ↓
OCRProcessor ← DataExtractor ← WebDriver Instance
     ↓              ↓
ProfileSaver ← Extracted Data
```

## Añadir Nuevas Funcionalidades

### 1. Agregar Nuevo Campo de Extracción

**Archivo**: `src/data_extractor.py`

```python
def _extract_additional_fields(self, details: Dict[str, Any]) -> None:
    """Extract additional profile fields."""
    
    # Añadir nuevo campo
    try:
        new_field_element = self.driver.find_element(By.XPATH, "//selector-for-new-field")
        details["nuevo_campo"] = new_field_element.text.strip()
    except:
        details["nuevo_campo"] = "NA"
```

### 2. Añadir Nueva Configuración

**Archivo**: `config/default_config.json`

```json
{
  "nueva_seccion": {
    "parametro1": "valor",
    "parametro2": 123
  }
}
```

**Archivo**: `src/config_manager.py`

```python
def _validate_config(self) -> None:
    """Validate configuration values."""
    required_sections = ["scraping", "browser", "ocr", "output", "nueva_seccion"]
    # ... rest of validation
```

### 3. Agregar Nuevo Procesador

```python
# src/nuevo_procesador.py
class NuevoProcesador:
    def __init__(self, config):
        self.config = config
    
    def procesar(self, data):
        # Lógica de procesamiento
        return processed_data
```

Luego integrar en `src/scraper.py`:

```python
from .nuevo_procesador import NuevoProcesador

class TinderScraper:
    def __init__(self, config):
        self.nuevo_procesador = NuevoProcesador(config)
```

## Debugging y Testing

### Logging

El sistema usa logging estándar de Python:

```python
import logging
logger = logging.getLogger(__name__)

# Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Ejecutar con Debug

```bash
python main.py --log-level DEBUG --profiles 1
```

### Test de Componentes Individuales

```python
# Test OCR processor
from src import OCRProcessor
ocr = OCRProcessor(config)
result = ocr.extract_text_from_image("test_image.png")

# Test browser manager
from src import BrowserManager
browser = BrowserManager(config)
driver = browser.setup_browser()
```

## Estructura de Datos

### Perfil Extraido

```json
{
  "id": "nombre_20241207_143022",
  "nombre": "Ana",
  "edad": "25",
  "verificado": "Yes",
  "imagenes": [
    "https://tinder.com/...",
    "https://tinder.com/..."
  ],
  "bio": "Estudiante de medicina...",
  "intereses": ["Viajar", "Cocinar"],
  "distancia": "5 km",
  "altura": "165 cm"
}
```

### Configuración

```json
{
  "scraping": {
    "num_profiles": 10,
    "like_probability": 0.151,
    "save_interval": 10
  },
  "browser": {
    "headless": false,
    "window_size": "maximized"
  },
  "ocr": {
    "verification_threshold": 0.75
  }
}
```

## Patrones de Desarrollo

### 1. Añadir Nuevo Selector

```python
# En data_extractor.py
def _extract_new_field(self) -> str:
    """Extract new field from profile."""
    selectors = [
        "//div[@class='new-field']",
        "//span[contains(text(), 'pattern')]",
        "//div[contains(@aria-label, 'label')]"
    ]
    
    for selector in selectors:
        try:
            element = self.driver.find_element(By.XPATH, selector)
            return element.text.strip()
        except:
            continue
    
    return "NA"
```

### 2. Añadir Validación

```python
# En config_manager.py
def _validate_new_config(self, value: Any) -> bool:
    """Validate new configuration value."""
    if not isinstance(value, expected_type):
        logger.warning(f"Invalid type for config: {value}")
        return False
    
    if not (min_val <= value <= max_val):
        logger.warning(f"Value out of range: {value}")
        return False
    
    return True
```

### 3. Añadir Manejo de Errores

```python
def new_operation(self):
    """Perform new operation with error handling."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # Operación principal
            result = self._perform_operation()
            return result
            
        except SpecificException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.error("All attempts failed")
                raise
            time.sleep(1)  # Wait before retry
```

## Testing y Validación

### Test Manual de Componentes

```bash
# Test configuración
python -c "from src import ConfigManager; cm = ConfigManager(); print(cm.get_full_config())"

# Test OCR (requiere imagen de prueba)
python -c "from src import OCRProcessor; ocr = OCRProcessor({}); print(ocr.check_tesseract_installation())"

# Test dependencias
python -c "from src.utils import validate_dependencies; print(validate_dependencies())"
```

### Validación de Salida

```python
import json

# Validar JSON de salida
with open('output/profiles.json', 'r') as f:
    profiles = json.load(f)
    
for profile in profiles:
    assert 'nombre' in profile
    assert 'edad' in profile
    assert isinstance(profile['imagenes'], list)
```

## Mejores Prácticas

### 1. Logging

```python
# Usar logging en lugar de print
logger.info("Starting operation")  # ✅ Correcto
print("Starting operation")        # ❌ Incorrecto
```

### 2. Manejo de Excepciones

```python
# Ser específico con excepciones
try:
    element = driver.find_element(By.XPATH, xpath)
except NoSuchElementException:  # ✅ Específico
    logger.warning("Element not found")
except Exception:  # ❌ Muy general
    pass
```

### 3. Configuración

```python
# Usar configuración centralizada
value = self.config.get("section.key", default_value)  # ✅ Correcto
value = hardcoded_value                                # ❌ Incorrecto
```

### 4. Validación de Datos

```python
# Validar datos antes de usar
if profile_data and profile_data.get('nombre'):
    process_profile(profile_data)  # ✅ Seguro
else:
    logger.warning("Invalid profile data")
```

## Extensiones Comunes

### 1. Añadir Nuevo Formato de Salida

```python
# En utils.py
class CSVProfileSaver(ProfileSaver):
    def save_profiles(self, profiles):
        import csv
        with open(self.filepath.replace('.json', '.csv'), 'w') as f:
            writer = csv.DictWriter(f, fieldnames=profiles[0].keys())
            writer.writeheader()
            writer.writerows(profiles)
```

### 2. Añadir Filtros de Perfil

```python
# En scraper.py
def _filter_profile(self, profile_data):
    """Apply filters to profile data."""
    age = int(profile_data.get('edad', 0))
    if age < 18 or age > 65:
        return False
    
    if len(profile_data.get('imagenes', [])) < 2:
        return False
    
    return True
```

### 3. Añadir Métricas Personalizadas

```python
# En utils.py
class AdvancedStats(ScrapingStats):
    def __init__(self):
        super().__init__()
        self.verified_profiles = 0
        self.profiles_with_bio = 0
    
    def add_verified_profile(self):
        self.verified_profiles += 1
    
    def get_verification_rate(self):
        if self.profiles_scraped > 0:
            return self.verified_profiles / self.profiles_scraped
        return 0.0
```

## Troubleshooting

### Problemas Comunes

1. **ChromeDriver no encontrado**
   ```bash
   # Reinstalar con script
   ./setup.sh
   ```

2. **Tesseract no instalado**
   ```bash
   # Ubuntu/Debian
   sudo apt install tesseract-ocr
   
   # macOS
   brew install tesseract
   ```

3. **Permisos de archivos**
   ```bash
   chmod +x setup.sh
   sudo chown -R $USER:$USER .
   ```

4. **Error de configuración**
   ```bash
   # Validar configuración
   python -c "from src import ConfigManager; ConfigManager()"
   ```

5. **Dependencias faltantes**
   ```bash
   pip install -r requirements.txt
   ```

## Contacto para Desarrolladores

Para contribuciones o preguntas técnicas:
- Crear issue en GitHub
- Seguir las guías de contribución
- Incluir logs y configuración en reportes de bugs