import subprocess

# List of python files to run
python_files = ['scrapeCentarTehnikeWithDBv4.py', 'scrapeINSTARwithDBv3.py', 'scrapeSanctaDomenicaWithDBv3.py',
                'comparingTVs.py']

# Running each python file one by one
for file in python_files:
    subprocess.run(['python', file])
