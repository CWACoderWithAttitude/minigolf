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
def create_game(db: Session, course_name: str, player_names: list[str]):
    players = []
    for name in player_names:
        player = get_player_by_name(db, name=name)
        if not player:
            player = create_player(db, name=name)
        players.append(player)
    
    db_game = models.Game(course_name=course_name, players=players)
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game

# Score CRUD
def record_score(db: Session, game_id: int, player_id: int, hole_number: int, strokes: int):
    db_score = models.Score(game_id=game_id, player_id=player_id, hole_number=hole_number, strokes=strokes)
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score

def get_game_scores(db: Session, game_id: int):
    return db.query(models.Score).filter(models.Score.game_id == game_id).all()