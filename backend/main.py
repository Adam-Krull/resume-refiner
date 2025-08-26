from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fun import pipeline
from models import JobDesc

app = FastAPI()
origins = ['http://localhost:3000']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.post('/')
async def refine_resume(
    job_desc: JobDesc
):
    job_dict = job_desc.dict()
    return pipeline(job_dict['text'])