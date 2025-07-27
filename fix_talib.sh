#!/bin/bash

# TA-Lib Installation Fix Script
# This script provides alternative methods to install TA-Lib

echo "🔧 TA-Lib Installation Fix Script"
echo "=================================="

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Detected macOS"
    
    # Check if Homebrew is installed
    if command -v brew &> /dev/null; then
        echo "✅ Homebrew found"
        echo ""
        echo "📦 Installing TA-Lib via Homebrew..."
        brew install ta-lib
        
        if [ $? -eq 0 ]; then
            echo "✅ TA-Lib installed successfully via Homebrew"
            echo ""
            echo "🔧 Now install the Python wrapper:"
            echo "   pip install TA-Lib"
        else
            echo "❌ Failed to install TA-Lib via Homebrew"
        fi
    else
        echo "❌ Homebrew not found"
        echo ""
        echo "📦 Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        if [ $? -eq 0 ]; then
            echo "✅ Homebrew installed"
            echo "📦 Now installing TA-Lib..."
            brew install ta-lib
        else
            echo "❌ Failed to install Homebrew"
        fi
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🐧 Detected Linux"
    
    # Check if we're in a Docker container
    if [ -f /.dockerenv ]; then
        echo "🐳 Running in Docker container"
        echo "ℹ️  The updated Dockerfile should handle TA-Lib installation"
        echo "   If you're still having issues, try:"
        echo "   docker-compose down && docker-compose up -d --build --force-recreate"
    else
        echo "📦 Installing TA-Lib system dependencies..."
        
        # Detect package manager
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y build-essential wget
        elif command -v yum &> /dev/null; then
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y wget
        elif command -v dnf &> /dev/null; then
            sudo dnf groupinstall -y "Development Tools"
            sudo dnf install -y wget
        else
            echo "❌ Unsupported package manager"
            exit 1
        fi
        
        echo "📦 Downloading and building TA-Lib from source..."
        cd /tmp
        wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
        tar -xzf ta-lib-0.4.0-src.tar.gz
        cd ta-lib/
        
        # Update config files for modern architectures
        wget -O config.guess 'https://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.guess;hb=HEAD'
        wget -O config.sub 'https://git.savannah.gnu.org/gitweb/?p=config.git;a=blob_plain;f=config.sub;hb=HEAD'
        chmod +x config.guess config.sub
        
        ./configure --prefix=/usr
        make
        sudo make install
        
        echo "✅ TA-Lib installed successfully"
        echo "🔧 Now install the Python wrapper:"
        echo "   pip install TA-Lib"
    fi
    
else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "   Please install TA-Lib manually for your system"
fi

echo ""
echo "📋 Next steps:"
echo "1. Install Python TA-Lib wrapper: pip install TA-Lib"
echo "2. Test installation: python -c 'import talib; print(talib.__version__)'"
echo "3. Run dependency check: python3 check_dependencies.py" 