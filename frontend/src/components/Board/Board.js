import './Board.css'
import { fileIntToString } from '../../helpers.js'

const Board = () => {
    const getSquareColor = (i, j) => {
        let c = "square";
        c += (i + j) % 2 === 0 ? " square--light" : " square--dark";
        return c;
    }
    const ranks = Array(8).fill().map((x, i) => 8-i)
    const files = Array(8).fill().map((x, i) => fileIntToString(i))

    return <div className="board">
        <div className="squares">
        {ranks.map((rank, i) =>
            files.map((file, j) =>
                <div key={file + rank} className={getSquareColor(i, j)}>{file}{rank}</div>)
        )
        }
        </div>
    </div>
}

export default Board
