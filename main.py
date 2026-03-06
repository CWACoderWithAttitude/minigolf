from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.orm import Session

from database import SessionLocal, engine
import crud
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "frontend/templates")))

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main page of the application.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start-game", response_class=HTMLResponse)
async def start_game(request: Request, db: Session = Depends(get_db)):
    """
    Starts a new game with a course name and a list of players from a form.
    """
    form_data = await request.form()
    course_name = form_data.get("course_name") or "Mystic Dunes"
    player_names = [p for p in form_data.getlist("players") if p]

    if not player_names:
        return HTMLResponse("<div id='game-area'>Please enter at least one player.</div>", status_code=400)

    game = crud.create_game(db=db, course_name=course_name, player_names=player_names)

    return templates.TemplateResponse("partials/game_status.html", {"request": request, "game": game})

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()