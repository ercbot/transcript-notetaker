# standard
import configparser
import os
import time
import re
# 3rd party
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate

# read config
config = configparser.ConfigParser()
config.read('config.ini')

# read config variables
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = config['REQUIRED']['openai-api-key']

# LangChain Config
# llm
llm = OpenAI(temperature=0)
# prompt
prompt = PromptTemplate(
    template="Write a concise summary of the following: {transcript}",
    input_variables=['transcript']
)
# chain
chain = LLMChain(
    prompt=prompt,
    llm=llm,
    verbose=False
)


def load_transcript(input_file):
    # Google Meet Transcripts have a header which we don't want to be summarized
    header_lines = 5

    file_text = input_file.readlines()

    head = file_text[:header_lines]
    transcript = "".join(file_text[header_lines:])

    return head, transcript


def create_meeting_notes(transcript_file):
    # read config variables
    # if not os.getenv("OPENAI_API_KEY"):
    #     os.environ["OPENAI_API_KEY"] = config['REQUIRED']['openai-api-key']
    # transcript_filepath = config['OPTIONAL']['transcript-filepath']
    # notes_filepath = config['OPTIONAL']['notes-filepath']

    head, transcript = load_transcript(transcript_file)

    # split the transcript on the 5-min timestamps
    regex_pattern = r"[0-9]{2}:[0-9]{2}:0{2}"
    five_min_chunks = re.split(regex_pattern, transcript)

    # create a textsplitter to subdivide those chunks into appropriately sized chunks.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)

    # list the meeting time and the chunks associated with it
    timestamped_summaries = []

    print(f"Summarizing {len(five_min_chunks)*5} minute meeting")
    start_time = time.time()
    # summarize the
    for i, five_minutes_chunk in enumerate(five_min_chunks):
        timestamp = time.strftime('%H:%M:%S', time.gmtime(60 * 5 * i))
        sub_chunks = text_splitter.split_text(five_minutes_chunk)

        summaries = []
        for j, chunk in enumerate(sub_chunks, 1):
            summaries.append(chain.run(chunk))
            print(f"{timestamp}: Chunk {j}/{len(sub_chunks)}")

        timestamped_summaries.append((timestamp, summaries))

        elapsed_time = time.time() - start_time
        minutes = elapsed_time // 60
        print(f"Summarized first {5 * (i+1)} minutes of meeting, {minutes:.0f} minutes {elapsed_time - 60 * minutes:.2f} seconds elapsed")

    first_line = re.split(r"[()]", head[0])

    # Transcript Notes
    meeting_notes = f'''# {first_line[0]}
{first_line[1]}
## Attendees
{head[2]}## Meeting Notes
'''
    for timestamp, summaries in timestamped_summaries:
        meeting_notes += f'### {timestamp}\n'
        for summary in summaries:
            meeting_notes += f"- {summary.strip()}\n"
    meeting_notes += "\nEnd of Meeting"

    return meeting_notes

    # with open(notes_filepath, 'w+') as f:
    #     f.write(meeting_notes)

    # print(f"Export to file {notes_filepath} completed")
