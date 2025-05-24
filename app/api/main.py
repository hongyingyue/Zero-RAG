from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from datetime import timedelta

from app.services.rag_service import RAGService
from app.services.agent_service import AgentService
from app.configs.settings import get_settings
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    User,
    fake_users_db,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Agentic RAG API")
settings = get_settings()

# Initialize services
rag_service = RAGService()
agent_service = AgentService(rag_service)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Token(BaseModel):
    access_token: str
    token_type: str

class Query(BaseModel):
    text: str
    chat_history: Optional[List[Dict[str, str]]] = None

class Document(BaseModel):
    content: str
    source: Optional[str] = None

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/query")
async def query_endpoint(
    query: Query,
    current_user: User = Depends(get_current_active_user)
):
    """Query the agent with RAG capabilities."""
    try:
        response = await agent_service.run(query.text, query.chat_history)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents")
async def upload_documents(
    documents: List[Document],
    current_user: User = Depends(get_current_active_user)
):
    """Upload and process documents."""
    try:
        docs = [doc.dict() for doc in documents]
        rag_service.process_documents(docs)
        return {"message": f"Successfully processed {len(docs)} documents"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/file")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload and process a single file."""
    try:
        content = await file.read()
        text = content.decode()
        doc = {"content": text, "source": file.filename}
        rag_service.process_documents([doc])
        return {"message": f"Successfully processed file: {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents")
async def clear_documents(
    current_user: User = Depends(get_current_active_user)
):
    """Clear all documents from the vector store."""
    try:
        rag_service.clear_collection()
        return {"message": "Successfully cleared all documents"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        reload=True
    ) 