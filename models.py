from dataclasses import dataclass, field
from typing import List

@dataclass
class Player:
    """Represents a player in the game."""
    name: str
    scores: List[int] = field(default_factory=list)

    @property
    def total_score(self) -> int:
        return sum(self.scores)

@dataclass
class Game:
    """Represents a single minigolf game."""
    players: List[Player]
    course_name: str
    number_of_holes: int = 18

    def add_player(self, player_name: str):
        """Adds a new player to the game."""
        if any(p.name == player_name for p in self.players):
            raise ValueError(f"Player {player_name} is already in the game.")
        self.players.append(Player(name=player_name))