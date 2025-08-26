import getpass
import os

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_community import GoogleDriveLoader

if not os.environ.get('GOOGLE_API_KEY'):
    print('Hello there.')
    os.environ['GOOGLE_API_KEY'] = getpass.getpass('Enter your Google API Key: ')

llm = init_chat_model('gemini-2.5-flash', model_provider='google_genai')

def pipeline(job_desc):
    #condense job description down to desired qualifications
    jd = condense_desc(job_desc)
    #read in 3 documents - detailed experience, resume, and cover letter
    docs = read_docs()
    #update resume

    #update cover letter

    #return resume and cover letter
    pass

def condense_desc(job_desc, model = llm):
    '''Receives the job description and returns a short list of technologies/proficiencies.'''
    #create prompt
    template = "Condense the following job description to a short list of desired skills: {job_desc}"
    #wrap into prompt template
    prompt_template = ChatPromptTemplate.from_messages(
        [('system', template), ('user', '{job_desc}')],
    )
    #invoke prompt template to create prompt object
    prompt = prompt_template.invoke({'job_desc': job_desc})
    #invoke model with prompt object to obtain response and return
    response = model.invoke(prompt)
    return response.content

def read_docs():
    '''Reads in all documents from designated folder.'''
    #create loader object pointed to drive folder containing docs
    loader = GoogleDriveLoader(
        folder_id = '1eKNZFPKh9H34mnEiDYLIZ6JGmX1YpTFC',
        token_path = './google_token.json',
    )
    #load the documents and return
    docs = loader.load()
    print(docs)
    return docs