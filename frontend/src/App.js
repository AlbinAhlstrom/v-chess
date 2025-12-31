import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';

// Components
import Lobby from './components/Lobby/Lobby';
import Profile from './components/Profile/Profile';
import About from './components/About/About';
import Rules from './components/Rules/Rules';
import LandingPage from './components/LandingPage/LandingPage';
import UsernamePrompt from './components/UsernamePrompt/UsernamePrompt';
import Settings from './components/Settings/Settings';
import Leaderboard from './components/Leaderboard/Leaderboard';
import Header from './components/Common/Header';
import Footer from './components/Common/Footer';
import GameBoardWrapper from './components/Board/GameBoardWrapper';

// Hooks
import { useUserSession } from './hooks/useUserSession';

function App() {
  const { user, loading, handleUsernameComplete } = useUserSession();

  if (loading) {
    return <div className="loading-screen">Loading...</div>;
  }

  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {user && !user.username && <UsernamePrompt onComplete={handleUsernameComplete} />}
        <Header user={user} />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Routes>
            <Route path="/" element={user ? <Navigate to="/create-game" replace /> : <LandingPage />} />
            <Route path="/create-game" element={<Lobby />} />
            <Route path="/otb" element={<GameBoardWrapper variant="standard" />} />
            <Route path="/otb/:variant" element={<GameBoardWrapper />} />
            <Route path="/matchmaking-game/:gameId" element={<GameBoardWrapper matchmaking={true} />} />
            <Route path="/computer-game/:gameId" element={<GameBoardWrapper matchmaking={true} computer={true} />} />
            <Route path="/game/:gameId" element={<GameBoardWrapper />} />
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