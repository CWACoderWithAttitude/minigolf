from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "frontend/templates")))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main page of the application.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/start-game", response_class=HTMLResponse)
async def start_game(request: Request):
    """A placeholder endpoint to demonstrate HTMX interactivity."""
    return "<div>A new game has started!</div>"

def __main__():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    __main__()