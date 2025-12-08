import './Pieces.css'
import Piece from './Piece'
import { fenToPosition, coordsToAlgebraic } from '../../helpers.js'
import { getFen } from '../../api.js'
import { useState, useRef } from 'react'


function Pieces() {
    const ref = useRef()
    const [state, setState] = useState(getFen())

    const position = fenToPosition(state);

    const calculateSquare = e => {
        const {width,left,top} = ref.current.getBoundingClientRect()
        const size = width / 8
        const file = Math.floor((e.clientX - left) / size)
        const rank = Math.floor((e.clientY - top) / size)
        return coordsToAlgebraic(file, rank)
    }

    const onDrop = e => {
        const newPosition = state
        const toSquare = calculateSquare(e)
        const [piece, fromFileStr, fromRankStr] = e.dataTransfer.getData("text").split(",")
        const fromFileIndex = parseInt(fromFileStr, 10);
        const fromRankIndex = parseInt(fromRankStr, 10);
        const fromSquare = coordsToAlgebraic(fromFileIndex, fromRankIndex)
        const newFen = getFen() //state, fromSquare, toSquare)
        console.log(fromSquare)
        console.log(toSquare)
    }
    const onDragOver = e => e.preventDefault()

    return (
        <div
            className="pieces"
            ref={ref}
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
