import './App.css';
import Board from './components/Board/Board.js';
import { Pieces } from './components/Pieces/Pieces.js'; // Import Pieces
import { useCallback } from 'react'; // Import useCallback

function App() {
  const handleFenChange = useCallback((newFen) => {
    // FEN state tracking removed from App as it's no longer displayed here
  }, []);

  return (
    <div className="App">
      <Board>
        <Pieces onFenChange={handleFenChange} />
      </Board>
    </div>
  );
}

export default App;