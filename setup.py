"""
Run this script first to install requirements.txt and create config file
"""
import configparser
import sys
import subprocess

# install requirements.txt
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

# create default config file
config = configparser.ConfigParser()

# Required
config['REQUIRED'] = {
    "openai-api-key": "Replace this with your key"
}

# Optional
config['OPTIONAL'] = {
    'transcript-filepath': 'transcript.txt',
    'notes-filepath': 'notes.md'
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)
