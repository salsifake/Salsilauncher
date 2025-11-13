from pydantic import BaseModel, Field


class AvaliacaoDetalhada(BaseModel):
    gameplay: int = Field(default=0, ge=0, le=3)
    graficos: int = Field(default=0, ge=0, le=2)
    historia: int = Field(default=0, ge=0, le=2)
    audio: int = Field(default=0, ge=0, le=2)
    inovacao: int = Field(default=0, ge=0, le=1)
    bonus: int = Field(default=0, ge=0, le=1)
