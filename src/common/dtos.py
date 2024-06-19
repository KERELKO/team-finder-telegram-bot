from dataclasses import dataclass


@dataclass
class UserDTO:
    id: int = 0
    game: str = ''
    username: str = ''
    skill: str = ''
    language: str = ''
