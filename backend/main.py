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

# --- MODELOS DE DADOS (FINAIS) ---
class AvaliacaoDetalhada(BaseModel):
    gameplay: int = Field(default=0, ge=0, le=3)
    graficos: int = Field(default=0, ge=0, le=2)
    historia: int = Field(default=0, ge=0, le=2)
    audio: int = Field(default=0, ge=0, le=2)
    inovacao: int = Field(default=0, ge=0, le=1)
    bonus: int = Field(default=0, ge=0, le=1)

class Colecao(BaseModel):
    id: str
    nome: str
    capa: Optional[str] = None
    descricao: Optional[str] = None

class Jogo(BaseModel):
    id: int
    nome: str
    caminho_executavel: str
    caminho_pasta: str
    tamanho_gb: Optional[float] = None
    imagem_capa: Optional[str] = None
    imagem_fundo: Optional[str] = None
    imagens_extras: List[str] = Field(default_factory=list)
    descricao: Optional[str] = None
    desenvolvedor: Optional[str] = None
    studio: Optional[str] = None
    engine: Optional[str] = None
    versao: Optional[str] = None
    links: List[str] = Field(default_factory=list)
    genero: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    colecoes: List[str] = Field(default_factory=list)
    tempo_jogado_segundos: int = 0
    ultima_vez_jogado: Optional[str] = None
    status: str = "Não Jogado"
    zerado: bool = False
    jogar_mais_tarde: bool = False
    review_texto: Optional[str] = None
    avaliacao_detalhada: Optional[AvaliacaoDetalhada] = None

# --- CONFIGURAÇÃO DA APLICAÇÃO ---
app = FastAPI(title="Salsilauncher API")
DB_FILE = "jogos_db.json"

