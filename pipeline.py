import getpass
import os

from docx import Document

from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import Docx2txtLoader
from langchain_core.prompts import ChatPromptTemplate

if not os.environ.get('GOOGLE_API_KEY'):
    os.environ['GOOGLE_API_KEY'] = getpass.getpass('Enter your Google API Key: ')

model = init_chat_model('gemini-2.5-flash', model_provider='google_genai') 

def pipeline():
    '''Pipeline function to call all functions in order.
    Takes in job description and returns updated resume and cover letter.'''
    #get job description input
    comp, desc = get_desc()
    #read local documents into memory, unpacking list into three objects
    exp, resume, cover = get_docs()
    #update resume using job description and experience
    new_resume = update_resume(exp, desc, resume)
    #update cover letter using job description and experience
    new_cover = update_cover(exp, desc, cover)
    #write updated documents to files with company name
    success = save_docs(comp, new_resume, new_cover)
    print(f'Documents created and saved? {success}')
    return success
def get_desc():
    '''Takes company name and job description as user input.'''
    #get name of company
    comp = input('What is the name of the company? ').lower().strip().replace(' ', '_')
    #read input and return
    desc = input('Paste the job description: ').strip()
    return comp, desc  

def get_docs():
    '''Reads in three documents from local filesystem:
    1) Extended description of professional experience
    2) Current resume
    3) Current cover letter'''
    #define filenames and empty list for document content
    filenames = ['exp.docx', 'resume.docx', 'cover.docx']
    docs = []
    #loop through and read in each file, adding to docs list
    for file in filenames:
        filepath = './docs/' + file
        loader = Docx2txtLoader(filepath)
        doc = loader.load()[0].page_content
        docs.append(doc)
    #return list of length three    
    return docs    

def update_resume(exp, desc, resume):
    '''Takes in professional experience, resume, and job description.
    Outputs the updated resume.'''
    #define system message template including context
    system_template = '''You will refine a candidate/'s resume to make them 
                      a standout applicant for the provided job description. 
                      Only edit the paragraphs describing their professional experience. 
                      Pull directly from their professional experience 
                      to update the resume. Return a resume of similar length.
                      
                      Job description: {desc}
                      
                      Professional experience: {exp}'''
    #define user prompt to share resume
    user_template = '''Please update my resume: {resume}'''
    #roll up into one prompt
    prompt_template = ChatPromptTemplate.from_messages(
        [('system', system_template), ('user', user_template)]
    )
    #invoke (fill) prompt with variable values
    prompt = prompt_template.invoke(
        {
            'desc': desc,
            'exp': exp,
            'resume': resume
        }
    )
    #invoke model to get response and return the content
    response = model.invoke(prompt)
    return response.content

def update_cover(exp, desc, cover):
    '''Takes professional experience, job description, and cover letter.
    Returns updated cover letter with relevant experience.'''
    #define system message template
    system_template = '''Refine the candidate/'s cover letter to be a standout applicant
                      for the provided job description. Pull directly from their provided 
                      professional experience to make the revisions. Retain the format of the 
                      original cover letter: first paragraph is the introduction, second 
                      paragraph explains relevant experience in greater detail, and third 
                      paragraph summarizes the experience and invites recruiter to engage.
                      Return a cover letter of similar length.
                      
                      Job description: {desc}
                      
                      Professional experience: {exp}'''
    #define simple template for user message
    user_template = '''Please update my cover letter: {cover}'''
    #wrap into single prompt
    prompt_template = ChatPromptTemplate.from_messages(
        [('system', system_template), ('user', user_template)]
    )
    #invoke with variables to produce complete prompt
    prompt = prompt_template.invoke(
        {
            'desc': desc,
            'exp': exp,
            'cover': cover
        }
    )
    #ship completed prompt to LLM and return content
    response = model.invoke(prompt)
    return response.content

def save_docs(comp, resume, cover):
    '''Takes the company name, resume, and cover letter.
    Creates a new folder for the company name and saves
    the updated documents to the folder.'''
    #create folder name
    folder = f'./{comp}/'
    #check for existence of folder 
    if os.path.isdir(folder):
        pass
    else:
        os.mkdir(folder)
    #save resume and cover letter to folder
    filenames = ['resume.docx', 'cover.docx']
    documents = [resume, cover]
    for filename, doc in zip(filenames, documents):
        document = Document()
        document.add_paragraph(doc)
        filepath = folder + filename
        document.save(filepath)
    return True    

if __name__ == '__main__':
    pipeline()