import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from crud import (
    create_player, get_player_by_name, get_players,
    create_game, get_game, update_game, record_score,
    get_game_scores, get_hole_scores, get_player_total_score, get_game_leaderboard
)
from database import Base

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
    create_player(db, name="Alice")
    player = get_player_by_name(db, name="Alice")
    assert player is not None
    assert player.name == "Alice"

def test_create_game(db):
    """Tests creating a game with players."""
    player_names = ["Bob", "Charlie"]
    game = create_game(db, course_name="Lighthouse Point", player_names=player_names)
    
    assert game.course_name == "Lighthouse Point"
    assert len(game.players) == 2
    
    db_bob = get_player_by_name(db, "Bob")
    db_charlie = get_player_by_name(db, "Charlie")
    
    assert db_bob is not None
    assert db_charlie is not None
    assert db_bob in game.players
    assert db_charlie in game.players

def test_record_and_get_scores(db):
    """Tests recording a score and retrieving it."""
    game = create_game(db, course_name="Windmill Valley", player_names=["Dave"])
    player = get_player_by_name(db, "Dave")
    
    record_score(db, game_id=game.id, player_id=player.id, hole_number=1, strokes=3)
    
    scores = get_game_scores(db, game_id=game.id)
    assert len(scores) == 1
    score = scores[0]
    assert score.hole_number == 1
    assert score.strokes == 3
    assert score.player_id == player.id
    assert score.game_id == game.id

def test_create_game_with_existing_player(db):
    """Tests that creating a game reuses existing players."""
    create_player(db, name="Eve")
    eve = get_player_by_name(db, "Eve")
    
    game = create_game(db, course_name="Fantasy Island", player_names=["Eve", "Frank"])
    
    assert len(game.players) == 2
    
    # Check that Eve was reused and not recreated
    all_players = get_players(db)
    assert len(all_players) == 2 # Eve and Frank
    
    db_eve = get_player_by_name(db, "Eve")
    assert db_eve.id == eve.id

def test_game_state_fields(db):
    """Tests that game has current_hole and is_completed fields."""
    game = create_game(db, course_name="State Test", player_names=["Alice"])
    
    assert game.current_hole == 1
    assert game.is_completed == 0

def test_update_game_state(db):
    """Tests updating game state (current_hole and is_completed)."""
    game = create_game(db, course_name="Update Test", player_names=["Bob"])
    
    updated = update_game(db, game.id, current_hole=5, is_completed=0)
    assert updated.current_hole == 5
    assert updated.is_completed == 0
    
    updated = update_game(db, game.id, is_completed=1)
    assert updated.is_completed == 1

def test_update_score(db):
    """Tests updating an existing score (editing)."""
    game = create_game(db, course_name="Edit Test", player_names=["Charlie"])
    player = get_player_by_name(db, "Charlie")
    
    # Record initial score
    record_score(db, game.id, player.id, 1, 4)
    scores = get_hole_scores(db, game.id, 1)
    assert len(scores) == 1
    assert scores[0].strokes == 4
    
    # Update the score
    record_score(db, game.id, player.id, 1, 5)
    scores = get_hole_scores(db, game.id, 1)
    assert len(scores) == 1
    assert scores[0].strokes == 5

def test_get_hole_scores(db):
    """Tests getting all scores for a specific hole."""
    game = create_game(db, course_name="Hole Score Test", player_names=["Alice", "Bob"])
    alice = get_player_by_name(db, "Alice")
    bob = get_player_by_name(db, "Bob")
    
    record_score(db, game.id, alice.id, 1, 3)
    record_score(db, game.id, bob.id, 1, 4)
    record_score(db, game.id, alice.id, 2, 5)
    
    hole_1_scores = get_hole_scores(db, game.id, 1)
    assert len(hole_1_scores) == 2
    
    hole_2_scores = get_hole_scores(db, game.id, 2)
    assert len(hole_2_scores) == 1

def test_get_player_total_score(db):
    """Tests calculating a player's total score."""
    game = create_game(db, course_name="Total Score Test", player_names=["Dave"])
    player = get_player_by_name(db, "Dave")
    
    record_score(db, game.id, player.id, 1, 3)
    record_score(db, game.id, player.id, 2, 4)
    record_score(db, game.id, player.id, 3, 5)
    
    total = get_player_total_score(db, game.id, player.id)
    assert total == 12

def test_get_game_leaderboard(db):
    """Tests generating a sorted leaderboard."""
    game = create_game(db, course_name="Leaderboard Test", player_names=["Alice", "Bob", "Charlie"])
    alice = get_player_by_name(db, "Alice")
    bob = get_player_by_name(db, "Bob")
    charlie = get_player_by_name(db, "Charlie")
    
    # Alice: 3 + 4 = 7
    record_score(db, game.id, alice.id, 1, 3)
    record_score(db, game.id, alice.id, 2, 4)
    
    # Bob: 4 + 5 = 9
    record_score(db, game.id, bob.id, 1, 4)
    record_score(db, game.id, bob.id, 2, 5)
    
    # Charlie: 5 + 3 = 8
    record_score(db, game.id, charlie.id, 1, 5)
    record_score(db, game.id, charlie.id, 2, 3)
    
    leaderboard = get_game_leaderboard(db, game.id)
    
    assert len(leaderboard) == 3
    assert leaderboard[0]["name"] == "Alice"
    assert leaderboard[0]["total_score"] == 7
    assert leaderboard[1]["name"] == "Charlie"
    assert leaderboard[1]["total_score"] == 8
    assert leaderboard[2]["name"] == "Bob"
    assert leaderboard[2]["total_score"] == 9

def test_game_with_custom_hole_count(db):
    """Tests creating a game with custom hole count."""
    game = create_game(db, course_name="9 Holes", player_names=["Eve"], number_of_holes=9)
    assert game.number_of_holes == 9
    
    game2 = create_game(db, course_name="27 Holes", player_names=["Frank"], number_of_holes=27)
    assert game2.number_of_holes == 27