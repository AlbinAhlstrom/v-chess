import { render, screen, fireEvent, act } from '@testing-library/react';
import { Pieces } from './Pieces';
import * as api from '../../api';

jest.mock('../../api');

describe('Pieces Component Integration', () => {
  let mockWebSocket;

  beforeEach(async () => { // Make beforeEach async
    // Mock Audio to prevent JSDOM errors
    jest.spyOn(window.HTMLMediaElement.prototype, 'play').mockImplementation(() => Promise.resolve());

    mockWebSocket = {
      send: jest.fn(),
      close: jest.fn(),
      onmessage: null,
      onclose: null,
      onerror: null,
      readyState: 1,
    };
    global.WebSocket = jest.fn(() => mockWebSocket);
    global.WebSocket.OPEN = 1;

    api.createGame.mockResolvedValue({
      game_id: 'test-game-id',
      fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    });

    api.getLegalMoves.mockResolvedValue({
        moves: [],
        status: "success"
    });

    // Render component and await initializations
    await act(async () => {
        render(<Pieces onFenChange={() => {}} />);
    });

    // Wait for game init and WebSocket connection
    expect(global.WebSocket).toHaveBeenCalled();

    // Simulate initial game_state message after connection
    await act(async () => {
        if (mockWebSocket.onmessage) {
            mockWebSocket.onmessage({
                data: JSON.stringify({
                    type: 'game_state',
                    fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', // White to move
                    status: 'connected',
                    move_history: [],
                    in_check: false,
                    is_over: false,
                })
            });
        }
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('selects piece on click and shows legal moves', async () => {
    api.getLegalMoves.mockImplementation((id, square) => {
        if (square === 'a2') {
            return Promise.resolve({
                moves: ['a2a3', 'a2a4'],
                status: 'success'
            });
        }
        return Promise.resolve({ moves: [], status: 'success' });
    });

    // Find piece at A2.
    const pieces = document.querySelectorAll('.piece');

    // Log all pieces' styles to debug
    pieces.forEach((p, index) => {
        console.log(`Piece ${index}: top = ${p.style.top}, left = ${p.style.left}`);
    });

    const pawnA2 = Array.from(pieces).find(p =>
        p.style.top.includes('6 *') && p.style.left.includes('0 *')
    );

    expect(pawnA2).toBeTruthy();

    await act(async () => {
        fireEvent.mouseDown(pawnA2, { clientX: 100, clientY: 600 });
        fireEvent.mouseUp(pawnA2, { clientX: 100, clientY: 600 });
    });

    expect(api.getLegalMoves).toHaveBeenCalledWith('test-game-id', 'a2');

    const dots = document.querySelectorAll('.legal-move-dot');
    expect(dots.length).toBe(2);

    const dotA3 = Array.from(dots).find(d => d.style.top.includes('5 *') && d.style.left.includes('0 *'));
    const dotA4 = Array.from(dots).find(d => d.style.top.includes('4 *') && d.style.left.includes('0 *'));

    expect(dotA3).toBeTruthy();
    expect(dotA4).toBeTruthy();
  });
});
