# Virtual Environment Setup Guide

## 🐍 Python Backend Dependencies

### 1. Create and Activate Virtual Environment

```bash
# Navigate to your project directory
cd /Users/bellayang/Capstone-2T6

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 2. Install Python Dependencies

```bash
# Install core dependencies
pip install --upgrade pip

# Install from existing requirements.txt
pip install -r requirements.txt

# Install additional dependencies for audio processing
pip install opensmile
pip install pydub
pip install nltk
pip install scikit-learn
pip install joblib

# Install dependencies for video processing
pip install opencv-python
pip install mediapipe
pip install ffmpeg-python
pip install py-feat

# Install additional ML and data processing libraries
pip install matplotlib
pip install seaborn
pip install plotly

# Install Hugging Face for LLM integration
pip install huggingface-hub
pip install transformers
pip install torch

# Install additional utilities
pip install python-multipart  # For file uploads in FastAPI
pip install aiofiles         # For async file operations
```

### 3. System Dependencies (macOS)

```bash
# Install FFmpeg (required for video/audio processing)
brew install ffmpeg

# Install SoX (for audio processing)
brew install sox

# If you don't have Homebrew, install it first:
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 4. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt')"
```

## ⚛️ Frontend Dependencies

### 1. Install Node.js Dependencies

```bash
# Make sure you're in the project root directory
cd /Users/bellayang/Capstone-2T6

# Install frontend dependencies
npm install
```

## 🚀 Complete Setup Script

Here's a complete setup script you can run:

```bash
#!/bin/bash

# Navigate to project directory
cd /Users/bellayang/Capstone-2T6

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install opensmile pydub nltk scikit-learn joblib
pip install opencv-python mediapipe ffmpeg-python py-feat
pip install matplotlib seaborn plotly
pip install huggingface-hub transformers torch
pip install python-multipart aiofiles

# Download NLTK data
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt')"

# Install system dependencies (macOS)
echo "Installing system dependencies..."
if command -v brew &> /dev/null; then
    brew install ffmpeg sox
else
    echo "Homebrew not found. Please install FFmpeg and SoX manually."
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

echo "Setup complete! 🎉"
echo ""
echo "To start the backend:"
echo "  source venv/bin/activate"
echo "  cd backend"
echo "  uvicorn app:app --reload"
echo ""
echo "To start the frontend:"
echo "  npm run dev"
```

## 📋 Complete Requirements File

I'll also create an updated requirements.txt with all dependencies:

```bash
# Core API and web framework
fastapi==0.108.0
uvicorn==0.22.0
python-multipart==0.0.6
aiofiles==23.2.1

# Audio processing
whisper==1.1.10
opensmile
pydub
sounddevice==0.5.2

# Video processing
opencv-python
mediapipe
ffmpeg-python
py-feat

# Machine Learning
scikit-learn
numpy==2.3.0
pandas
joblib
matplotlib
seaborn
plotly

# Natural Language Processing
nltk

# LLM Integration
huggingface-hub
transformers
torch

# Data processing
scipy==1.15.3
pydantic==2.11.0

# Utilities
tqdm==4.67.1
requests==2.32.3
python-dotenv==1.1.0
```

## 🔧 Troubleshooting

### Common Issues:

1. **FFmpeg not found**: Make sure FFmpeg is installed and in your PATH
2. **OpenCV issues**: Try `pip install opencv-python-headless` instead
3. **Py-Feat installation**: May require additional system dependencies
4. **CUDA/GPU issues**: Install CPU-only PyTorch if you don't have GPU support

### Verify Installation:

```bash
# Test Python imports
python -c "
import whisper
import opensmile
import cv2
import mediapipe
import pandas as pd
import sklearn
print('All imports successful!')
"

# Test backend
cd backend
python -c "from app import app; print('Backend imports successful!')"

# Test frontend
cd ..
npm run build
```

## 🎯 Quick Start Commands

After setup, use these commands to run the application:

```bash
# Terminal 1 - Backend
cd /Users/bellayang/Capstone-2T6
source venv/bin/activate
cd backend
uvicorn app:app --reload

# Terminal 2 - Frontend  
cd /Users/bellayang/Capstone-2T6
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
