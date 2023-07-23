---
title: Google Meet Transcript Notetaker
emoji: 📝
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.24.0
app_file: app.py
pinned: false
---

# Google Meet Transcript AI Notes

## Description

A Streamlit app designed to create relevant notes from a transcript of a Google Meet meeting. Currently, with the proper,
options configured, Google Meet will automatically create an AI transcript of your meetings which is saved to Google Drive. 
Often it is more useful to see just the notes from a meeting rather than the full transcript. This app uses OpenAI
prompts to create a detailed summary of the meeting from the transcript, as if it was taking notes in real time during 
the meeting.

You will need an OpenAI API key to use this project.

## Hugging Face Space

This a demo of this app is hosted as a [Hugging Face Space](https://huggingface.co/spaces/ericbotti/transcript-notetaker).

## Installation 

install the requirements from the requirements.txt using:

``
pip install -r requirements.txt
``

## Usage

Enter your API key in the text input field, and upload your transcript as a .txt file. 

You should then be able to press the "Create Notes" button which will then start summarization process. 
This can take a few minutes, depending on the size of your file. 

When completed the notes will display on the app, and you will be able to download them in a file called "notes.md"
