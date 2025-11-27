// frontend/src/pages/DetalhesJogo.js
import React, { useState, useEffect, useCallback } from 'react';
import './DetalhesJogo.css';
import { Link, useParams } from 'react-router-dom';
import StarRating from '../components/StarRating'; // Importamos nosso novo componente
import api from '../services/api';

export default DetalhesJogo;

function DetalhesJogo() {

  const { id } = useParams();
  const [jogo, setJogo] = useState(null); // Inicia como nulo, pois ainda não temos os dados

  useEffect(() => {
    // Busca os dados do jogo específico usando o ID da URL
    api.get(`/jogos/${id}`)
      .then(response => {
        setJogo(response.data);
      })
      .catch(error => {
        console.error('Erro ao buscar detalhes do jogo:', error);
      });// frontend/src/pages/DetalhesJogo.js
      
      function DetalhesJogo() {
        const { id } = useParams();
        const [jogo, setJogo] = useState(null);
      
        // useCallback para evitar recriar a função a cada renderização
        const calcularNotaGeral = useCallback(() => {
          if (!jogo || !jogo.avaliacao_detalhada) return 0;
          const { gameplay, graficos, historia, audio, inovacao, bonus } = jogo.avaliacao_detalhada;
          // Implementa a regra de cálculo que definimos
          const notaTotal = (gameplay + graficos + historia + audio + inovacao) * 0.5 + bonus;
          return notaTotal;
        }, [jogo]);
      
        useEffect(() => {
          api.get(`/jogos/${id}`)
            .then(response => {
              // Garante que a avaliação detalhada exista no objeto do jogo
              if (!response.data.avaliacao_detalhada) {
                response.data.avaliacao_detalhada = { gameplay: 0, graficos: 0, historia: 0, audio: 0, inovacao: 0, bonus: 0 };
              }
              setJogo(response.data);
            })
            .catch(error => console.error('Erro ao buscar detalhes do jogo:', error));
        }, [id]);
      
        const handleReviewTextChange = (e) => {
          setJogo(prev => ({ ...prev, review_texto: e.target.value }));
        };
      
        const handleDetailedRatingChange = (category, newRating) => {
          setJogo(prev => ({
            ...prev,
            avaliacao_detalhada: {
              ...prev.avaliacao_detalhada,
              [category]: newRating,
            },
          }));
        };
      
        const handleSaveChanges = () => {
          api.put(`/jogos/${id}`, jogo)
            .then(response => {
              alert('Review e alterações salvas com sucesso!');
              setJogo(response.data);
            })
            .catch(error => console.error('Erro ao salvar review:', error));
        };
      
        if (!jogo) return <div className="loading">Carregando...</div>;
      
        const notaGeral = calcularNotaGeral();
      
        return (
          <div className="detalhes-container">
            <div className="detalhes-header">
              {/* ... (cabeçalho com capa e informações que já fiz) ... */}
              <div className="nota-geral">Nota: {notaGeral.toFixed(1)} / 6.0</div>
              <Link to={`/jogo/${id}/editar`}><button>Editar Jogo</button></Link>
            </div>
            <div className="detalhes-body">
              {/* ... (seção de descrição) ... */}
      
              {/* NOVA SEÇÃO DE REVIEW */}
              <div className="review-section">
                <h2>Sua Review</h2>
                <div className="review-layout">
                  <textarea 
                    className="review-textarea"
                    placeholder="Escreva sua review aqui..." 
                    value={jogo.review_texto || ''}
                    onChange={handleReviewTextChange}
                  />
                  <div className="detailed-ratings">
                    <div className="rating-item"><span>Gameplay</span><StarRating maxRating={3} rating={jogo.avaliacao_detalhada.gameplay} onRatingChange={r => handleDetailedRatingChange('gameplay', r)} /></div>
                    <div className="rating-item"><span>Gráficos</span><StarRating maxRating={2} rating={jogo.avaliacao_detalhada.graficos} onRatingChange={r => handleDetailedRatingChange('graficos', r)} /></div>
                    <div className="rating-item"><span>História</span><StarRating maxRating={2} rating={jogo.avaliacao_detalhada.historia} onRatingChange={r => handleDetailedRatingChange('historia', r)} /></div>
                    <div className="rating-item"><span>Áudio</span><StarRating maxRating={2} rating={jogo.avaliacao_detalhada.audio} onRatingChange={r => handleDetailedRatingChange('audio', r)} /></div>
                    <div className="rating-item"><span>Inovação</span><StarRating maxRating={1} rating={jogo.avaliacao_detalhada.inovacao} onRatingChange={r => handleDetailedRatingChange('inovacao', r)} /></div>
                    <div className="rating-item"><span>Bônus</span><StarRating maxRating={1} rating={jogo.avaliacao_detalhada.bonus} onRatingChange={r => handleDetailedRatingChange('bonus', r)} /></div>
                  </div>
                </div>
                <button onClick={handleSaveChanges} className="save-button">Salvar Alterações</button>
              </div>
            </div>
          </div>
        );
      }
  }, [id]); // O efeito roda novamente se o ID na URL mudar

  // Enquanto os dados do jogo não chegam, mostramos uma mensagem de carregamento
  if (!jogo) {
    return <div className="loading">Carregando...</div>;
  }

  // Quando os dados chegam, renderizamos a página
  return (
    <div className="detalhes-container">
      {/* A imagem de fundo que planejamos no futuro viria aqui */}
      <div className="detalhes-header">
        {jogo.imagem_capa && (
          <img src={`/${jogo.imagem_capa}`} alt={`Capa de ${jogo.nome}`} className="detalhes-capa" />
        )}
        <div className="detalhes-header-info">
            <h1>{jogo.nome}</h1>
            <p>Desenvolvedor: {jogo.desenvolvedor || '-'}</p>
            <p>Gênero: {jogo.genero || '-'}</p>
            <Link to={`/jogo/${id}/editar`}>
                <button>Editar Jogo</button>
            </Link>
        </div>
      </div>
      <div className="detalhes-body">
        <h2>Descrição</h2>
        <p className="descricao">{jogo.descricao || 'Nenhuma descrição fornecida.'}</p>
      </div>
    </div>
  );
}