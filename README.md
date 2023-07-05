# Google Meet Transcript AI Notes

## Description

A python script designed to create relevant notes from a transcript of a Google Meet meeting. Currently, with the proper,
options configured, Google Meet will automatically create an AI transcript of your meetings which is saved to Google Drive. 
Often it is more useful to see just the notes from a meeting rather than the full transcript. This script uses OpenAI
prompts to create a detailed summary of the meeting from the transcript, as if it was taking notes in real time during 
the meeting.

You will need an OpenAI API key to use this project.

## Installation 

Run the setup.py file to install the requirements and create the config.ini file

# Usage

Ensure your transcript is a .txt file. 

Configure the name of your transcript and the name of the output notes file in the config.ini file. Run the main.py script. 
