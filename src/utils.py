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
    
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)
