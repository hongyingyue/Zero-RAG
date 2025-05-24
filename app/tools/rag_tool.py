
from transformers import Tool


class RAGTool:
    name = "retrieval"
    description = "A tool that can retrieve the context information about query."
    inputs = {
        "question": {"description": "the question to answer", "type": "text"},
    }
    output_type = "text"

    def __init__(self, retrieval_engine):
        self.retrieval_engine = retrieval_engine

    def __call__(self, question: str) -> str:
        return self.retrieval_engine.retrieve(question)


class Agent:
    def __init__(self, llm_model_name: str, retrieval_tool: RAGTool):
        self.tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
        self.model = AutoModelForCausalLM.from_pretrained(llm_model_name)
        self.retrieval_tool = retrieval_tool

    def generate_response(self, user_query: str) -> str:
        # Simple decision-making: if the query looks like it needs external info, use the tool
        if "what is" in user_query.lower() or "who is" in user_query.lower() or "when was" in user_query.lower():
            print("\n[Agent]: It seems like this question might need external information. Using the retrieval tool...")
            context = self.retrieval_tool(question=user_query)
            if "No relevant context found" not in context:
                prompt = f"Based on the following information: '{context}', answer the question: '{user_query}'"
            else:
                prompt = user_query # Try to answer without context if retrieval fails
        else:
            prompt = user_query

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt")
        output = self.model.generate(input_ids, max_length=100, num_return_sequences=1, pad_token_id=self.tokenizer.eos_token_id)
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return response

# Initialize components
knowledge = {
    "Artificial Intelligence": "Artificial intelligence (AI) is intelligence demonstrated by machines, as opposed to natural intelligence displayed by animals including humans.",
    "Burnaby Population": "The population of Burnaby, British Columbia is approximately 250,000 as of recent estimates.",
    "Transformer Architecture": "The Transformer is a deep learning model that adopts the mechanism of self-attention, differentially weighting the significance of each part of the input data.",
}
retrieval_engine = Retrieval(knowledge_base=knowledge)
rag_tool = RAGTool(retrieval_engine=retrieval_engine)
agent = Agent("gpt2", rag_tool) # Using a smaller model for demo purposes

# Interact with the agent
print("Welcome to the simple Agentic RAG demo!")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = agent.generate_response(user_input)
    print(f"Agent: {response}")
