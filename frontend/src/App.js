import './App.css';
import Board from './components/Board/Board.js';
import { Pieces } from './components/Pieces/Pieces.js';
import { useCallback, useState, useEffect } from 'react';
import Lobby from './components/Lobby/Lobby.js';
import Profile from './components/Profile/Profile.js';
import { BrowserRouter, Routes, Route, Link, useParams, Navigate } from 'react-router-dom';
import { getMe, getAuthLinks } from './api.js';

function Header() {
  const [user, setUser] = useState(null);
  const { loginLink, logoutLink } = getAuthLinks();

  const fetchUser = useCallback(() => {
    getMe().then(data => {
      if (data.user) {
        setUser(data.user);
      } else {
        setUser(null);
      }
    }).catch(e => {
      console.error("Failed to fetch user:", e);
      setUser(null);
    });
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  // Refresh user when tab is focused (e.g. returning from login redirect)
  useEffect(() => {
    window.addEventListener('focus', fetchUser);
    return () => window.removeEventListener('focus', fetchUser);
  }, [fetchUser]);

  return (
    <header className="main-header">
      <nav className="header-nav">
        <Link to="/create-game" className="header-logo">V-Chess</Link>
        <Link to="/create-game" className="header-link">Create Game</Link>
      </nav>
      <div className="auth-section">
        {user ? (
          <div className="user-profile">
            <Link to="/profile">
              <img src={user.picture} alt={user.name} className="header-avatar" title={user.name} />
            </Link>
            <a className="header-auth-link" href={logoutLink}>Logout</a>
          </div>
        ) : (
          <a className="header-auth-link" href={loginLink}>Login</a>
        )}
      </div>
    </header>
  );
}

function GameBoard({ variant: propVariant, matchmaking = false }) {
  const { variant: urlVariant } = useParams();
  const variant = urlVariant || propVariant || "standard";
  const [flipped, setFlipped] = useState(false);
  
  const handleFenChange = useCallback((newFen) => {
    // FEN state tracking removed from App
  }, []);

  const showCoordinates = (() => {
    const saved = localStorage.getItem('showBoardCoordinates');
    return saved !== null ? JSON.parse(saved) : false;
  })();

  return (
    <div className="App">
      <Board flipped={flipped} showCoordinates={showCoordinates}>
        <Pieces 
          onFenChange={handleFenChange} 
          variant={variant} 
          matchmaking={matchmaking}
          setFlipped={setFlipped}
        />
      </Board>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route path="/" element={<Navigate to="/create-game" replace />} />
        <Route path="/create-game" element={<Lobby />} />
        <Route path="/otb" element={<GameBoard variant="standard" />} />
        <Route path="/otb/:variant" element={<GameBoard />} />
        <Route path="/matchmaking-game/:gameId" element={<GameBoard matchmaking={true} />} />
        <Route path="/game/:gameId" element={<GameBoard />} />
        <Route path="/profile" element={<Profile />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
