#!/usr/bin/env python3
"""
Setup script for Microsoft Agent Framework - Marking Workflow
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def setup_environment():
    """Setup environment file"""
    env_example = Path(".env.example")
    env_file = Path(".env")

    if env_file.exists():
        print("✅ Environment file already exists")
        return True

    if env_example.exists():
        print("📝 Creating environment file...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            content = src.read()
            dst.write(content)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your OpenAI API key")
        return True
    else:
        print("❌ .env.example not found")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ["examples", "logs", "output"]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    print(f"✅ Created directories: {', '.join(directories)}")

def verify_installation():
    """Verify the installation"""
    print("\n🔍 Verifying installation...")

    try:
        import autogen
        print("✅ Microsoft AutoGen imported successfully")
    except ImportError:
        print("❌ Failed to import AutoGen")
        return False

    try:
        import openai
        print("✅ OpenAI library imported successfully")
    except ImportError:
        print("❌ Failed to import OpenAI library")
        return False

    try:
        from schemas import StudentWork, Subject
        print("✅ Custom schemas imported successfully")
    except ImportError:
        print("❌ Failed to import custom schemas")
        return False

    return True

def main():
    """Main setup function"""
    print("🚀 Microsoft Agent Framework - Marking Workflow Setup")
    print("=" * 60)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install requirements
    if not install_requirements():
        sys.exit(1)

    # Setup environment
    if not setup_environment():
        sys.exit(1)

    # Create directories
    create_directories()

    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed")
        sys.exit(1)

    print("\n✅ Setup completed successfully!")
    print("\n📝 Next Steps:")
    print("1. Edit .env file with your OpenAI API key")
    print("2. Run: python main.py (for example workflow)")
    print("3. Run: python utils.py (for testing)")
    print("4. Run: python main.py --interactive (for custom input)")

    print("\n📖 Documentation:")
    print("- README.md: Complete usage guide")
    print("- examples/sample_data.json: Sample input data")
    print("- .env.example: Environment configuration template")

if __name__ == "__main__":
    main()