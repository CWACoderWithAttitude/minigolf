import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from minigolf_app import crud
from minigolf_app.database import Base

# Setup for in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pytest fixture to set up and tear down the database for each test function
@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    yield db_session
    db_session.close()
    Base.metadata.drop_all(bind=engine)

def test_create_and_get_player(db):
    """Tests creating and retrieving a player."""
    crud.create_player(db, name="Alice")
    player = crud.get_player_by_name(db, name="Alice")
    assert player is not None
    assert player.name == "Alice"

def test_create_game(db):
    """Tests creating a game with players."""
    player_names = ["Bob", "Charlie"]
    game = crud.create_game(db, course_name="Lighthouse Point", player_names=player_names)
    
    assert game.course_name == "Lighthouse Point"
    assert len(game.players) == 2
    
    db_bob = crud.get_player_by_name(db, "Bob")
    db_charlie = crud.get_player_by_name(db, "Charlie")
    
    assert db_bob is not None
    assert db_charlie is not None
    assert db_bob in game.players
    assert db_charlie in game.players

def test_record_and_get_scores(db):
    """Tests recording a score and retrieving it."""
    game = crud.create_game(db, course_name="Windmill Valley", player_names=["Dave"])
    player = crud.get_player_by_name(db, "Dave")
    
    crud.record_score(db, game_id=game.id, player_id=player.id, hole_number=1, strokes=3)
    
    scores = crud.get_game_scores(db, game_id=game.id)
    assert len(scores) == 1
    score = scores[0]
    assert score.hole_number == 1
    assert score.strokes == 3
    assert score.player_id == player.id
    assert score.game_id == game.id

def test_create_game_with_existing_player(db):
    """Tests that creating a game reuses existing players."""
    crud.create_player(db, name="Eve")
    eve = crud.get_player_by_name(db, "Eve")
    
    game = crud.create_game(db, course_name="Fantasy Island", player_names=["Eve", "Frank"])
    
    assert len(game.players) == 2
    
    # Check that Eve was reused and not recreated
    all_players = crud.get_players(db)
    assert len(all_players) == 2 # Eve and Frank
    
    db_eve = crud.get_player_by_name(db, "Eve")
    assert db_eve.id == eve.id