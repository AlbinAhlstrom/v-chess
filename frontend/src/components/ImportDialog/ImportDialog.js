import './ImportDialog.css';
import { useState } from 'react';

function ImportDialog({ onImport, onCancel }) {
    const [fen, setFen] = useState('');
    const [variant, setVariant] = useState('standard');

    const handleSubmit = (e) => {
        e.preventDefault();
        onImport(fen, variant);
    };

    const handleOverlayClick = (e) => {
        if (e.target === e.currentTarget) {
            onCancel();
        }
    };

    return (
        <div className="import-dialog-overlay" onClick={handleOverlayClick}>
            <div className="import-dialog">
                <h3>Import Game from FEN</h3>
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '15px' }}>
                        <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Variant:</label>
                        <select 
                            value={variant} 
                            onChange={(e) => setVariant(e.target.value)}
                            style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #444', backgroundColor: '#302e2b', color: '#fff' }}
                        >
                            <option value="standard">Standard</option>
                            <option value="antichess">Antichess</option>
                        </select>
                    </div>
                    <input
                        type="text"
                        value={fen}
                        onChange={(e) => setFen(e.target.value)}
                        placeholder="Paste FEN string here"
                        className="fen-input"
                    />
                    <div className="import-actions">
                        <button type="button" onClick={onCancel} className="cancel-button">Cancel</button>
                        <button type="submit" className="import-button">Import</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default ImportDialog;
