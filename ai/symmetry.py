def orientations(board):
    result = []
    for reflected in (False, True):
        current = tuple(board[r*3 + (2-c if reflected else c)] for r in range(3) for c in range(3))
        for _ in range(4):
            result.append(current)
            current = tuple(current[(2-c)*3+r] for r in range(3) for c in range(3))
    return result
def canonical(board):
    return min(orientations(board))
