
import os
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client,Client
from routes import users
from routes import projects
from routes import files
from routes import chats

load_dotenv()



app = FastAPI(title="RAG API", description="API for Retrieval-Augmented Generation", version="1.0"  )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG API!"}

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(files.router)
app.include_router(chats.router)



    

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000,reload=True)
    