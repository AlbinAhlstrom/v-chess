import React from 'react';
import { Link } from 'react-router-dom';

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

export default Footer;
