// frontend/src/pages/ColecoesPage.js
import React, { useState, useEffect } from 'react';
import CollectionCard from '../components/CollectionCard';
import './ColecoesPage.css'; // Vamos criar este arquivo
import api from '../services/api';

function ColecoesPage() {
  const [colecoes, setColecoes] = useState([]);

  const fetchColecoes = () => {
    api.get('/colecoes')
      .then(response => setColecoes(response.data))
      .catch(error => console.error('Erro ao buscar coleções:', error));
  };

  useEffect(() => {
    fetchColecoes();
  }, []);

  const handleCreateCollection = () => {
    const nome = window.prompt("Digite o nome da nova coleção:");
    if (nome) {
      // Cria um ID simples a partir do nome (ex: "Jogos de Terror" -> "jogos-de-terror")
      const id = nome.toLowerCase().replace(/\s+/g, '-');
      const novaColecao = { id, nome, capa: null, descricao: null };

      api.post('/colecoes', novaColecao)
        .then(() => {
          // Após criar, busca a lista de coleções novamente para atualizar a tela
          fetchColecoes();
        })
        .catch(error => console.error('Erro ao criar coleção:', error));
    }
  };

  return (
    <div className="colecoes-page">
      <h1>Coleções</h1>
      <div className="colecoes-grid">
        <CollectionCard onClick={handleCreateCollection} />
        {colecoes.map(c => (
          <CollectionCard key={c.id} colecao={c} />
        ))}
      </div>
    </div>
  );
}

export default ColecoesPage;