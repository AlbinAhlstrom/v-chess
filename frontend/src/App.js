import './App.css';
import Board from './components/Board/Board.js';
import { Pieces } from './components/Pieces/Pieces.js';
import { useCallback } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function GameBoard({ variant }) {
  const handleFenChange = useCallback((newFen) => {
    // FEN state tracking removed from App as it's no longer displayed here
  }, []);

  return (
    <div className="App">
      <Board>
        <Pieces onFenChange={handleFenChange} variant={variant} />
      </Board>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<GameBoard variant="standard" />} />
        <Route path="/standard" element={<GameBoard variant="standard" />} />
        <Route path="/antichess" element={<GameBoard variant="antichess" />} />
        <Route path="/atomic" element={<GameBoard variant="atomic" />} />
        <Route path="/chess960" element={<GameBoard variant="chess960" />} />
        <Route path="/crazyhouse" element={<GameBoard variant="crazyhouse" />} />
        <Route path="/horde" element={<GameBoard variant="horde" />} />
        <Route path="/kingofthehill" element={<GameBoard variant="kingofthehill" />} />
        <Route path="/racingkings" element={<GameBoard variant="racingkings" />} />
        <Route path="/threecheck" element={<GameBoard variant="threecheck" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
