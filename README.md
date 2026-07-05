Radio Logbook ProA specialized application designed for radio enthusiasts to efficiently manage, analyze, and visualize DX logs. 
This project was developed with the support of Gemini AI, demonstrating how to build professional-grade software without formal programming expertise.
How it Works:
Data Source: It loads your radio data from a local CSV file.
Data Persistence: All updates and modifications are saved directly to the CSV file.
Cross-Platform: The logic is written in Python, making it compatible with any operating system (Windows, macOS, Linux).
Prerequisites:
Python: Download and install the latest version of Python from python.org.
Libraries: Once Python is installed, install the required components via terminal:
pip install streamlit pandas
CSV File Requirements
Your CSV file must contain these columns:
Date: (format: DD/MM/YYYY)
Station: Name of the radio station.
Latitudine: Latitude coordinate.
Longitudine: Longitude coordinate.
Because the application runs on the Streamlit framework, you need a simple execution file to start it easily on your PC.
The Launcher File (LanciaLog.bat)
I have provided a batch file named LanciaLog.bat to automate the launch process.
Ensure the file path inside LanciaLog.bat matches your project folder location.
This file handles the environment setup and launches the app instantly.
Simply double-click the LanciaLog.bat file. The script will automatically navigate to your project directory, launch the Streamlit server, and open the application in your default web browser.
Intelligent Filtering: Advanced sidebar controls to filter logs.
Data Analysis: Automated Pareto analysis for your stations.
Distance Calculation: Real-time distance mapping based on coordinates.
Custom Sorting: Distance-based ranking for long-range catches.
Integrated Workflow: Seamless interface for logging and mapping.
NOTE: THIS IS A FULLY CUSTOMIZABLE PROGRAM. ALL PROVIDED FILES ARE DESIGNED TO BE OPENED AND EDITED USING PYTHON. YOU CAN EASILY MODIFY THE CODE, SETTINGS, AND PERSONALIZED PARAMETERS—SUCH AS DIRECTORY PATHS OR STATION NAMES—TO MATCH YOUR SPECIFIC SYSTEM REQUIREMENTS. PLEASE NOTE THAT THE CURRENT SCRIPTS ARE WRITTEN IN ITALIAN AND ARE CONFIGURED SPECIFICALLY FOR MY PC SETUP; THEREFORE, YOU SHOULD UPDATE THE PATHS WITHIN THE LAUNCHER AND THE SOURCE CODE TO ENSURE IT FUNCTIONS CORRECTLY ON YOUR MACHINE.
