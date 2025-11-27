// frontend/src/components/AccordionItem.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './AccordionItem.css';
import api from "../../services/api"

function AccordionItem({ colecao }) {
  const [isOpen, setIsOpen] = useState(false);
  const [jogos, setJogos] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Este efeito roda quando o usuário abre o acordeão
  useEffect(() => {
    // Se não estiver aberto ou se os jogos já foram carregados, não faz nada
    if (!isOpen || jogos.length > 0) {
      return;
    }

    setIsLoading(true);
    api.get(`/colecoes/${colecao.id}/jogos`)
      .then(response => {
        setJogos(response.data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error(`Erro ao buscar jogos da coleção ${colecao.nome}:`, error);
        setIsLoading(false);
      });
  }, [isOpen, colecao.id, colecao.nome, jogos.length]);

  return (
    <div className="accordion-item">
      <div className="accordion-header" onClick={() => setIsOpen(!isOpen)}>
        <span className={`arrow ${isOpen ? 'open' : ''}`}>▶</span>
        <span className="collection-name">{colecao.nome}</span>
      </div>
      {isOpen && (
        <div className="accordion-content">
          {isLoading && <div className="loading-jogos">Carregando jogos...</div>}
          {!isLoading && jogos.length === 0 && <div className="no-jogos">Nenhum jogo nesta coleção.</div>}
          {!isLoading && jogos.map(jogo => (
            <Link key={jogo.id} to={`/jogo/${jogo.id}`} className="game-link">
              {/* No futuro podemos adicionar o ícone do jogo aqui */}
              {jogo.nome}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

export default AccordionItem;