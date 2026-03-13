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


@app.post("/select-player-count", response_class=HTMLResponse)
async def select_player_count(request: Request):
    """
    Accept player count and serve the player names form.
    """
    form_data = await request.form()
    course_name = form_data.get("course_name") or "Mystic Dunes"
    player_count = form_data.get("player_count", "").strip()
    
    if not player_count:
        return HTMLResponse('<div class="error">Please select the number of players.</div>', status_code=400)
    
    try:
        player_count = int(player_count)
        if player_count < 1 or player_count > 10:
            return HTMLResponse('<div class="error">Please select between 1 and 10 players.</div>', status_code=400)
    except ValueError:
        return HTMLResponse('<div class="error">Invalid player count.</div>', status_code=400)
    
    return templates.TemplateResponse(
        "partials/player_names_form.html",
        {"request": request, "course_name": course_name, "player_count": player_count}
    )


@app.post("/submit-player-names", response_class=HTMLResponse)
async def submit_player_names(request: Request, db: Session = Depends(get_db)):
    """
    Create a game with the provided player names.
    """
    form_data = await request.form()
    course_name = form_data.get("course_name") or "Mystic Dunes"
    player_names = [p.strip() for p in form_data.getlist("players") if p.strip()]

    if not player_names:
        return HTMLResponse('<div class="error">Please enter at least one player name.</div>', status_code=400)
    
    if len(player_names) != len(set(player_names)):
        return HTMLResponse('<div class="error">Player names must be unique.</div>', status_code=400)

    game = crud.create_game(db=db, course_name=course_name, player_names=player_names)

    return templates.TemplateResponse(
        "partials/game_setup.html",
        {"request": request, "game": game}
    )


@app.post("/submit-game-setup", response_class=HTMLResponse)
async def submit_game_setup(request: Request, db: Session = Depends(get_db)):
    """
    Set number of holes and start the game.
    """
    form_data = await request.form()
    game_id = form_data.get("game_id")
    number_of_holes = form_data.get("number_of_holes", "18")

    try:
        game_id = int(game_id)
        number_of_holes = int(number_of_holes)
        if number_of_holes not in [9, 18, 27]:
            return HTMLResponse('<div class="error">Number of holes must be 9, 18, or 27.</div>', status_code=400)
    except ValueError:
        return HTMLResponse('<div class="error">Invalid input.</div>', status_code=400)

    game = crud.update_game(db=db, game_id=game_id, number_of_holes=number_of_holes, current_hole=1)
    
    if not game:
        return HTMLResponse('<div class="error">Game not found.</div>', status_code=404)

    return templates.TemplateResponse(
        "partials/scoring_interface.html",
        {"request": request, "game": game, "current_hole": 1}
    )


@app.post("/record-score/{game_id}/{hole_number}", response_class=HTMLResponse)
async def record_score(game_id: int, hole_number: int, request: Request, db: Session = Depends(get_db)):
    """
    Record scores for all players for the current hole.
    """
    game = crud.get_game(db, game_id)
    if not game:
        return HTMLResponse('<div class="error">Game not found.</div>', status_code=404)

    form_data = await request.form()
    
    try:
        hole_number = int(hole_number)
        if hole_number < 1 or hole_number > game.number_of_holes:
            return HTMLResponse('<div class="error">Invalid hole number.</div>', status_code=400)

        for player in game.players:
            strokes_key = f"strokes_{player.id}"
            strokes = form_data.get(strokes_key)
            
            if strokes:
                try:
                    strokes = int(strokes)
                    if strokes < 1:
                        return HTMLResponse(f'<div class="error">Strokes must be positive for {player.name}.</div>', status_code=400)
                    crud.record_score(db, game_id, player.id, hole_number, strokes)
                except ValueError:
                    return HTMLResponse(f'<div class="error">Invalid stroke count for {player.name}.</div>', status_code=400)
    except ValueError:
        return HTMLResponse('<div class="error">Invalid hole number.</div>', status_code=400)

    # Move to next hole or complete game
    next_hole = hole_number + 1
    if next_hole > game.number_of_holes:
        crud.update_game(db, game_id, is_completed=1)
        game = crud.get_game(db, game_id)
        leaderboard = crud.get_game_leaderboard(db, game_id)
        return templates.TemplateResponse(
            "partials/game_complete.html",
            {"request": request, "game": game, "leaderboard": enumerate(leaderboard, 1)}
        )
    else:
        crud.update_game(db, game_id, current_hole=next_hole)
        game = crud.get_game(db, game_id)
        return templates.TemplateResponse(
            "partials/scoring_interface.html",
            {"request": request, "game": game, "current_hole": next_hole}
        )


@app.get("/game/{game_id}/scorecard", response_class=HTMLResponse)
async def get_scorecard(game_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Return the scorecard for the current game state.
    """
    game = crud.get_game(db, game_id)
    if not game:
        return HTMLResponse('<div class="error">Game not found.</div>', status_code=404)

    all_scores = crud.get_game_scores(db, game_id)
    scores_dict = {}
    for score in all_scores:
        scores_dict[(score.player_id, score.hole_number)] = score.strokes

    totals = {}
    for player in game.players:
        totals[player.id] = sum(s.strokes for s in all_scores if s.player_id == player.id)

    max_hole = game.current_hole
    winner = None
    if game.is_completed:
        leaderboard = crud.get_game_leaderboard(db, game_id)
        if leaderboard:
            winner = leaderboard[0]["name"]

    return templates.TemplateResponse(
        "partials/scorecard.html",
        {
            "request": request,
            "game_id": game_id,
            "players": game.players,
            "scores": scores_dict,
            "totals": totals,
            "max_hole": max_hole,
            "winner": winner
        }
    )


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()