# 🚀 Guía de Inicio Rápido

## Instalación Rápida

1. **Ejecutar el script de instalación:**
```bash
./setup.sh
```

2. **Activar el entorno virtual:**
```bash
source venv/bin/activate
```

3. **Ejecutar el scraper:**
```bash
python main.py --profiles 10
```

## Comandos Más Utilizados

### Scraping Básico
```bash
# Scraping de 10 perfiles (configuración por defecto)
python main.py

# Scraping de 50 perfiles
python main.py --profiles 50

# Scraping con 20% de probabilidad de like
python main.py --profiles 30 --like-rate 0.2
```

### Configuración Avanzada
```bash
# Usar configuración personalizada
python main.py --config config/example_custom_config.json

# Modo silencioso (sin output)
python main.py --quiet --profiles 20

# Modo debug
python main.py --log-level DEBUG --profiles 5
```

### Opciones de Output
```bash
# Archivo de salida personalizado
python main.py --output mi_research.json --profiles 25

# Directorio de salida personalizado
python main.py --output-dir resultados/

# Sin capturas de pantalla
python main.py --no-screenshots --profiles 15
```

## Pasos de Configuración Manual

### 1. Verificar Dependencias
```bash
python main.py --validate-deps
```

### 2. Agregar Plantilla de Verificación
- Captura una imagen del icono de verificación de Tinder (tick azul)
- Guárdala como `templates/tick_icon.png`

### 3. Configurar el Navegador
- Cierra todas las instancias de Chrome/Chromium
- Asegúrate de estar logueado en Tinder en el navegador

## Solución de Problemas Comunes

### Error: "ChromeDriver not found"
```bash
pip uninstall webdriver-manager
pip install webdriver-manager
```

### Error: "Tesseract not found"
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr

# macOS
brew install tesseract
```

### Error: "No profiles extracted"
- Verifica que estés logueado en Tinder
- Asegúrate de que la página esté completamente cargada
- Intenta reducir la velocidad aumentando los delays en la configuración

## Configuración Personalizada

### Crear Configuración Personalizada
```bash
cp config/example_custom_config.json config/mi_config.json
# Editar mi_config.json según tus necesidades
python main.py --config config/mi_config.json
```

### Parámetros Importantes
- `num_profiles`: Número de perfiles a extraer
- `like_probability`: Probabilidad de dar like (0.0-1.0)
- `save_interval`: Guardar cada N perfiles
- `timeout_minutes`: Tiempo máximo sin nuevos perfiles antes de recargar

## Mejores Prácticas

1. **Empezar Pequeño**: Prueba con 5-10 perfiles primero
2. **Configurar Delays**: Aumenta los delays si encuentras problemas
3. **Backups**: Los perfiles se guardan automáticamente cada N profiles
4. **Verificación**: Siempre verifica que la plantilla de verificación esté en su lugar
5. **Monitoreo**: Usa `--log-level DEBUG` para ver más detalles durante la ejecución

## Estructura de Datos de Salida

```json
{
  "id": "Ana_20241207_143022",
  "nombre": "Ana",
  "edad": "25",
  "verificado": "Yes",
  "bio": "Me gusta viajar y la fotografía",
  "altura": "165 cm",
  "distancia": "5 km",
  "intereses": ["Viajes", "Fotografía", "Música"],
  "imagenes": ["https://...", "https://..."],
  "ubicacion": "Madrid, España"
}
```

## Consideraciones Éticas

- ✅ Usa solo para investigación académica
- ✅ Respeta la privacidad de los usuarios
- ✅ Cumple con las leyes locales de protección de datos
- ✅ Sigue los términos de servicio de Tinder
- ❌ No uses para spam o acoso
- ❌ No redistribuyas datos personales