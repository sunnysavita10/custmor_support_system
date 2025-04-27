import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from langchain_core.runnables import RunnablePassthrough

from langchain_core.output_parsers import StrOutputParser

from langchain_core.prompts import ChatPromptTemplate

from retriever.retrieval import Retriever

from utils.model_loader import ModelLoader

from prompt_library.prompt import PROMPT_TEMPLATES


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") 
templates = Jinja2Templates(directory="templates")
# Allow CORS (optional for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

retriever_obj = Retriever()

model_loader = ModelLoader()

def invoke_chain(query:str):
    
    retriever=retriever_obj.load_retriever()
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATES["product_bot"])
    llm= model_loader.load_llm()
    
    chain=(
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    
    )
    
    output=chain.invoke(query)
    
    return output

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the chat interface.
    """
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/get",response_class=HTMLResponse)
async def chat(msg:str=Form(...)):
    result=invoke_chain(msg)
    print(f"Response: {result}")
    return result