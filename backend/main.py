import os
from fastapi import Depends, FastAPI, Body, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from Salsilauncher.backend.schemas.colecao import ColecaoCreate, ColecaoJogosUpdate
from pathlib import Path
from backend.utils.image_processing import save_webp_image, validate_image_upload
from backend.data.paths import get_capa_path, get_fundo_path, get_extra_image_path
from backend.config.settings import get_settings
from backend.core.exceptions import http_exception_handler, unhandled_exception_handler
from backend.core.logging import logger
from backend.schemas.jogo import JogoCreate, JogoUpdate, JogoRead
from backend.utils.scan_validation import validar_scan_path
from backend.db.init_db import init_db
from sqlmodel import Session, select
from backend.db.session import get_session
from backend.db.models.colecao import Colecao
from backend.db.models.jogo import Jogo
from backend.db.repositories.jogo_repository import (
    listar_jogos as repo_listar_jogos,
    buscar_jogos_por_tags as repo_buscar_jogos_por_tags,
    obter_jogo_por_id as repo_obter_jogo_por_id,
    criar_jogo as repo_criar_jogo, 
    atualizar_jogo as repo_atualizar_jogo,
    remover_jogo as repo_remover_jogo,
    jogos_aleatorios as repo_jogos_aleatorios
)


# Inicialização do FastAPI
app = FastAPI(title="Salsilauncher API")

settings = get_settings()

# Inicialização do banco de dados
@app.on_event("startup")
def on_startup():
    init_db()

