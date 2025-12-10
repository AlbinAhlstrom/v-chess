export const fileIntToString = n => 'abcdefgh'.split('')[n]
export const coordsToAlgebraic = (file, rank) => `${fileIntToString(file)}${8-rank}`
export const algebraicToCoords = (algebraic) => {
    const file = algebraic.charCodeAt(0) - 97; // 'a' is 97
    const rank = 8 - parseInt(algebraic[1], 10);
    return { file, rank };
}

export const fenToPosition = (fen) => {
    const [pieceData] = fen.split(" ");
    const ranks = pieceData.split("/");
    return ranks.map(rank => {
      const expandedRank = [];
      rank.split("").forEach(char => {
        const charAsInt = parseInt(char, 10);
        if (isNaN(charAsInt)) {
          expandedRank.push(char);
        } else {
          for (let i = 0; i < charAsInt; i++) {
            expandedRank.push(null);
          }
        }
      });
      return expandedRank;
    });
};

export const copyPosition = position => {
    return position
}
