from pydantic import BaseModel


class KnowledgeBaseRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class ChatRequest(BaseModel):
    knowledge_base_id: str
    question: str
    history: Optional[List[Dict[str, str]]] = []

class ChatResponse(BaseModel):
    answer: str
    source_documents: Optional[List[Dict[str, Any]]] = []
    conversation_id: Optional[str] = None

class KnowledgeBaseInfo(BaseModel):
    id: str
    name: str
    description: str
    file_count: int
    created_at: str

class UploadResponse(BaseModel):
    success: bool
    message: str
    file_ids: Optional[List[str]] = []