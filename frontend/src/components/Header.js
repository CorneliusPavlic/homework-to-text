import React from 'react';
import script2math from '../assets/script2math.png';

const Header = () => {
  return (
    <header style={{ textAlign: 'center', margin: '20px 0' }}>
      <img src={script2math} alt="Script 2 Math" style={{ width: '200px', marginBottom: '10px' }} />
      <h1>We help teachers grade accurately and efficiently. Let's grade!</h1>
    </header>
  );
};

export default Header;
