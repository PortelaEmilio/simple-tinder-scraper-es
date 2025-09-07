#!/bin/bash

# Tinder Scraper Setup Script
# This script sets up the environment for the Tinder Scraper

set -e

echo "🔍 Tinder Scraper Setup"
echo "======================="

# Check if Python 3.8+ is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        echo "✅ Python $PYTHON_VERSION found"
        
        # Check if version is 3.8 or higher
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
            echo "✅ Python version is compatible"
        else
            echo "❌ Python 3.8 or higher is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        echo "❌ Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if Tesseract is installed
check_tesseract() {
    if command -v tesseract &> /dev/null; then
        TESSERACT_VERSION=$(tesseract --version | head -n1)
        echo "✅ $TESSERACT_VERSION found"
    else
        echo "⚠️  Tesseract OCR not found."
        echo "   Please install Tesseract:"
        echo "   - Ubuntu/Debian: sudo apt update && sudo apt install tesseract-ocr"
        echo "   - macOS: brew install tesseract"
        echo "   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
        
        read -p "   Continue without Tesseract? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check if Chrome/Chromium is installed
check_chrome() {
    if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null; then
        echo "✅ Chrome/Chromium browser found"
    else
        echo "⚠️  Chrome/Chromium browser not found."
        echo "   Please install Google Chrome or Chromium browser."
        
        read -p "   Continue without Chrome? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Create virtual environment
setup_venv() {
    echo "📦 Setting up Python virtual environment..."
    
    if [ -d "venv" ]; then
        echo "   Virtual environment already exists."
        read -p "   Recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            python3 -m venv venv
        fi
    else
        python3 -m venv venv
    fi
    
    echo "✅ Virtual environment ready"
}

# Install Python dependencies
install_dependencies() {
    echo "📥 Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install dependencies
    pip install -r requirements.txt
    
    echo "✅ Dependencies installed successfully"
}

# Create necessary directories
setup_directories() {
    echo "📁 Creating necessary directories..."
    
    mkdir -p output
    mkdir -p screenshots
    mkdir -p templates
    
    echo "✅ Directories created"
}

# Copy template file if available
setup_templates() {
    echo "🖼️  Setting up templates..."
    
    # Check if there's a tick icon in the parent directory
    if [ -f "../template/tick_icon.png" ]; then
        cp "../template/tick_icon.png" "templates/"
        echo "✅ Verification template copied"
    else
        echo "⚠️  Verification template not found."
        echo "   Please add a Tinder verification icon image to:"
        echo "   templates/tick_icon.png"
    fi
}

# Validate installation
validate_installation() {
    echo "🔍 Validating installation..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run validation
    if python main.py --validate-deps; then
        echo "✅ Installation validation successful"
    else
        echo "❌ Installation validation failed"
        exit 1
    fi
}

# Main setup process
main() {
    echo "Starting setup process..."
    echo
    
    check_python
    check_tesseract
    check_chrome
    setup_venv
    install_dependencies
    setup_directories
    setup_templates
    validate_installation
    
    echo
    echo "🎉 Setup completed successfully!"
    echo
    echo "📝 Next steps:"
    echo "   1. Activate the virtual environment: source venv/bin/activate"
    echo "   2. Add verification template: templates/tick_icon.png"
    echo "   3. Run the scraper: python main.py --help"
    echo
    echo "🚀 Quick start:"
    echo "   source venv/bin/activate"
    echo "   python main.py --profiles 10"
    echo
}

# Run main function
main