# Configuração dos manipuladores de exceção
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings["ALLOWED_ORIGINS"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Diretório de mídia (bootstrap) ---
settings["MIDIA_DIR"].mkdir(parents=True, exist_ok=True)

app.mount(
    "/midia_launcher",
    StaticFiles(directory=settings["MIDIA_DIR"]),
    name="midia",
)


#  --- ENDPOINTS DA API ---


@app.get("/jogos/aleatorio", response_model=List[JogoRead])
def listar_jogos_aleatorios(
    tags: Optional[str] = Query(None, description="Tags separadas por vírgula"),
    limit: int = Query(5, ge=1, le=100),
    session: Session = Depends(get_session)
):
    """
    Retorna até 5 jogos aleatórios, aplicando filtro por tags se fornecido
    """
    logger.info("GET /jogos/aleatorio chamado (tags=%s)", tags)

    jogos = repo_jogos_aleatorios(session, limit=limit)

    # Filtragem por tags
    if tags:
        tags_requisitadas = {t.strip().lower() for t in tags.split(",")}
        jogos = [
            jogo for jogo in jogos
            if tags_requisitadas.issubset(
                {t.lower() for t in jogo.tags}
            )
        ]

    # Seleção aleatória
    if not jogos:
        logger.warning("Nenhum jogo encontrado para seleção aleatória")
        return []

    return jogos




@app.get("/jogos", response_model=List[JogoRead])
def listar_jogos(
    q: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    logger.info("GET /jogos chamado (q=%s, tags=%s)", q, tags)

    jogos = repo_listar_jogos(
        session,
        offset=offset,
        limit=limit
    )

    # filtro por tags
    if tags:
        tags_requisitadas = {t.strip().lower() for t in tags.split(",")}
        jogos = [
            jogo for jogo in jogos
            if tags_requisitadas.issubset(
                {t.lower() for t in jogo.tags}
            )
        ]

    # filtro por texto
    if q:
        q_lower = q.lower()
        jogos = [
            jogo for jogo in jogos
            if q_lower in jogo.nome.lower()
            or (jogo.descricao and q_lower in jogo.descricao.lower())
        ]

    return jogos




@app.post("/scan")
def escanear_pasta_por_jogos(
    caminho: str = Body(..., embed=True),
    session: Session = Depends(get_session)
):
    """
    Varre um diretório em busca de novas pastas contendo executáveis .exe.
    Cria jogos automaticamente para qualquer pasta nova detectada.
    """
    logger.info("POST /scan chamado (caminho=%s)", caminho)
    
    scan_path = Path(caminho)
    validar_scan_path(scan_path)

    jogos = repo_listar_jogos(session, offset=0, limit=10_000)
    pastas_existentes = {j.caminho_pasta for j in jogos}
    novos = []

    # Descobrir novas pastas
    def descobrir_pastas_validas():
        for nome in os.listdir(caminho):
            pasta = os.path.join(caminho, nome)
            if os.path.isdir(pasta) and pasta not in pastas_existentes:
                yield pasta

    # Encontrar executável na pasta
    def encontrar_executavel(pasta):
        for root, _, files in os.walk(pasta):
            for f in files:
                if f.lower().endswith(".exe"):
                    return os.path.join(root, f)
        return None

    # Criar o objeto Jogo a partir da pasta
    def criar_jogo_para_pasta(pasta, executavel):
        nome = os.path.basename(pasta)
        return Jogo(
            nome=nome,
            caminho_executavel=executavel,
            caminho_pasta=pasta
        )

    # Processar pastas novas
    for pasta in descobrir_pastas_validas():
        exe = encontrar_executavel(pasta)
        if not exe:
            logger.warning("Pasta ignorada (sem executável): %s", pasta)
            continue  # ignorar pastas sem executável
        jogo = criar_jogo_para_pasta(pasta, exe)
        criado = repo_criar_jogo(session, jogo)
        novos.append(criado)

    # salvar se mudou
    if novos:
        logger.info("%d novos jogos adicionados via scan", len(novos))

    return {
        "status": f"{len(novos)} jogos adicionados.",
        "adicionados": [j.id for j in novos],
        "total_biblioteca": len(jogos) + len(novos)
    }



@app.post("/jogos/{jogo_id}/capa", status_code=200)
async def upload_capa_jogo(
    jogo_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    logger.info("Upload de capa iniciado (jogo_id=%d)", jogo_id)
    validate_image_upload(file)

    jogo = repo_obter_jogo_por_id(session, jogo_id)

    if not jogo:
        logger.warning("Tentativa de upload de capa para jogo inexistente (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Caminho unificado da capa
    path_capa = get_capa_path(jogo_id)

    try:
        saved_path = save_webp_image(file.file, path_capa)
    except Exception as e:
        logger.error("Erro ao salvar capa do jogo %d: %s", jogo_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")

    jogo.capa = saved_path.replace("\\", "/")
    repo_atualizar_jogo(session, jogo)

    return {
        "status": "Capa atualizada com sucesso!",
        "caminho_imagem": jogo.capa
    }



@app.post("/jogos/{jogo_id}/fundo", status_code=200)
async def upload_fundo_jogo(
    jogo_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    logger.info("Upload de fundo iniciado (jogo_id=%d)", jogo_id)
    validate_image_upload(file)

    jogo = repo_obter_jogo_por_id(session, jogo_id)

    if not jogo:
        logger.warning("Tentativa de upload de fundo para jogo inexistente (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    caminho_fundo = get_fundo_path(jogo_id)

    try:
        saved_path = save_webp_image(file.file, caminho_fundo, size=(1920, 1080))
    except Exception as e:
        logger.error("Erro ao salvar fundo do jogo %d: %s", jogo_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")

    jogo.fundo = saved_path.replace("\\", "/")
    repo_atualizar_jogo(session, jogo)

    return {
        "status": "Imagem de fundo atualizada!",
        "caminho_imagem": jogo.fundo
    }



@app.post("/jogos/{jogo_id}/extras", status_code=200)
async def upload_imagens_extras(
    jogo_id: int,
    files: List[UploadFile] = File(...),
    session: Session = Depends(get_session)
):
    logger.info("Upload de imagens extras iniciado (jogo_id=%d, arquivos=%d)", jogo_id, len(files))

    jogo = repo_obter_jogo_por_id(session, jogo_id)

    if not jogo:
        logger.warning("Tentativa de upload de extras para jogo inexistente (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    novos_caminhos = []

    try:
        start_index = len(jogo.imagens_extras)

        for i, file in enumerate(files):
            validate_image_upload(file)
            output_path = get_extra_image_path(jogo_id, start_index + i)
            saved = save_webp_image(file.file, output_path, size=(1280, 720))
            saved = saved.replace("\\", "/")
            novos_caminhos.append(saved)
            jogo.imagens_extras.append(saved)

        repo_atualizar_jogo(session, jogo)

    except Exception as e:
        logger.error("Erro ao salvar imagens extras do jogo %d: %s", jogo_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao salvar imagens extras: {e}")

    return {
        "status": "Imagens extras adicionadas!",
        "arquivos_salvos": novos_caminhos
    }



@app.get("/jogos/{jogo_id}", response_model=JogoRead)
def obter_detalhes_do_jogo(
    jogo_id: int,
    session: Session = Depends(get_session)
):
    logger.info("GET /jogos/%d chamado", jogo_id)

    jogo = repo_obter_jogo_por_id(session, jogo_id)

    if not jogo:
        logger.warning("Jogo não encontrado (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    return jogo



@app.get("/colecoes", response_model=List[Colecao])
def listar_colecoes(
    session: Session = Depends(get_session)
):
    """
    Carrega e retorna a lista de coleções do banco de dados
    """
    logger.info("GET /colecoes chamado")

    return session.exec(select(Colecao)).all()


@app.post("/colecoes", response_model=Colecao, status_code=201)
def criar_colecao(
    colecao: ColecaoCreate,
    session: Session = Depends(get_session)
):
    logger.info("POST /colecoes chamado (nome=%s)", colecao.nome)

    nova_colecao = Colecao(
        nome=colecao.nome
    )

    session.add(nova_colecao)
    session.commit()
    session.refresh(nova_colecao)

    return nova_colecao


@app.get("/colecoes/{colecao_id}/jogos", response_model=List[JogoRead])
def listar_jogos_da_colecao(
    colecao_id: int,
    session: Session = Depends(get_session)
):
    """
    Retorna todos os jogos que pertencem a uma coleção específica
    """
    logger.info("GET /colecoes/%s/jogos chamado", colecao_id)

    colecao = session.get(Colecao, colecao_id)

    if not colecao:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")

    return colecao.jogos

@app.post("/colecoes/{colecao_id}/jogos", status_code=200)
def adicionar_jogos_a_colecao(
    colecao_id: int,
    payload: ColecaoJogosUpdate,
    session: Session = Depends(get_session)
):
    """
    Associa jogos existentes a uma coleção
    """
    logger.info(
        "POST /colecoes/%d/jogos chamado (quantidade=%d)",
        colecao_id,
        len(payload.jogos)
    )

    colecao = session.get(Colecao, colecao_id)
    if not colecao:
        raise HTTPException(status_code=404, detail="Coleção não encontrada")

    # Jogos já associados (para evitar duplicação)
    jogos_existentes = {j.id for j in colecao.jogos}

    for jogo_id in payload.jogos:
        jogo = session.get(Jogo, jogo_id)
        if not jogo:
            logger.warning(
                "Jogo inexistente ignorado na associação (id=%d)",
                jogo_id
            )
            continue

        if jogo.id not in jogos_existentes:
            colecao.jogos.append(jogo)

    session.commit()
    session.refresh(colecao)

    return {
        "status": "Jogos associados com sucesso",
        "colecao_id": colecao.id,
        "total_jogos": len(colecao.jogos)
    }



@app.get("/tags", response_model=List[str])
def listar_tags_unicas(session: Session = Depends(get_session)):
    """
    Retorna uma lista de todas as tags únicas de todos os jogos
    """
    logger.info("GET /tags chamado")

    jogos = session.exec(select(Jogo)).all()

    todas_as_tags = set()

    for jogo in jogos:
        for tag in jogo.tags:
            todas_as_tags.add(tag)

    return sorted(list(todas_as_tags))



@app.post("/jogos", response_model=JogoRead, status_code=201)
def criar_jogo(
    jogo: JogoCreate,
    session: Session = Depends(get_session)
):
    """
    Cria um novo jogo e salva no banco
    """
    logger.info("POST /jogos chamado (nome=%s)", jogo.nome)

    novo_jogo = Jogo.model_validate(jogo)
    return repo_criar_jogo(session, novo_jogo) 


@app.put("/jogos/{jogo_id}", response_model=JogoRead)
def atualizar_jogo(
    jogo_id: int,
    dados: JogoUpdate,
    session: Session = Depends(get_session)
):
    logger.info("PUT /jogos/%d chamado", jogo_id)

    jogo = repo_obter_jogo_por_id(session, jogo_id)
    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    dados_dict = dados.model_dump(exclude_unset=True)
    for campo, valor in dados_dict.items():
        setattr(jogo, campo, valor)

    atualizado = repo_atualizar_jogo(session, jogo)
    return atualizado



@app.delete("/jogos/{jogo_id}", status_code=204)
def remover_jogo(jogo_id: int, session: Session = Depends(get_session)):
    """Remove um jogo do banco de dados."""
    logger.info("DELETE /jogos/%d chamado", jogo_id)

    jogo = repo_obter_jogo_por_id(session, jogo_id)
    if not jogo:
        logger.warning("Tentativa de remover jogo inexistente (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    repo_remover_jogo(session, jogo)
    return  # Retorna uma resposta vazia com status 204 No Content