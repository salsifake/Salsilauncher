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


# Inicialização do FastAPI
app = FastAPI(title="Salsilauncher API")
DB_FILE = "jogos_db.json"

# --- CORS Middleware ---

# ler origens permitidas do .env
origins_env = os.getenv("ALLOWED_ORIGINS", "")
if origins_env.strip():
    allowed_origins = [o.strip() for o in origins_env.split(",")]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração do diretório de mídia
BASE_DIR = Path(__file__).resolve().parent
MIDIA_DIR = BASE_DIR / "midia_launcher"

# cria se estiver faltando
MIDIA_DIR.mkdir(exist_ok=True)

app.mount("/midia_launcher", StaticFiles(directory=MIDIA_DIR), name="midia")

#  --- ENDPOINTS DA API ---

@app.get("/jogos", response_model=List[Jogo])
def listar_jogos(q: Optional[str] = None, tags: Optional[str] = None):
    jogos = carregar_jogos()

    # filtro por tags
    if tags:
        tags_requisitadas = {t.strip().lower() for t in tags.split(",")}
        jogos = [
            jogo for jogo in jogos
            if tags_requisitadas.issubset({t.lower() for t in jogo.tags})
        ]

    # busca por texto com prioridade
    if q:
        termo = q.lower()
        resultados = []

        for jogo in jogos:
            score = 0

            if termo in jogo.nome.lower():
                score += 5
            if any(termo in t.lower() for t in jogo.tags):
                score += 3
            if jogo.desenvolvedor and termo in jogo.desenvolvedor.lower():
                score += 2
            if jogo.studio and termo in jogo.studio.lower():
                score += 1
            if jogo.descricao and termo in jogo.descricao.lower():
                score += 1
            if any(termo in link.nome.lower() for link in jogo.links):
                score += 1

            if score > 0:
                resultados.append((jogo, score))

        resultados.sort(key=lambda x: x[1], reverse=True)
        return [j for j, _ in resultados]
    return jogos


@app.post("/scan")
def escanear_pasta_por_jogos(caminho: str = Body(..., embed=True)):
    """
    Varre um diretório em busca de novas pastas contendo executáveis .exe.
    Cria jogos automaticamente para qualquer pasta nova detectada.
    """
    if not os.path.isdir(caminho):
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
        novo_id = max((j.id for j in jogos), default=0) + 1
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
            continue  # ignorar pastas sem executável
        jogo = criar_jogo_para_pasta(pasta, exe, jogos)
        jogos.append(jogo)
        novos.append(jogo)

    # salvar se mudou
    if novos:
        salvar_jogos(jogos)

    return {
        "status": f"{len(novos)} jogos adicionados.",
        "adicionados": [j.id for j in novos],
        "total_biblioteca": len(jogos)
    }


@app.post("/jogos/{jogo_id}/capa", status_code=200)
async def upload_capa_jogo(jogo_id: int, file: UploadFile = File(...)):
    jogos = carregar_jogos()
    jogo = next((j for j in jogos if j.id == jogo_id), None)

    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Caminho unificado da capa
    path_capa = get_capa_path(jogo_id)

    try:
        saved_path = save_webp_image(file.file, path_capa)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {e}")

    jogo.imagem_capa = saved_path.replace("\\", "/")
    salvar_jogos(jogos)

    return {
        "status": "Capa atualizada com sucesso!",
        "caminho_imagem": jogo.imagem_capa
    }

@app.post("/jogos/{jogo_id}/fundo", status_code=200)
async def upload_fundo_jogo(jogo_id: int, file: UploadFile = File(...)):
    jogos = carregar_jogos()
    jogo = next((j for j in jogos if j.id == jogo_id), None)

    if not jogo:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    caminho_fundo = get_fundo_path(jogo_id)

    try:
        saved_path = save_webp_image(file.file, caminho_fundo, size=(1920, 1080))
    except Exception as e:
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
    jogos = carregar_jogos()
    jogo = next((j for j in jogos if j.id == jogo_id), None)

    if not jogo:
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
        raise HTTPException(status_code=500, detail=f"Erro ao salvar imagens extras: {e}")

    return {
        "status": "Imagens extras adicionadas!",
        "arquivos_salvos": novos_caminhos
    }


