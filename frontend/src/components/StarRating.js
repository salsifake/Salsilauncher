import React from 'react';
import './StarRating.css';

// maxRating: o número máximo de estrelas que podem ser dadas
// rating: a nota atual (quantas estrelas estão preenchidas)
// onRatingChange: uma função que será chamada quando o usuário clicar em uma estrela
function StarRating({ maxRating, rating, onRatingChange }) {
  const stars = [];
  for (let i = 1; i <= maxRating; i++) {
    stars.push(
      <span
        key={i}
        className={i <= rating ? 'star filled' : 'star'}
        onClick={() => onRatingChange(i)}
      >
        ★
      </span>
    );
  }

  return <div className="star-rating-container">{stars}</div>;
}

export default StarRating;