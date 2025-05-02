def manhattanDistance(node1, node2):
    """
    Calculate the Manhattan distance between two nodes.

    Args:
        node1: First node (Node object with position property or object with x,y properties)
        node2: Second node (Node object with position property or object with x,y properties)

    Returns:
        float: Manhattan distance between the two nodes
    """
    # Handle Node objects which have position property
    x1 = node1.position.x
    y1 = node1.position.y
    x2 = node2.position.x
    y2 = node2.position.y
    
    return abs(x1 - x2) + abs(y1 - y2)
