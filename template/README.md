# Plantilla de Verificación

✅ **¡CONFIGURADO!** La imagen de verificación ya está disponible.

## Estado Actual:
- ✅ `tick_icon.png` - Imagen del icono de verificación de Tinder (24x23 px)
- ✅ Formato PNG válido
- ✅ Compatible con OpenCV
- ✅ **El scraper puede detectar perfiles verificados**

## Cómo Funciona:
El scraper usa esta imagen como plantilla para detectar automáticamente si un perfil está verificado mediante:
1. **Template Matching**: Compara la imagen del perfil con esta plantilla
2. **Umbral de coincidencia**: 75% (configurable en config_simple.json)
3. **Resultado**: "Yes" si está verificado, "No" si no, "NA" si hay error

## Si Necesitas Cambiarla:
1. Toma una nueva captura del icono ✓ azul de Tinder
2. Recorta solo el icono (recomendado: ~20x20 píxeles)  
3. Guárdala como `tick_icon.png` reemplazando la actual
4. Asegúrate de que sea formato PNG
