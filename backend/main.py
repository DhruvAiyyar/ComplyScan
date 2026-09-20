"""
ComplyScan - FastAPI Application
"""

from fastapi import FastAPI

from database import create_tables
from routes.scans import router as scans_router
from routes.dashboard import router as dashboard_router
from routes.reports import router as reports_router

# Create FastAPI application.
app = FastAPI(
    title="ComplyScan API",
    description="Packaged Commodity Label Compliance Checker",
    version="1.0"
)


# Make sure database tables exist.
create_tables()


# Register scan routes.
app.include_router(scans_router)

# Register dashboard routes.
app.include_router(dashboard_router)

app.include_router(reports_router)

@app.get("/")
def root():
    """
    Simple health-check endpoint.
    """
    return {
        "message": "ComplyScan backend is running"
    }