import './App.css';
import Board from './components/Board/Board.js';
import { Pieces } from './components/Pieces/Pieces.js';
import { useCallback, useState, useEffect } from 'react';
import Lobby from './components/Lobby/Lobby.js';
import Profile from './components/Profile/Profile.js';
import About from './components/About/About.js';
import LandingPage from './components/LandingPage/LandingPage.js';
import Settings from './components/Settings/Settings.js';
import Leaderboard from './components/Leaderboard/Leaderboard.js';
import { BrowserRouter, Routes, Route, Link, useParams, Navigate } from 'react-router-dom';
import { getMe, getAuthLinks } from './api.js';

function Header({ user }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const { loginLink, logoutLink } = getAuthLinks();

  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);

  // Close dropdown when clicking outside
  useEffect(() => {
    const closeDropdown = (e) => {
        if (isDropdownOpen && !e.target.closest('.user-profile-dropdown-container')) {
            setIsDropdownOpen(false);
        }
    };
    document.addEventListener('click', closeDropdown);
    return () => document.removeEventListener('click', closeDropdown);
  }, [isDropdownOpen]);

  return (
    <header className="main-header">
      <nav className="header-nav">
        <Link to="/" className="header-logo">
          <img src="/vchess_192.png" alt="V-Chess" className="header-logo-img" />
        </Link>
        <Link to="/create-game" className="header-link header-link-create">Create Game</Link>
        <Link to="/leaderboards" className="header-link">Leaderboards</Link>
        <Link to="/about" className="header-link">About</Link>
      </nav>
      <div className="auth-section">
        {user ? (
          <div className="user-profile-dropdown-container" style={{ position: 'relative' }}>
            <div className="user-profile-trigger" onClick={toggleDropdown} style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <img src={user.picture} alt={user.name} className="header-avatar" />
            </div>
            
            {isDropdownOpen && (
                <div className="profile-dropdown-menu">
                    <Link to="/profile" className="dropdown-item" onClick={() => setIsDropdownOpen(false)}>
                        Profile
                    </Link>
                    <Link to="/settings" className="dropdown-item" onClick={() => setIsDropdownOpen(false)}>
                        Settings
                    </Link>
                    <a href={logoutLink} className="dropdown-item logout">
                        Logout
                    </a>
                </div>
            )}
          </div>
        ) : (
          <a className="header-auth-link" href={loginLink}>Login</a>
        )}
      </div>
    </header>
  );
}

function GameBoard({ variant: propVariant, matchmaking = false, computer = false }) {
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
          computer={computer}
          setFlipped={setFlipped}
        />
      </Board>
    </div>
  );
}

function Footer() {
  return (
    <footer className="main-footer">
      <a href="https://discord.gg/wGCBs5Qr" target="_blank" rel="noopener noreferrer" className="footer-link">Discord</a>
      <a href="https://forms.gle/your-feedback-form" target="_blank" rel="noopener noreferrer" className="footer-link">Feedback</a>
      <Link to="/about" className="footer-link">About</Link>
    </footer>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(() => {
    getMe().then(data => {
      setUser(data.user || null);
      setLoading(false);
    }).catch(e => {
      console.error("Failed to fetch user:", e);
      setUser(null);
      setLoading(false);
    });
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  useEffect(() => {
    window.addEventListener('focus', fetchUser);
    return () => window.removeEventListener('focus', fetchUser);
  }, [fetchUser]);

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header user={user} />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Routes>
            <Route path="/" element={user ? <Navigate to="/create-game" replace /> : <LandingPage />} />
            <Route path="/create-game" element={<Lobby />} />
            <Route path="/otb" element={<GameBoard variant="standard" />} />
            <Route path="/otb/:variant" element={<GameBoard />} />
            <Route path="/matchmaking-game/:gameId" element={<GameBoard matchmaking={true} />} />
            <Route path="/computer-game/:gameId" element={<GameBoard matchmaking={true} computer={true} />} />
            <Route path="/game/:gameId" element={<GameBoard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/profile/:userId" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/leaderboards" element={<Leaderboard />} />
            <Route path="/leaderboards/:variant" element={<Leaderboard />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
