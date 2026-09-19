from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.scan import router as scan_router

app = FastAPI(title="ComplyScan API")

# Allow Live Server, localhost, and all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "ComplyScan backend is running"}