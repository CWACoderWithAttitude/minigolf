from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

game_players = Table(
    'game_players', Base.metadata,
    Column('game_id', ForeignKey('games.id'), primary_key=True),
    Column('player_id', ForeignKey('players.id'), primary_key=True)
)

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String)
    number_of_holes = Column(Integer, default=18)

    players = relationship("Player", secondary=game_players, back_populates="games")
    scores = relationship("Score", back_populates="game")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    games = relationship("Game", secondary=game_players, back_populates="players")
    scores = relationship("Score", back_populates="player")

class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    hole_number = Column(Integer, nullable=False)
    strokes = Column(Integer, nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)

    player = relationship("Player", back_populates="scores")
    game = relationship("Game", back_populates="scores")