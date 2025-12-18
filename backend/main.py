# backend/main.py

import os
import json, shutil, tempfile
from fastapi import FastAPI, Body, HTTPException, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
from PIL import Image
import random
from backend.data.storage import salvar_jogos, carregar_jogos, salvar_colecoes, carregar_colecoes
from pathlib import Path
from backend.models.Jogo import Jogo
from backend.models.Colecao import Colecao
from backend.models.AvaliacaoDetalhada import AvaliacaoDetalhada
from backend.models.Links import Link
from backend.utils.image_processing import save_webp_image
from backend.data.paths import get_capa_path, get_fundo_path, get_extra_image_path
from backend.config.settings import get_settings
from backend.core.exceptions import http_exception_handler, unhandled_exception_handler
from backend.core.logging import logger
from backend.schemas.jogo import JogoCreate, JogoUpdate, JogoRead



# Inicialização do FastAPI
app = FastAPI(title="Salsilauncher API")
DB_FILE = "jogos_db.json"

settings = get_settings()

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
def listar_jogos_aleatorios(tags: Optional[str] = Query(None, description="Tags separadas por vírgula")):
    """
    Retorna até 5 jogos aleatórios, aplicando filtro por tags se fornecido
    """
    logger.info("GET /jogos/aleatorio chamado (tags=%s)", tags)

    jogos = carregar_jogos()

    # Filtragem por tags
    if tags:
        tags_requisitadas = {t.strip().lower() for t in tags.split(",")}
        jogos = [
            jogo for jogo in jogos
            if tags_requisitadas.issubset(
                {t.lower() for t in jogo.get("tags", [])}
            )
        ]

    # Seleção aleatória
    if not jogos:
        logger.warning("Nenhum jogo encontrado para seleção aleatória")
        return []

    quantidade = min(5, len(jogos))
    return random.sample(jogos, quantidade)


@app.get("/jogos", response_model=List[JogoRead])
def listar_jogos(q: Optional[str] = None, tags: Optional[str] = None):
    logger.info("GET /jogos chamado (q=%s, tags=%s)", q, tags)

    jogos = carregar_jogos()

    # filtro por tags
    if tags:
        tags_requisitadas = {t.strip().lower() for t in tags.split(",")}
        jogos = [
            jogo for jogo in jogos
            if tags_requisitadas.issubset({t.lower() for t in jogo["tags"]})
        ]

    # busca por texto com prioridade
    if q:
        termo = q.lower()
        resultados = []

        for jogo in jogos:
            score = 0

            if termo in jogo["nome"].lower():
                score += 5
            if any(termo in t.lower() for t in jogo.get("tags", [])):
                score += 3
            if jogo.get("desenvolvedor") and termo in jogo["desenvolvedor"].lower():
                score += 2
            if jogo.get("studio") and termo in jogo["studio"].lower():
                score += 1
            if jogo.get("descricao") and termo in jogo.get("descricao", "").lower():
                score += 1
            if any(termo in link["nome"].lower() for link in jogo.get("links", [])):
                score += 1

            if score > 0:
                resultados.append((jogo, score))

        resultados.sort(key=lambda x: x[1], reverse=True)
        logger.info("Busca retornou %d resultados", len(resultados))
        return [j for j, _ in resultados]

    return jogos


