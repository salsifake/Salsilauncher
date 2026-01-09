import pytest
from backend.db.models.colecao import Colecao


@pytest.fixture
def colecao_base(session):
    colecao = Colecao(
        nome="Coleção de Teste"
    )

    session.add(colecao)
    session.commit()
    session.refresh(colecao)

    return colecao

@pytest.fixture
def colecao_com_jogos(session, colecao_base, varios_jogos):
    # associa os 3 primeiros jogos
    colecao_base.jogos.extend(varios_jogos[:3])

    session.commit()
    session.refresh(colecao_base)

    return colecao_base
