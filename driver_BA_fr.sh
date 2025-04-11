# !/bin/bash
source /net/local/home/gulleyd/public_html/bulletin/python_virtual_environment/venv/bin/activate # Activate the Python 2.7 virtual environment containing the necessary libraries
cd /net/local/home/gulleyd/public_html/bulletin/ # Change to the appropriate directory in order to import custom libraries not part of the virtual environment
clear
python menu_fr.py # Run the application
cd - # Return to previous directory
source /net/local/home/$USER/.profile
clear
