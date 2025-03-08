from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.responses import Response, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from sqlalchemy.orm import Session
import os
import uuid
from dotenv import load_dotenv

from app.services.llm_service import LLMService
from app.services.simulation_service import SimulationService
from app.services.analytics_service import AnalyticsService
# from app.models.database import init_db, Call, Message
from app.core.auth import get_current_user, create_access_token, User, Token
from app.core.logger import logger
from app.services.sentiment_service import SentimentService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="AI Call Center")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Initialize services
llm_service = LLMService(api_key=os.getenv("GROQ_API_KEY"))
simulation_service = SimulationService(llm_service)
analytics_service = AnalyticsService()
sentiment_service = SentimentService()

# Initialize database (commented out for future use)
# engine = init_db(os.getenv("DATABASE_URL", "sqlite:///./call_center.db"))

# Dependency to get database session (commented out for future use)
# def get_db():
#     db = Session(engine)
#     try:
#         yield db
#     finally:
#         db.close()

# Web interface routes
@app.get("/")
async def home(request: Request):
    empty_stats = {
        "total_calls": 0,
        "average_duration": 0,
        "total_messages": 0
    }
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": empty_stats,
        "recent_calls": []
    })

@app.get("/simulator")
async def simulator(request: Request):
    return templates.TemplateResponse("call_simulator.html", {"request": request})

# Simulation API endpoints
@app.post("/api/simulate/start")
async def start_simulation():
    """Start a new call simulation."""
    simulation_id = str(uuid.uuid4())
    if simulation_service.start_simulation(simulation_id):
        return JSONResponse({"simulation_id": simulation_id})
    raise HTTPException(status_code=400, detail="Could not start simulation")

@app.post("/api/simulate/end")
async def end_simulation(request: Request):
    """End an active call simulation."""
    data = await request.json()
    simulation_id = data.get('simulation_id')
    
    if not simulation_id:
        return JSONResponse({'error': 'Missing simulation_id'}, status_code=400)
        
    if simulation_service.end_simulation(simulation_id):
        return JSONResponse({"status": "success"})
    raise HTTPException(status_code=404, detail="Simulation not found")

@app.post("/api/simulate/message")
async def process_message(request: Request):
    """Process a message in the simulation."""
    data = await request.json()
    simulation_id = data.get('simulation_id')
    message = data.get('message')
    
    if not all([simulation_id, message]):
        return JSONResponse({'error': 'Missing required fields'}, status_code=400)
        
    response = await simulation_service.process_message(simulation_id, message)
    if response:
        return JSONResponse({"response": response})
    raise HTTPException(status_code=404, detail="Simulation not found or inactive")

@app.post("/api/simulate/transfer")
async def transfer_simulation(request: Request):
    data = await request.json()
    simulation_id = data.get('simulation_id')
    agent_id = data.get('agent_id')
    reason = data.get('reason')
    
    if not all([simulation_id, agent_id, reason]):
        return JSONResponse({'error': 'Missing required fields'}, status_code=400)
    
    try:
        simulation_service.transfer_call(simulation_id, agent_id, reason)
        return JSONResponse({'status': 'success', 'message': 'Call transferred successfully'})
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=400)

@app.post("/api/simulate/note")
async def add_note(request: Request):
    data = await request.json()
    simulation_id = data.get('simulation_id')
    content = data.get('content')
    
    if not all([simulation_id, content]):
        return JSONResponse({'error': 'Missing required fields'}, status_code=400)
    
    try:
        simulation_service.add_note(simulation_id, content)
        return JSONResponse({'status': 'success', 'message': 'Note added successfully'})
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=400)

@app.post("/api/simulate/tag")
async def add_tag(request: Request):
    data = await request.json()
    simulation_id = data.get('simulation_id')
    name = data.get('name')
    tag_type = data.get('type', 'default')
    
    if not all([simulation_id, name]):
        return JSONResponse({'error': 'Missing required fields'}, status_code=400)
    
    try:
        simulation_service.add_tag(simulation_id, name, tag_type)
        return JSONResponse({'status': 'success', 'message': 'Tag added successfully'})
    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=400)

@app.get("/call-history")
async def call_history(request: Request):
    simulations = simulation_service.get_all_simulations()
    return templates.TemplateResponse("call_history.html", {
        "request": request,
        "simulations": simulations
    })

# Protected API endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != os.getenv("API_USERNAME") or form_data.password != os.getenv("API_PASSWORD"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

# Database-dependent endpoints (commented out for future use)
# @app.get("/api/calls/statistics")
# async def get_call_statistics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     """Get overall call statistics."""
#     logger.info("Fetching call statistics")
#     stats = analytics_service.get_call_statistics(db)
#     return JSONResponse(content=stats)

# @app.get("/api/calls/{call_id}/history")
# async def get_call_history(
#     call_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Get detailed history for a specific call."""
#     logger.info(f"Fetching history for call {call_id}")
#     history = analytics_service.get_call_history(db, call_id)
#     if not history:
#         raise HTTPException(status_code=404, detail="Call not found")
#     return JSONResponse(content=history)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 