import './Pieces.css'
import Piece from './Piece'
import { fenToPosition} from '../../helpers.js'
import { getFen } from '../../api.js'
import { useState } from 'react'


function Pieces() {
    const [state, setState] = useState(getFen())
    const position = fenToPosition(state);

    const onDrop = e => {
        const [piece,file,rank] = e.dataTransfer.getData("text").split(",")
        console.log(piece, file, rank)
    }
    const onDragOver = e => e.preventDefault()

    return (
        <div
            className="pieces"
            onDragOver={onDragOver}
            onDrop={onDrop}>

            {position.map((rankArray, rankIndex) =>
                rankArray.map((pieceType, fileIndex) =>
                    pieceType
                        ? <Piece
                            key={`p-${rankIndex}-${fileIndex}`}
                            rank={rankIndex}
                            file={fileIndex}
                            piece={pieceType}
                          />
                        : null
                )
            )}
        </div>
    );
}

export default Pieces;
