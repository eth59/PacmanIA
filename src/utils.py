def manhattanDistance(xy1, xy2):
    """
    Compute the Manhattan distance between two points.
    
    Parameters:
    xy1 (tuple): The first point (x1, y1).
    xy2 (tuple): The second point (x2, y2).
    
    Returns:
    int: The Manhattan distance between the two points.
    """
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])