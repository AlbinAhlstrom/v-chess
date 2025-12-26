import './App.css';
import Board from './components/Board/Board.js';
import { Pieces } from './components/Pieces/Pieces.js';
import { useCallback, useState, useEffect } from 'react';
import Lobby from './components/Lobby/Lobby.js';
import Profile from './components/Profile/Profile.js';
import About from './components/About/About.js';
import Rules from './components/Rules/Rules.js';
import LandingPage from './components/LandingPage/LandingPage.js';
import Settings from './components/Settings/Settings.js';
import Leaderboard from './components/Leaderboard/Leaderboard.js';
import { BrowserRouter, Routes, Route, Link, useParams, Navigate } from 'react-router-dom';
import { getMe, getAuthLinks } from './api.js';

function Header({ user }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { loginLink, logoutLink } = getAuthLinks();

  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);
  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

  // Close menus when clicking outside
  useEffect(() => {
    const closeMenus = (e) => {
        if (isDropdownOpen && !e.target.closest('.user-profile-dropdown-container')) {
            setIsDropdownOpen(false);
        }
        if (isMobileMenuOpen && !e.target.closest('.mobile-menu-container') && !e.target.closest('.hamburger-button')) {
            setIsMobileMenuOpen(false);
        }
    };
    document.addEventListener('click', closeMenus);
    return () => document.removeEventListener('click', closeMenus);
  }, [isDropdownOpen, isMobileMenuOpen]);

  const navLinks = [
    { to: "/create-game", label: "Create Game", className: "header-link header-link-create" },
    { to: "/rules/standard", label: "Rules", className: "header-link" },
    { to: "/leaderboards", label: "Leaderboards", className: "header-link" },
    { to: "/about", label: "About", className: "header-link" },
  ];

  return (
    <header className="main-header">
      <div className="header-left">
        <Link to="/" className="header-logo" onClick={() => setIsMobileMenuOpen(false)}>
          <img src="/v_chess_dot_com.png" alt="V-Chess.com" className="header-logo-img" />
        </Link>
        <nav className="header-nav-desktop">
          {navLinks.map(link => (
            <Link key={link.to} to={link.to} className={link.className}>{link.label}</Link>
          ))}
        </nav>
      </div>

      <div className="header-right">
        <button className="hamburger-button" onClick={toggleMobileMenu}>
          <svg viewBox="0 0 24 24" width="24" height="24" stroke="white" strokeWidth="2" fill="none">
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
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
      </div>

      {isMobileMenuOpen && (
        <div className="mobile-menu-overlay">
          <div className="mobile-menu-container">
            {navLinks.map(link => (
              <Link 
                key={link.to} 
                to={link.to} 
                className="mobile-nav-link" 
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      )}
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
      <a href="https://docs.google.com/forms/d/1KbRrUx4oW_jXlli110CnDYjQJqX_dtr_4uFmVjO6poU/viewform" target="_blank" rel="noopener noreferrer" className="footer-link">Feedback</a>
      <Link to="/rules/standard" className="footer-link">Rules</Link>
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
            <Route path="/rules" element={<Rules />} />
            <Route path="/rules/:variant" element={<Rules />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
