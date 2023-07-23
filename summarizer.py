# built in
from io import StringIO
import re
import time
# 3rd party - located in requirements.txt
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai

HEADER_SIZE = 5 # number of lines in the transcript header
CHUNK_SIZE = 2000 # approximate length in characters for each chunk being summarized
TEMPERATURE = 0


def load_transcript(input_file):
    """Load the text from the transcript uploaded using the file uploader widget"""
    # transform file from bytes to string
    input_string = StringIO(input_file.getvalue().decode('UTF-8'))

    # Google Meet Transcripts have a header with info like the meeting title, date, and attendees
    # We'll want to extract this information separately, instead of having it passed to a summarizer

    file_text = input_string.readlines()

    header = file_text[:HEADER_SIZE]
    transcript = "".join(file_text[HEADER_SIZE:])

    return header, transcript


def chunk_transcript(transcript: str):
    # Google Meet transcripts show the timestamp every 5 minutes
    # split the transcript on the 5-min timestamps
    timestamp_regex_pattern = r"[0-9]{2}:[0-9]{2}:0{2}"
    five_minute_chunks = re.split(timestamp_regex_pattern, transcript)

    # create a textsplitter to subdivide those chunks into appropriately sized chunks.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE)

    # for each 5 minute chunk divide further into sub-chunks of appropriate length
    chunks = [text_splitter.split_text(five_minute_chunk) for five_minute_chunk in five_minute_chunks]

    # chunks, is a list of lists
    # outer list represents 5-minute sections of the meeting
    # inner lists representing the subdivisions of that sections that are small enough to be summarized thoroughly

    return chunks


def summarize_chunks(five_minute_chunks, user_api_key, debug = False):
    """Create summaries of each chunk of the transcript"""

    system_prompt = '''As a professional summarizer, create a concise and comprehensive summary of the provided conversation, while adhering to these guidelines:
    1. Craft a summary that is detailed, thorough, in-depth, and complex, while maintaining clarity and conciseness.
    2, Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects.
    3. Rely strictly on the provided text, without including external information.
    4. Format the summary in paragraph form for easy understanding.
    5. Do not start the response with "In this conversation", "During this conversation", "During the conversation" or a similar phrase
    '''

    total_chunks = sum([len(five_minute_chunk) for five_minute_chunk in five_minute_chunks])
    number_of_summarized_chunks = 0

    progress_bar = st.progress(number_of_summarized_chunks, f"Summarized {number_of_summarized_chunks}/{total_chunks} Chunks...")

    five_minute_summaries = []
    for sub_chunks in five_minute_chunks:
        summaries = []
        for chunk in sub_chunks:
            if not debug:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk}
                ]

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=TEMPERATURE,
                    api_key=user_api_key
                )

                summary = response['choices'][0]['message']['content']
            else:
                summary = "I would be a meeting note :D"

            # update progress bar
            number_of_summarized_chunks += 1
            progress_bar.progress(number_of_summarized_chunks / total_chunks,
                                  f"Summarized {number_of_summarized_chunks}/{total_chunks} Chunks...")

            summaries.append(summary)

        five_minute_summaries.append(summaries)

    return five_minute_summaries


def format_notes(big_summaries, header):
    """Create a string containing the meeting notes in Markdown format"""
    # The header of Google Meet transcripts are always the same structure, so we can manually extract info from them
    first_line = re.split(r"[()]", header[0]) # the first line contains both the title and the date
    meeting_name = first_line[0]
    meeting_date = first_line[1]
    attendees = header[2]

    meeting_notes = f"# {meeting_name}\n{meeting_date}\n## Attendees\n{attendees}\n## Meeting Notes\n"

    for i, summaries in enumerate(big_summaries):
        timestamp = time.strftime('%H:%M:%S', time.gmtime(60 * 5 * i))

        meeting_notes += f"### {timestamp}\n"
        for summary in summaries:
            meeting_notes += f"- {summary.strip()}\n"

    return meeting_notes
