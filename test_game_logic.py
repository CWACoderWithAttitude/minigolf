import pytest
from minigolf_app.game_logic.models import Player, Game

def test_player_total_score():
    """Tests that the player's total score is calculated correctly."""
    player = Player(name="Alice", scores=[3, 4, 2, 5])
    assert player.total_score == 14

def test_add_player_to_game():
    """Tests adding a player to a game."""
    game = Game(players=[], course_name="Lighthouse Point")
    game.add_player("Bob")
    assert len(game.players) == 1
    assert game.players[0].name == "Bob"

def test_add_duplicate_player_raises_error():
    """Tests that adding a duplicate player raises a ValueError."""
    player1 = Player(name="Charlie")
    game = Game(players=[player1], course_name="Windmill Valley")
    with pytest.raises(ValueError):
        game.add_player("Charlie")