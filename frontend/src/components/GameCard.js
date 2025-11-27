import React, { useRef } from 'react';
import './GameCard.css';
import { Link } from 'react-router-dom';
import api from "../../services/api"

function GameCard({ jogo }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    api.post(`/jogos/${jogo.id}/capa`, formData)
    .then(() => window.location.reload())
    .catch(error => console.error('Erro no upload:', error));
  };

  const handleImageClick = () => fileInputRef.current.click();

  return (
    // O que faz:
  //   O componente <Link> do React Router transforma tudo que está dentro dele
  //   em um link de navegação. Ele é melhor que uma tag <a> normal porque
  //   ele não recarrega a página, apenas muda a URL e avisa o roteador
  //   para renderizar o novo componente.
  <Link to={`/jogo/${jogo.id}`} className="game-card-link">
  <div className="game-card">
    <input type="file" ref={fileInputRef} onChange={handleFileChange} style={{ display: 'none' }} accept="image/*" />
    <div className="game-card-image-container" onClick={(e) => { e.preventDefault(); handleImageClick(); }}>
      {jogo.imagem_capa ? (
        <img src={`http://127.0.0.1:8000/${jogo.imagem_capa}`} alt={`Capa de ${jogo.nome}`} className="game-card-image"/>
      ) : (
        <div className="game-card-image-placeholder"><span>Adicionar Capa</span></div>
      )}
    </div>
    <div className="game-card-info">
      <h3 className="game-card-title">{jogo.nome}</h3>
    </div>
  </div>
</Link>
);
}
export default GameCard;