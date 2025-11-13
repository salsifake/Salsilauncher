// frontend/src/pages/AdicionarJogoPage.js
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

// Este é o estado inicial para um jogo novo e vazio
const JOGO_VAZIO = {
    nome: '', caminho_executavel: '', caminho_pasta: '', descricao: '',
    desenvolvedor: '', studio: '', engine: '', versao: '', genero: '',
    tags: [], colecoes: []
};

function AdicionarJogoPage() {
    const { id } = useParams(); // Pega o ID da URL, se existir
    const navigate = useNavigate(); // Hook para nos permitir navegar entre páginas
    const isEditMode = Boolean(id); // Se tem ID, estamos no modo de edição

    const [jogoData, setJogoData] = useState(JOGO_VAZIO);
    const [allCollections, setAllCollections] = useState([]);

    // Se estamos em modo de edição, busca os dados do jogo e das coleções
    useEffect(() => {
        // Busca todas as coleções existentes para popular o seletor
        axios.get('http://127.0.0.1:8000/colecoes').then(res => setAllCollections(res.data));

        if (isEditMode) {
            axios.get(`http://127.0.0.1:8000/jogos/${id}`)
                .then(response => {
                    setJogoData(response.data);
                });
        }
    }, [id, isEditMode]);

    // Função genérica para atualizar qualquer campo do formulário
    const handleChange = (e) => {
        const { name, value } = e.target;
        setJogoData(prev => ({ ...prev, [name]: value }));
    };

    // Função para lidar com a seleção de coleções
    const handleCollectionChange = (e) => {
        const selectedOptions = Array.from(e.target.selectedOptions, option => option.value);
        setJogoData(prev => ({ ...prev, colecoes: selectedOptions }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const request = isEditMode
            ? axios.put(`http://127.0.0.1:8000/jogos/${id}`, jogoData)
            : axios.post('http://127.0.0.1:8000/jogos', { ...jogoData, id: 0 }); // Envia ID 0 para criação

        request.then(response => {
            const jogoSalvo = response.data;
            navigate(`/jogo/${jogoSalvo.id}`); // Navega para a página do jogo salvo
        }).catch(error => console.error("Erro ao salvar o jogo:", error));
    };

    const handleDelete = () => {
        if (window.confirm("Você tem certeza que quer remover este jogo? Esta ação não pode ser desfeita.")) {
            axios.delete(`http://127.0.0.1:8000/jogos/${id}`)
                .then(() => navigate('/')) // Navega para a home após remover
                .catch(error => console.error("Erro ao remover o jogo:", error));
        }
    };

    return (
        <div style={{padding: '2rem'}}>
            <h1>{isEditMode ? 'Editar Jogo' : 'Adicionar Novo Jogo'}</h1>
            <form onSubmit={handleSubmit}>
                {/* Vamos adicionar os campos do formulário aqui */}
                <label>Nome do Jogo:</label>
                <input name="nome" value={jogoData.nome} onChange={handleChange} required />

                <label>Caminho do Executável:</label>
                <input name="caminho_executavel" value={jogoData.caminho_executavel} onChange={handleChange} />

                <label>Desenvolvedor:</label>
                <input name="desenvolvedor" value={jogoData.desenvolvedor} onChange={handleChange} />

                <label>Coleções:</label>
                <select multiple value={jogoData.colecoes} onChange={handleCollectionChange}>
                    {allCollections.map(c => <option key={c.id} value={c.id}>{c.nome}</option>)}
                </select>

                {/* Adicionar mais campos aqui seguindo o mesmo padrão */}

                <button type="submit">{isEditMode ? 'Salvar Alterações' : 'Adicionar Jogo'}</button>
                {isEditMode && <button type="button" onClick={handleDelete}>Remover Jogo</button>}
            </form>
        </div>
    );
}

export default AdicionarJogoPage;