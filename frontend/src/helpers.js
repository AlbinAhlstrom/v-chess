export const fileIntToString = file => String.fromCharCode(file + 97)

export const coordsToAlgebraic = (fileIndex, rankIndex) => {
    const file = fileIntToString(fileIndex);
    const rank = 8 - rankIndex;
    return `${file}${rank}`;
};

export const fenToPosition = (fenString) => {
    const piecesFen = fenString.split(' ')[0];
    let position = Array(8).fill().map(() => Array(8).fill(''));
    let rankIndex = 0;
    let fileIndex = 0;

    for (const char of piecesFen) {
        if (char === '/') {
            rankIndex++;
            fileIndex = 0;
        } else if (!isNaN(parseInt(char))) {
            fileIndex += parseInt(char);
        } else {
            position[rankIndex][fileIndex] = char;
            fileIndex++;
        }
    }

    return position;
};

export const copyPosition = position => {
    return position
}