# CORS Middleware
origins = ["http://localhost:6969"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir arquivos estáticos da pasta de mídia
app.mount("/midia_launcher", StaticFiles(directory="midia_launcher"), name="midia")

    
# Função de salvamento atômico
def salvar_arquivo_atomico(path: str, dados):
    # cria um arquivo temporário na mesma pasta
    dir_path = os.path.dirname(path) or "."
    fd, temp_path = tempfile.mkstemp(dir=dir_path)
    os.close(fd)

    try:
        # grava o JSON completo no arquivo temporário e substitui o arquivo antigo de forma atômica
        with open(temp_path, "w", encoding="utf-8") as temp_file:
            json.dump(dados, temp_file, indent=4, ensure_ascii=False)
        shutil.move(temp_path, path)

    except Exception as e:
        # remove o temporário se algo der errado
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

# FUNÇÕES AUXILIARES DE BANCO DE DADOS
def salvar_jogos(jogos: List[Jogo]):
    dados_para_salvar = [jogo.dict() for jogo in jogos]
    salvar_arquivo_atomico(DB_FILE, dados_para_salvar)

def salvar_colecoes(colecoes: List[Colecao]):
    dados_para_salvar = [c.dict() for c in colecoes]
    salvar_arquivo_atomico(COLECOES_DB_FILE, dados_para_salvar)

def carregar_jogos() -> List[Jogo]:
    if not os.path.exists(DB_FILE):
        salvar_arquivo_atomico(DB_FILE, [])
        return []
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            dados_brutos = json.load(f)
            return [Jogo(**data) for data in dados_brutos]
    except json.JSONDecodeError:
        return []

    
COLECOES_DB_FILE = "colecoes_db.json"

def carregar_colecoes() -> List[Colecao]:
    if not os.path.exists(COLECOES_DB_FILE):
        # Cria uma coleção padrão "Jogar mais Tarde" se o arquivo não existir
        colecao_padrao = [Colecao(id="jogar-mais-tarde", nome="Jogar mais Tarde")]
        salvar_colecoes(colecao_padrao)
        return colecao_padrao
    try:
        with open(COLECOES_DB_FILE, "r", encoding="utf-8") as f:
            dados_brutos = json.load(f)
            return [Colecao(**data) for data in dados_brutos]
    except json.JSONDecodeError:
        return []

#  ENDPOINTS DA API

@app.get("/jogos", response_model=List[Jogo])
def listar_jogos(q: Optional[str] = None, tags: Optional[str] = None):
    """
    Lista jogos com busca e filtro.
    - q: termo de busca
    - tags: string de tags separadas por vírgula (ex: "rpg,acao")
    """
    jogos = carregar_jogos()

    # Filtragem por Tags
    if tags:
        tags_requisitadas = set(tags.lower().split(','))
        jogos = [
            jogo for jogo in jogos if tags_requisitadas.issubset(set(t.lower() for t in jogo.tags))
        ]

    # Busca por Texto com Pontuação
    if q:
        resultados_com_pontuacao = []
        termo_busca = q.lower()
        for jogo in jogos:
            pontuacao = 0
            if termo_busca in jogo.nome.lower():
                pontuacao += 10
            if jogo.studio and termo_busca in jogo.studio.lower():
                pontuacao += 5
            if jogo.descricao and termo_busca in jogo.descricao.lower():
                pontuacao += 1

            if pontuacao > 0:
                resultados_com_pontuacao.append({"jogo": jogo, "pontuacao": pontuacao})

        # Ordena os resultados pela pontuação
        resultados_ordenados = sorted(resultados_com_pontuacao, key=lambda x: x["pontuacao"], reverse=True)
        return [item["jogo"] for item in resultados_ordenados]

    return jogos

@app.post("/scan")
def escanear_pasta_por_jogos(caminho: str = Body(..., embed=True)):
    jogos_atuais = carregar_jogos()
    pastas_atuais = {jogo.caminho_pasta for jogo in jogos_atuais}
    novos_jogos_encontrados = 0

    for nome_pasta in os.listdir(caminho):
        caminho_completo_pasta = os.path.join(caminho, nome_pasta)
        if not os.path.isdir(caminho_completo_pasta) or caminho_completo_pasta in pastas_atuais:
            continue
        
        executavel_encontrado = None
        for sub_root, _, sub_files in os.walk(caminho_completo_pasta):
            for arquivo in sub_files:
                if arquivo.lower().endswith(".exe"):
                    executavel_encontrado = os.path.join(sub_root, arquivo)
                    break
            if executavel_encontrado:
                break
        
        if executavel_encontrado:
            novo_id = max([j.id for j in jogos_atuais], default=0) + 1
            novo_jogo = Jogo(id=novo_id, nome=nome_pasta, caminho_executavel=executavel_encontrado, caminho_pasta=caminho_completo_pasta)
            jogos_atuais.append(novo_jogo)
            pastas_atuais.add(caminho_completo_pasta)
            novos_jogos_encontrados += 1
    
    if novos_jogos_encontrados > 0:
        salvar_jogos(jogos_atuais)

    return {"status": "Escaneamento concluído!", "novos_jogos_adicionados": novos_jogos_encontrados, "total_na_biblioteca": len(jogos_atuais)}

@app.post("/jogos/{jogo_id}/capa", status_code=200)
async def upload_capa_jogo(jogo_id: int, file: UploadFile = File(...)):
    jogos = carregar_jogos()
    jogo_para_atualizar = next((j for j in jogos if j.id == jogo_id), None)
    if not jogo_para_atualizar:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    caminho_imagem = f"midia_launcher/{jogo_id}_capa.webp"
    try:
        img = Image.open(file.file)
        img.thumbnail((600, 900))
        img.save(caminho_imagem, "webp", quality=85)
    except Exception:
        raise HTTPException(status_code=500, detail="Não foi possível processar a imagem.")
    
    jogo_para_atualizar.imagem_capa = caminho_imagem
    salvar_jogos(jogos)
    return {"status": "Capa atualizada com sucesso!", "caminho_imagem": caminho_imagem}

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
    Carrega e retorna a lista de coleções do seu próprio banco de dados.
    """
    return carregar_colecoes()

@app.post("/colecoes", response_model=Colecao, status_code=201)
def criar_colecao(colecao: Colecao):
    """
    Recebe os dados de uma nova coleção e a salva no banco de dados.
    """
    colecoes_atuais = carregar_colecoes()
    # Checa se uma coleção com esse ID já existe
    if any(c.id == colecao.id for c in colecoes_atuais):
        raise HTTPException(status_code=400, detail="Uma coleção com este ID já existe.")

    colecoes_atuais.append(colecao)
    salvar_colecoes(colecoes_atuais)
    return colecao

@app.get("/colecoes/{colecao_id}/jogos", response_model=List[Jogo])
def listar_jogos_da_colecao(colecao_id: str):
    """
    Retorna todos os jogos que pertencem a uma coleção específica.
    """
    todos_jogos = carregar_jogos()
    jogos_na_colecao = [
        jogo for jogo in todos_jogos if colecao_id in jogo.colecoes
    ]
    return jogos_na_colecao

@app.get("/tags", response_model=List[str])
def listar_tags_unicas():
    """Retorna uma lista de todas as tags únicas de todos os jogos."""
    jogos = carregar_jogos()
    todas_as_tags = set()
    for jogo in jogos:
        for tag in jogo.tags:
            todas_as_tags.add(tag)
    return sorted(list(todas_as_tags))

@app.get("/jogos/aleatorio", response_model=List[Jogo])
def listar_jogos_aleatorios(tags: Optional[str] = None):
    """Lista até 5 jogos aleatórios, opcionalmente filtrados por tags."""
    jogos = carregar_jogos()
    if tags:
        tags_requisitadas = set(tags.lower().split(','))
        jogos = [
            jogo for jogo in jogos if tags_requisitadas.issubset(set(t.lower() for t in jogo.tags))
        ]

    # Define o número de jogos aleatórios, no máximo 5 ou o total de jogos disponíveis
    num_aleatorios = min(5, len(jogos))
    return random.sample(jogos, num_aleatorios)

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
