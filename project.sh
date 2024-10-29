#!/bin/bash

# Set project name
PROJECT_NAME="streamlit_app"

# Create project directory
#mkdir $PROJECT_NAME
#cd $PROJECT_NAME

# Create subdirectories
mkdir config
mkdir models
mkdir pages
mkdir services
mkdir utils

# Create sub-subdirectories
mkdir pages/user
mkdir pages/company
mkdir pages/vc
mkdir pages/training

# Create __init__.py files
touch pages/user/__init__.py
touch pages/company/__init__.py
touch pages/vc/__init__.py
touch pages/training/__init__.py

# Create other files
touch config/settings.py
touch config/logging.py
touch requirements.txt
touch .gitignore
touch README.md
touch app.py

# Create user subpages
touch pages/user/user_page.py
touch pages/user/user_subpage1.py
touch pages/user/user_subpage2.py

# Create client subpages
touch pages/company/company_page.py
touch pages/company/company_subpage1.py
touch pages/company/company_subpage2.py

# Create vc subpages
touch pages/vc/vc_page.py
touch pages/vc/vc_subpage1.py
touch pages/vc/vc_subpage2.py

# Create training subpages
touch pages/training/training_page.py
touch pages/training/training_subpage1.py
touch pages/training/training_subpage2.py

# Create services
touch services/user_service.py
touch services/company_service.py
touch services/vc_service.py
touch services/training_service.py

# Create models
touch models/user.py
touch models/company.py
touch models/vc.py
touch models/training.py

echo "Folder structure generated successfully!"