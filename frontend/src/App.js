import './App.css';
import Board from './components/Board/Board.js';
import { Pieces } from './components/Pieces/Pieces.js'; // Import Pieces
import FenDisplay from './components/FenDisplay/FenDisplay.js'; // Import FenDisplay
import { useState } from 'react'; // Import useState

function App() {
  const [fen, setFen] = useState(null); // State to hold the current FEN

  const handleFenChange = (newFen) => {
    setFen(newFen);
  };

  return (
    <div className="App">
      {/* Render FenDisplay above the Board, passing the current fen state */}
      {fen && <FenDisplay fen={fen} />}
      {/* Pass Pieces as children to Board, and pass the handleFenChange callback to Pieces */}
      <Board>
        <Pieces onFenChange={handleFenChange} />
      </Board>
    </div>
  );
}

export default App;