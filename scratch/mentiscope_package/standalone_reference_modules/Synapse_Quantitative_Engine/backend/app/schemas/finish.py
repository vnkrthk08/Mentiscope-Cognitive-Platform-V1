from pydantic import BaseModel


class FinishRequest(BaseModel):

    session_id: str