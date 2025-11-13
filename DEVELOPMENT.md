# Guia de Desenvolvimento – Salsilauncher

Este documento explica como configurar o ambiente, executar o projeto e contribuir com segurança.

---

## 1. Requisitos
- **Python 3.10+**
- **Node.js 18+**
- **npm**
- **VS Code** (recomendado)
- **GitHub Desktop** ou Git CLI

---

## 2. Instalação

### Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

O backend estará em `http://127.0.0.1:8000`  
O frontend em `http://localhost:5173`

---

## 3. Estrutura de Branches
| Tipo  | Exemplo | Uso |
|-------|----------|-----|
| `feat/` | `feat/atomic-save` | Nova funcionalidade |
| `fix/` | `fix/upload-bug` | Correção de bug |
| `chore/` | `chore/docs-update` | Infra, docs ou setup |
| `dev` | | Branch de desenvolvimento principal |

---

## 4. Commits
Use o padrão **Conventional Commits**:
```
<tipo>(escopo opcional): descrição curta
```
Exemplo:
```
feat(api): add atomic save for jogos_db
fix(frontend): correct game filter by tags
```

Tipos comuns: `feat`, `fix`, `chore`, `docs`, `test`, `refactor`

---

## 5. Pull Requests
Antes de abrir uma PR:
- Verifique se o código roda localmente.
- Atualize documentação se necessário.
- Marque o checklist do template.
- Nomeie a PR conforme o padrão de commits.

---

## 6. Testes
Os testes ficam em `backend/tests`.

Para executar:
```bash
cd backend
pytest
```

---

## 7. Ambiente (.env)
Crie um arquivo `.env` baseado em `.env.example`:
```
DATABASE_URL=sqlite:///./data.db
DEBUG=True
```

---

## 8. Dicas
- Sempre ative o venv antes de rodar o backend.
- Use `Ctrl + Shift + P → Python: Select Interpreter` no VS Code.
- Use `npm run dev` no terminal separado para o frontend.

---
