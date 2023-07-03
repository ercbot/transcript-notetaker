# standard
import configparser
import os
import time
# 3rd party
from langchain.llms import OpenAI
from langchain import LLMChain
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import PromptTemplate

# read config
config = configparser.ConfigParser()
config.read('config.ini')

def summarize_chunks(chunks):
    number_of_chunks = len(chunks)
    print(f"Summarizing: {number_of_chunks} chunks")
    chunk_summaries = []
    start_time = time.time()
    for i, chunk in enumerate(chunks, 1):
        chunk_summaries.append(chain.run(chunk))
        # info
        elapsed_time = time.time() - start_time
        minutes = elapsed_time // 60
        print(f"Completed Summary {i}/{number_of_chunks}, {minutes:.0f} minutes {elapsed_time - 60 * minutes:.2f} seconds elapsed")

    return chunk_summaries


if __name__ == '__main__':
    # read config variables
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = config['REQUIRED']['openai-api-key']
    transcript_filepath = config['OPTIONAL']['transcript-filepath']
    notes_filepath = config['OPTIONAL']['notes-filepath']

    llm = OpenAI(temperature=0)

    loader = UnstructuredFileLoader(transcript_filepath)
    transcript = loader.load()

    # Split the text into smaller chunks that can be processed by the AI
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    chunks = text_splitter.split_documents(transcript)

    prompt = PromptTemplate(
        template="Write a concise summary of the following: {transcript}",
        input_variables=['transcript']
    )

    chain = LLMChain(
        prompt=prompt,
        llm=llm,
        verbose=False
    )

    summaries = summarize_chunks(chunks)

    meeting_notes = ''.join([summary for summary in summaries])

    with open(notes_filepath, 'w') as f:
        f.write(meeting_notes)