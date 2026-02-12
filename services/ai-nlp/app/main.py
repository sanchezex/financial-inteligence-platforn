from fastapi import FastAPI
import uvicorn

app = FastAPI(title="AI/NLP Service", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ai-nlp"}

@app.get("/")
async def root():
    return {"service": "ai-nlp", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)

