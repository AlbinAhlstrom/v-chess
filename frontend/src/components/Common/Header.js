import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAuthLinks } from '../../api';

function Header({ user }) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { loginLink, logoutLink } = getAuthLinks();

  const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);
  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);

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

export default Header;
