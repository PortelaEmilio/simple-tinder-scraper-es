#!/usr/bin/env python3
"""
Simple Tinder Scraper ES
Main entry point for the application.

Usage:
    python main.py [options]

For help:
    python main.py --help
"""

import argparse
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import (
    TinderScraper, 
    ConfigManager, 
    setup_logging, 
    validate_dependencies
)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Simple Tinder Scraper ES - Extrae perfiles de Tinder para investigación",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py                                    # Ejecutar con configuración por defecto
  python main.py --profiles 50                     # Extraer 50 perfiles
  python main.py --config config/custom.json       # Usar configuración personalizada
  python main.py --output mis_perfiles.json        # Archivo de salida personalizado
  python main.py --like-rate 0.2 --profiles 100    # 20% de likes, 100 perfiles
  python main.py --log-level DEBUG                 # Habilitar logging de debug

⚠️  IMPORTANTE: Esta herramienta es solo para fines de investigación.
   Por favor, respeta los términos de servicio de Tinder y la privacidad de los usuarios.
        """
    )
    
    # Configuration options
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Ruta al archivo de configuración (por defecto: config/default_config.json)"
    )
    
    # Scraping options
    parser.add_argument(
        "--profiles", "-p",
        type=int,
        help="Número de perfiles a extraer (sobrescribe configuración)"
    )
    
    parser.add_argument(
        "--like-rate", "-l",
        type=float,
        help="Probabilidad de dar like a un perfil (0.0-1.0, sobrescribe configuración)"
    )
    
    parser.add_argument(
        "--save-interval", "-s",
        type=int,
        help="Guardar perfiles cada N perfiles (sobrescribe configuración)"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Nombre del archivo de salida (sobrescribe configuración)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directorio de salida (sobrescribe configuración)"
    )
    
    # Browser options
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Ejecutar navegador en modo sin interfaz gráfica"
    )
    
    parser.add_argument(
        "--no-screenshots",
        action="store_true",
        help="Deshabilitar guardado de capturas de pantalla"
    )
    
    # Logging options
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Establecer nivel de logging (por defecto: INFO)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suprimir salida (solo nivel ERROR)"
    )
    
    # Utility options
    parser.add_argument(
        "--validate-deps",
        action="store_true",
        help="Validar dependencias y salir"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Simple Tinder Scraper ES v1.0.0"
    )
    
    return parser.parse_args()

def apply_cli_overrides(config_manager, args):
    """Apply command line argument overrides to configuration."""
    
    # Scraping overrides
    if args.profiles is not None:
        if args.profiles <= 0:
            print("❌ Error: El número de perfiles debe ser positivo")
            sys.exit(1)
        config_manager.update("scraping.num_profiles", args.profiles)
    
    if args.like_rate is not None:
        if not 0.0 <= args.like_rate <= 1.0:
            print("❌ Error: La tasa de likes debe estar entre 0.0 y 1.0")
            sys.exit(1)
        config_manager.update("scraping.like_probability", args.like_rate)
    
    if args.save_interval is not None:
        if args.save_interval <= 0:
            print("❌ Error: El intervalo de guardado debe ser positivo")
            sys.exit(1)
        config_manager.update("scraping.save_interval", args.save_interval)
    
    # Output overrides
    if args.output:
        config_manager.update("output.filename", args.output)
    
    if args.output_dir:
        config_manager.update("output.output_directory", args.output_dir)
    
    # Browser overrides
    if args.headless:
        config_manager.update("browser.headless", True)
    
    if args.no_screenshots:
        config_manager.update("output.save_screenshots", False)

def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                      🔍 SIMPLE TINDER SCRAPER ES 🔍                        ║
║                                                                              ║
║                  Herramienta Simple de Extracción de Perfiles               ║
║                           Solo para Fines de Investigación                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

⚠️  AVISO LEGAL:
   • Esta herramienta está destinada únicamente para investigación académica
   • Respeta los Términos de Servicio de Tinder y la privacidad de los usuarios
   • Eres responsable del uso ético y legal
   • Considera las regulaciones de protección de datos en tu jurisdicción

"""
    print(banner)

def print_configuration_summary(config_manager):
    """Print a summary of the current configuration."""
    config = config_manager.get_full_config()
    
    print("📋 RESUMEN DE CONFIGURACIÓN:")
    print("-" * 50)
    print(f"🎯 Perfiles a extraer: {config['scraping']['num_profiles']}")
    print(f"💚 Probabilidad de like: {config['scraping']['like_probability']:.1%}")
    print(f"💾 Intervalo de guardado: {config['scraping']['save_interval']} perfiles")
    print(f"📁 Archivo de salida: {config['output']['output_directory']}/{config['output']['filename']}")
    print(f"📸 Guardar capturas: {'Sí' if config['output']['save_screenshots'] else 'No'}")
    print(f"🌐 Modo sin interfaz: {'Sí' if config['browser']['headless'] else 'No'}")
    print("-" * 50)

def main():
    """Main entry point."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Setup logging
        log_level = "ERROR" if args.quiet else args.log_level
        setup_logging(log_level)
        
        # Validate dependencies if requested
        if args.validate_deps:
            print("🔍 Validando dependencias...")
            if validate_dependencies():
                print("✅ Todas las dependencias están disponibles")
                sys.exit(0)
            else:
                print("❌ Faltan algunas dependencias")
                sys.exit(1)
        
        # Print banner
        if not args.quiet:
            print_banner()
        
        # Validate dependencies
        if not validate_dependencies():
            print("❌ Por favor, instala las dependencias faltantes antes de continuar.")
            sys.exit(1)
        
        # Load configuration
        config_manager = ConfigManager(args.config)
        
        # Apply command line overrides
        apply_cli_overrides(config_manager, args)
        
        # Print configuration summary
        if not args.quiet:
            print_configuration_summary(config_manager)
        
        # Confirm before starting
        if not args.quiet:
            print("\n🚨 RECORDATORIOS IMPORTANTES:")
            print("   • Asegúrate de haber iniciado sesión en Tinder en tu navegador")
            print("   • Cierra otras instancias de Chrome/Chromium")
            print("   • Este proceso puede tomar tiempo dependiendo del número de perfiles")
            print("   • Puedes parar en cualquier momento con Ctrl+C")
            
            confirm = input("\n🤔 ¿Listo para comenzar la extracción? (s/N): ").strip().lower()
            if confirm != 's' and confirm != 'sí' and confirm != 'si':
                print("Operación cancelada.")
                sys.exit(0)
        
        # Initialize and run scraper
        print("\n🚀 Inicializando scraper...")
        scraper = TinderScraper(config_manager.get_full_config())
        
        try:
            # Setup
            if not scraper.setup():
                print("❌ Error al configurar el scraper")
                sys.exit(1)
            
            # Run scraping
            results = scraper.run()
            
            # Print results
            if not args.quiet:
                print(f"\n🎉 ¡Extracción completada!")
                print(f"📊 Perfiles extraídos: {results['profiles_extracted_this_session']}")
                print(f"📁 Total de perfiles en archivo: {results['total_profiles_in_file']}")
                print(f"⚡ Tasa de éxito: {results['success_rate']:.1f}%")
        
        finally:
            # Cleanup
            scraper.cleanup()
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrumpido por el usuario. Limpiando...")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()