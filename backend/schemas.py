from pydantic import BaseModel
from typing import Optional

class SetUsernameRequest(BaseModel):
    username: str

class UserSettingsRequest(BaseModel):
    default_time: float
    default_increment: float
    default_time_control_enabled: bool

class NewGameRequest(BaseModel):
    variant: str = "standard"
    fen: Optional[str] = None
    time_control: Optional[dict] = None
    play_as: Optional[str] = "white"
    is_computer: bool = False

class LegalMovesRequest(BaseModel):
    game_id: str
    square: str

class GameRequest(BaseModel):
    game_id: str
