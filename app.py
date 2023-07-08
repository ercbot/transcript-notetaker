# standard
from io import StringIO
# 3rd party
import streamlit as st
# local
import main

st.set_page_config(page_title='Transcript Notetaker', page_icon=':memo:', layout='wide')

st.write("Hello World")

upload = st.file_uploader("Transcript", type='.txt')

take_notes = st.button("Create Notes")

if take_notes and upload:
    upload_stringio = StringIO(upload.getvalue().decode('UTF-8'))

    notes = main.create_meeting_notes(upload_stringio)

if notes:
    st.download_button("Download Notes", notes, "notes.md")

    st.markdown(notes)
