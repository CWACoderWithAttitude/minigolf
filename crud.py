from sqlalchemy.orm import Session
import models

# Player CRUD
def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def get_player_by_name(db: Session, name: str):
    return db.query(models.Player).filter(models.Player.name == name).first()

def get_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Player).offset(skip).limit(limit).all()

def create_player(db: Session, name: str):
    db_player = models.Player(name=name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

# Game CRUD
def create_game(db: Session, course_name: str, player_names: list[str], number_of_holes: int = 18):
    players = []
    for name in player_names:
        player = get_player_by_name(db, name=name)
        if not player:
            player = create_player(db, name=name)
        players.append(player)
    
    db_game = models.Game(course_name=course_name, players=players, number_of_holes=number_of_holes)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

def get_game(db: Session, game_id: int):
    return db.query(models.Game).filter(models.Game.id == game_id).first()

def update_game(db: Session, game_id: int, **kwargs):
    db_game = get_game(db, game_id)
    if db_game:
        for key, value in kwargs.items():
            setattr(db_game, key, value)
        db.commit()
        db.refresh(db_game)
    return db_game

def get_game_progress(db: Session, game_id: int):
    game = get_game(db, game_id)
    if not game:
        return None
    return {
        "game_id": game.id,
        "course_name": game.course_name,
        "current_hole": game.current_hole,
        "number_of_holes": game.number_of_holes,
        "is_completed": bool(game.is_completed),
        "players": [{"id": p.id, "name": p.name} for p in game.players]
    }

# Score CRUD
def record_score(db: Session, game_id: int, player_id: int, hole_number: int, strokes: int):
    existing_score = db.query(models.Score).filter(
        models.Score.game_id == game_id,
        models.Score.player_id == player_id,
        models.Score.hole_number == hole_number
    ).first()
    
    if existing_score:
        existing_score.strokes = strokes
        db.commit()
        db.refresh(existing_score)
        return existing_score
    
    db_score = models.Score(game_id=game_id, player_id=player_id, hole_number=hole_number, strokes=strokes)
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score

def get_game_scores(db: Session, game_id: int):
    return db.query(models.Score).filter(models.Score.game_id == game_id).all()

def get_hole_scores(db: Session, game_id: int, hole_number: int):
    return db.query(models.Score).filter(
        models.Score.game_id == game_id,
        models.Score.hole_number == hole_number
    ).all()

def get_player_total_score(db: Session, game_id: int, player_id: int):
    scores = db.query(models.Score).filter(
        models.Score.game_id == game_id,
        models.Score.player_id == player_id
    ).all()
    return sum(s.strokes for s in scores)

def get_game_leaderboard(db: Session, game_id: int):
    game = get_game(db, game_id)
    if not game:
        return []
    
    leaderboard = []
    for player in game.players:
        total = get_player_total_score(db, game_id, player.id)
        leaderboard.append({"player_id": player.id, "name": player.name, "total_score": total})
    
    leaderboard.sort(key=lambda x: x["total_score"])
    return leaderboard