@app.post("/scan")
def escanear_pasta_por_jogos(caminho: str = Body(..., embed=True)):
    """
    Varre um diretório em busca de novas pastas contendo executáveis .exe.
    Cria jogos automaticamente para qualquer pasta nova detectada.
    """
    logger.info("POST /scan chamado (caminho=%s)", caminho)

    if not os.path.isdir(caminho):
        logger.error("Caminho inválido informado no scan: %s", caminho)
        raise HTTPException(status_code=400, detail="Caminho inválido ou inexistente.")

    jogos = carregar_jogos()
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
    def criar_jogo_para_pasta(pasta, executavel, jogos):
        novo_id = max((j["id"] for j in jogos), default=0) + 1
        nome = os.path.basename(pasta)
        return Jogo(
            id=novo_id,
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
        jogo = criar_jogo_para_pasta(pasta, exe, jogos)
        jogos.append(jogo)
        novos.append(jogo)

    # salvar se mudou
    if novos:
        salvar_jogos(jogos)
        logger.info("%d novos jogos adicionados via scan", len(novos))

    return {
        "status": f"{len(novos)} jogos adicionados.",
        "adicionados": [j["id"] for j in novos],
        "total_biblioteca": len(jogos)
    }


@app.post("/jogos/{jogo_id}/capa", status_code=200)
async def upload_capa_jogo(jogo_id: int, file: UploadFile = File(...)):
    logger.info("Upload de capa iniciado (jogo_id=%d)", jogo_id)

    jogos = carregar_jogos()
    jogo = next((j for j in jogos if j["id"] == jogo_id), None)

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

    jogo.imagem_capa = saved_path.replace("\\", "/")
    salvar_jogos(jogos)

    return {
        "status": "Capa atualizada com sucesso!",
        "caminho_imagem": jogo.imagem_capa
    }


@app.post("/jogos/{jogo_id}/fundo", status_code=200)
async def upload_fundo_jogo(jogo_id: int, file: UploadFile = File(...)):
    logger.info("Upload de fundo iniciado (jogo_id=%d)", jogo_id)

    jogos = carregar_jogos()
    jogo = next((j for j in jogos if j["id"] == jogo_id), None)

    if not jogo:
        logger.warning("Tentativa de upload de fundo para jogo inexistente (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    caminho_fundo = get_fundo_path(jogo_id)

    try:
        saved_path = save_webp_image(file.file, caminho_fundo, size=(1920, 1080))
    except Exception as e:
        logger.error("Erro ao salvar fundo do jogo %d: %s", jogo_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")

    jogo.imagem_fundo = saved_path.replace("\\", "/")
    salvar_jogos(jogos)

    return {
        "status": "Imagem de fundo atualizada!",
        "caminho_imagem": jogo.imagem_fundo
    }


@app.post("/jogos/{jogo_id}/extras", status_code=200)
async def upload_imagens_extras(
    jogo_id: int,
    files: List[UploadFile] = File(...)
):
    logger.info("Upload de imagens extras iniciado (jogo_id=%d, arquivos=%d)", jogo_id, len(files))

    jogos = carregar_jogos()
    jogo = next((j for j in jogos if j["id"] == jogo_id), None)

    if not jogo:
        logger.warning("Tentativa de upload de extras para jogo inexistente (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    novos_caminhos = []

    try:
        start_index = len(jogo.imagens_extras)

        for i, file in enumerate(files):
            output_path = get_extra_image_path(jogo_id, start_index + i)
            saved = save_webp_image(file.file, output_path, size=(1280, 720))
            saved = saved.replace("\\", "/")
            novos_caminhos.append(saved)
            jogo.imagens_extras.append(saved)

        salvar_jogos(jogos)

    except Exception as e:
        logger.error("Erro ao salvar imagens extras do jogo %d: %s", jogo_id, e)
        raise HTTPException(status_code=500, detail=f"Erro ao salvar imagens extras: {e}")

    return {
        "status": "Imagens extras adicionadas!",
        "arquivos_salvos": novos_caminhos
    }


@app.get("/jogos/{jogo_id}", response_model=JogoRead)
def obter_detalhes_do_jogo(jogo_id: int):
    logger.info("GET /jogos/%d chamado", jogo_id)

    jogos = carregar_jogos()
    jogo_encontrado = next((j for j in jogos if j["id"] == jogo_id), None)

    if not jogo_encontrado:
        logger.warning("Jogo não encontrado (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    return jogo_encontrado


@app.get("/colecoes", response_model=List[Colecao])
def listar_colecoes():
    """
    Carrega e retorna a lista de coleções do banco de dados
    """
    logger.info("GET /colecoes chamado")
    return carregar_colecoes()


@app.post("/colecoes", response_model=Colecao, status_code=201)
def criar_colecao(colecao: Colecao):
    """
    Cria uma nova coleção e garante que o ID seja único e salva no banco
    """
    logger.info("POST /colecoes chamado (id=%s)", colecao.id)

    colecoes = carregar_colecoes()

    # Verificação de ID duplicado
    if any(c.id == colecao.id for c in colecoes):
        logger.warning("Tentativa de criar coleção duplicada (id=%s)", colecao.id)
        raise HTTPException(
            status_code=400,
            detail="Uma coleção com este ID já existe."
        )

    colecoes.append(colecao)
    salvar_colecoes(colecoes)

    return colecao


@app.get("/colecoes/{colecao_id}/jogos", response_model=List[JogoRead])
def listar_jogos_da_colecao(colecao_id: str):
    """
    Retorna todos os jogos que pertencem a uma coleção específica
    """
    logger.info("GET /colecoes/%s/jogos chamado", colecao_id)

    todos_jogos = carregar_jogos()
    jogos_na_colecao = [
        jogo for jogo in todos_jogos if colecao_id in jogo["colecoes"]
    ]
    return jogos_na_colecao


@app.get("/tags", response_model=List[str])
def listar_tags_unicas():
    """
    Retorna uma lista de todas as tags únicas de todos os jogos
    """
    logger.info("GET /tags chamado")

    jogos = carregar_jogos()
    todas_as_tags = set()
    for jogo in jogos:
        for tag in jogo["tags"]:
            todas_as_tags.add(tag)
    return sorted(list(todas_as_tags))


@app.post("/jogos", response_model=JogoRead, status_code=201)
def criar_novo_jogo(jogo_dados: JogoCreate):
    """Cria uma nova entrada de jogo no banco de dados."""
    logger.info("POST /jogos chamado (nome=%s)", jogo_dados.nome)

    jogos = carregar_jogos()

    novo_id = max((j["id"] for j in jogos), default=0) + 1

    jogo_dict = jogo_dados.model_dump()
    jogo_dict["id"] = novo_id
    jogo_dict["imagem_capa"] = None
    jogo_dict["imagem_fundo"] = None
    jogo_dict["imagens_extras"] = []

    jogos.append(jogo_dict)
    salvar_jogos(jogos)
    return jogo_dict


@app.put("/jogos/{jogo_id}", response_model=JogoRead)
def atualizar_jogo(jogo_id: int, jogo_atualizado: JogoUpdate):
    """Atualiza os dados de um jogo existente."""
    logger.info("PUT /jogos/%d chamado", jogo_id)

    jogos = carregar_jogos()
    index = next((i for i, j in enumerate(jogos) if j["id"] == jogo_id), -1)

    if index == -1:
        logger.warning("Tentativa de atualizar jogo inexistente (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    dados_atualizados = jogo_atualizado.model_dump(exclude_unset=True)

    for campo, valor in dados_atualizados.items():
        jogos[index][campo] = valor

    salvar_jogos(jogos)
    return jogos[index]


@app.delete("/jogos/{jogo_id}", status_code=204)
def remover_jogo(jogo_id: int):
    """Remove um jogo do banco de dados."""
    logger.info("DELETE /jogos/%d chamado", jogo_id)

    jogos = carregar_jogos()
    jogos_filtrados = [j for j in jogos if j["id"] != jogo_id]

    if len(jogos_filtrados) == len(jogos):
        logger.warning("Tentativa de remover jogo inexistente (id=%d)", jogo_id)
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    salvar_jogos(jogos_filtrados)
    return  # Retorna uma resposta vazia com status 204 No Content