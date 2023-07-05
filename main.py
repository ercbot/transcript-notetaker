# standard
import configparser
import os
import time
import re
# 3rd party
from langchain.llms import OpenAI
from langchain import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate

# read config
config = configparser.ConfigParser()
config.read('config.ini')


def load_transcript(path: str):
    # Google Meet Transcripts have a header which we don't want to be summarized
    header_lines = 5

    with open(path, 'r') as input_file:
        file_text = input_file.readlines()

    head = file_text[:header_lines]
    transcript = "".join(file_text[header_lines:])

    return head, transcript


if __name__ == '__main__':
    # read config variables
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = config['REQUIRED']['openai-api-key']
    transcript_filepath = config['OPTIONAL']['transcript-filepath']
    notes_filepath = config['OPTIONAL']['notes-filepath']

    llm = OpenAI(temperature=0)

    head, transcript = load_transcript(transcript_filepath)

    # split the transcript on the 5-min timestamps
    regex_pattern = r"[0-9]{2}:[0-9]{2}:[0-9]{2}"
    five_min_chunks = re.split(regex_pattern, transcript)

    # create a textsplitter to subdivide those chunks into appropriately sized chunks.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)

    # prompt
    prompt = PromptTemplate(
        template="Write a concise summary of the following: {transcript}",
        input_variables=['transcript']
    )

    chain = LLMChain(
        prompt=prompt,
        llm=llm,
        verbose=False
    )

    # list the meeting time and the chunks associated with it
    timestamped_summaries = []

    print(f"Summarizing {len(five_min_chunks)*5} minute meeting")
    start_time = time.time()
    # summarize the
    for i, five_minutes_chunk in enumerate(five_min_chunks):
        timestamp = time.strftime('%H:%M:%S', time.gmtime(60 * 5 * i))
        sub_chunks = text_splitter.split_text(five_minutes_chunk)

        summaries = []
        for j, chunk in enumerate(sub_chunks):
            summaries.append(chain.run(chunk))
            print(f"{timestamp}: Chunk {j}/{len(sub_chunks)}")

        timestamped_summaries.append((timestamp, summaries))

        elapsed_time = time.time() - start_time
        minutes = elapsed_time // 60
        print(f"Summarized first {5 * (i+1)} minutes of meeting, {minutes:.0f} minutes {elapsed_time - 60 * minutes:.2f} seconds elapsed")

    first_line = re.split(r"[()]", head[0])

    # Write summaries to file
    with open(notes_filepath, 'w+') as f:
        f.write(f"# {first_line[0]}\n")
        f.write(f"{first_line[1]}\n")
        f.write("## Attendees\n")
        f.write(f"{head[2]}\n")
        f.write('## Meeting Notes\n')
        for timestamp, summaries in timestamped_summaries:
            f.write(f"### {timestamp}\n")
            for summary in summaries:
                f.write(f"- {summary.strip()}\n")

    print(f"Export to file {notes_filepath} completed")