@app.get("/jogos/{jogo_id}", response_model=Jogo)
def obter_detalhes_do_jogo(jogo_id: int):
    jogos = carregar_jogos()
    jogo_encontrado = next((j for j in jogos if j.id == jogo_id), None)

    if not jogo_encontrado:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    return jogo_encontrado

@app.get("/colecoes", response_model=List[Colecao])
def listar_colecoes():
    """
    Carrega e retorna a lista de coleções do banco de dados
    """
    return carregar_colecoes()

@app.post("/colecoes", response_model=Colecao, status_code=201)
def criar_colecao(colecao: Colecao):
    """
    Cria uma nova coleção e garante que o ID seja único e salva no banco
    """
    colecoes = carregar_colecoes()

    # Verificação de ID duplicado
    if any(c.id == colecao.id for c in colecoes):
        raise HTTPException(
            status_code=400,
            detail="Uma coleção com este ID já existe."
        )

    colecoes.append(colecao)
    salvar_colecoes(colecoes)

    return colecao


@app.get("/colecoes/{colecao_id}/jogos", response_model=List[Jogo])
def listar_jogos_da_colecao(colecao_id: str):
    """
    Retorna todos os jogos que pertencem a uma coleção específica
    """
    todos_jogos = carregar_jogos()
    jogos_na_colecao = [
        jogo for jogo in todos_jogos if colecao_id in jogo.colecoes
    ]
    return jogos_na_colecao

@app.get("/tags", response_model=List[str])
def listar_tags_unicas():
    """
    Retorna uma lista de todas as tags únicas de todos os jogos
    """
    jogos = carregar_jogos()
    todas_as_tags = set()
    for jogo in jogos:
        for tag in jogo.tags:
            todas_as_tags.add(tag)
    return sorted(list(todas_as_tags))

@app.get("/jogos/aleatorio", response_model=List[Jogo])
def listar_jogos_aleatorios(tags: Optional[str] = None):
    """
    Retorna até 5 jogos aleatórios, aplicando filtro por tags se fornecido
    """
    jogos = carregar_jogos()

    # Filtragem por tags
    if tags:
        tags_requisitadas = set(tags.lower().split(","))
        jogos = [
            jogo for jogo in jogos
            if tags_requisitadas.issubset({t.lower() for t in jogo.tags})
        ]

    # Seleção aleatória
    if not jogos:
        return []

    quantidade = min(5, len(jogos))
    return random.sample(jogos, quantidade)

@app.post("/jogos", response_model=Jogo, status_code=201)
def criar_novo_jogo(jogo_dados: Jogo):
    """Cria uma nova entrada de jogo no banco de dados."""
    jogos = carregar_jogos()
    # Define um novo ID para o jogo
    novo_id = max([j.id for j in jogos], default=0) + 1
    jogo_dados.id = novo_id

    jogos.append(jogo_dados)
    salvar_jogos(jogos)
    return jogo_dados

@app.put("/jogos/{jogo_id}", response_model=Jogo)
def atualizar_jogo(jogo_id: int, jogo_atualizado: Jogo):
    """Atualiza os dados de um jogo existente."""
    jogos = carregar_jogos()
    index_do_jogo = next((i for i, j in enumerate(jogos) if j.id == jogo_id), -1)

    if index_do_jogo == -1:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Garante que o ID não seja alterado
    jogo_atualizado.id = jogo_id
    jogos[index_do_jogo] = jogo_atualizado
    salvar_jogos(jogos)
    return jogo_atualizado

@app.delete("/jogos/{jogo_id}", status_code=204)
def remover_jogo(jogo_id: int):
    """Remove um jogo do banco de dados."""
    jogos = carregar_jogos()
    jogos_filtrados = [j for j in jogos if j.id != jogo_id]

    if len(jogos_filtrados) == len(jogos):
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    salvar_jogos(jogos_filtrados)
    return # Retorna uma resposta vazia com status 204 No Content
