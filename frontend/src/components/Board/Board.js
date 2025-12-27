import './Board.css'
import { fileIntToString } from '../../helpers.js'

function Board({ children, flipped = false, showCoordinates = false, pointerEvents = 'auto' }) { // Accept children prop
    const getSquareColor = (i, j) => {
        let c = "square";
        c += (i + j) % 2 === 0 ? " square--light" : " square--dark";
        return c;
    }
    const ranks = Array(8).fill().map((x, i) => flipped ? i + 1 : 8 - i)
    const files = Array(8).fill().map((x, i) => flipped ? fileIntToString(7 - i) : fileIntToString(i))

    return <div className="board" style={{ pointerEvents }}>
        {/* Rank labels (1-8) */}
        {showCoordinates && (
            <div className="coordinates coordinates--ranks">
                {ranks.map(rank => <div key={rank}>{rank}</div>)}
            </div>
        )}

        <div className="squares">
        {flipped ? 
            ranks.slice().reverse().map((rank, i) =>
                files.slice().reverse().map((file, j) =>
                    <div key={file + rank} className={getSquareColor(7 - i, 7 - j)} data-square={file + rank}></div>)
            )
            :
            ranks.map((rank, i) =>
                files.map((file, j) =>
                    <div key={file + rank} className={getSquareColor(i, j)} data-square={file + rank}></div>)
            )
        }
        </div>

        {/* File labels (a-h) */}
        {showCoordinates && (
            <div className="coordinates coordinates--files">
                {files.map(file => <div key={file}>{file}</div>)}
            </div>
        )}

        {children} {/* Render children here */}
    </div>
}

export default Board