import pytest
from backend.db.models.jogo import Jogo


@pytest.fixture
def jogo_base(session):
    """
    Jogo mínimo válido no banco
    """
    jogo = Jogo(
        nome="Jogo de Teste",
        descricao="Descrição de teste",
        caminho_executavel="C:/jogos/teste/game.exe",
        caminho_pasta="C:/jogos/teste",
        tags=["acao", "indie"]
    )

    session.add(jogo)
    session.commit()
    session.refresh(jogo)

    return jogo

@pytest.fixture
def varios_jogos(session):
    jogos = []

    for i in range(5):
        jogo = Jogo(
            nome=f"Jogo {i}",
            descricao=f"Descricao {i}",
            caminho_executavel=f"C:/jogos/jogo{i}/game.exe",
            caminho_pasta=f"C:/jogos/jogo{i}",
            tags=["acao"] if i % 2 == 0 else ["rpg"]
        )
        jogos.append(jogo)

    session.add_all(jogos)
    session.commit()

    return jogos
