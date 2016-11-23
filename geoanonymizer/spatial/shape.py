# -*- coding: utf-8 -*-

"""
Functions dealing with shapes, especially points and polygons.
"""


def is_a_vertex_of_polygon(x, y, polygon):
    """
    Check if the `x`/`y` coordinate is a vertex of the `polygon`.

        >>> polygon = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))

        >>> is_a_vertex_of_polygon(0.0, 0.0, polygon)
        True

        >>> is_a_vertex_of_polygon(0.5, 0.5, polygon)
        False

    Beware:
        - latitude is `y` and longitude is `x`
        - coordinate and `polygon` must use the same geodesic projection system
    """
    return (x, y) in polygon


def is_within_bounding_box(x, y, minx, miny, maxx, maxy):
    """
    Check if the `x`/`y` coordinate is within the bounding box, defined
    by the `minx`/`miny` coordinate and the `maxx`/`maxy` coordinate.

        >>> is_within_bounding_box(0.5, 0.5, 0.0, 0.0, 1.0, 1.0)
        True

        >>> is_within_bounding_box(0.5, 0.5, 1.0, 1.0, 0.0, 0.0)
        True

        >>> is_within_bounding_box(0.5, 0.5, 1.0, 0.0, 0.0, 1.0)
        True

        >>> is_within_bounding_box(0.5, 0.5, 0.0, 1.0, 1.0, 0.0)
        True

        >>> is_within_bounding_box(2.0, 2.0, 0.0, 0.0, 1.0, 1.0)
        False

        >>> is_within_bounding_box(2.0, 2.0, 1.0, 1.0, 0.0, 0.0)
        False

        >>> is_within_bounding_box(2.0, 2.0, 1.0, 0.0, 0.0, 1.0)
        False

        >>> is_within_bounding_box(2.0, 2.0, 0.0, 1.0, 1.0, 0.0)
        False

    Beware:
        - latitude is `y` and longitude is `x`
        - All parameters must use the same geodesic projection system
    """
    return (
        x >= min(minx, maxx) and x <= max(minx, maxx) and
        y >= min(miny, maxy) and y <= max(miny, maxy)
    )


def is_on_line(x, y, ax, ay, bx, by):
    """
    Check if point `x`/`y` is on the line segment from `ax`/`ay` to `bx`/`by`
    or the degenerate case that all 3 points are coincident.

        >>> is_on_line(0.5, 0.5, 0.0, 0.0, 1.0, 1.0)
        True

        >>> is_on_line(0.0, 0.0, 0.0, 0.0, 1.0, 1.0)
        True

        >>> is_on_line(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        True

        >>> is_on_line(0.0, 0.5, 0.0, 0.0, 1.0, 1.0)
        False

        >>> is_on_line(0.5, 0.0, 0.0, 0.0, 1.0, 1.0)
        False

    """
    return ((bx - ax) * (y - ay) == (x - ax) * (by - ay) and
            ((ax <= x <= bx or bx <= x <= ax) if ax != bx else
             (ay <= y <= by or by <= y <= ay)))


def is_inside_polygon(x, y, polygon):
    """
    Check if the given `x`/`y` coordinate is inside the given `polygon`.

        >>> polygon = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))

        >>> is_inside_polygon(0.0, 0.0, polygon)
        True

        >>> is_inside_polygon(0.0, 0.5, polygon)
        ... # Attention: edge case, this should be True
        False

        >>> is_inside_polygon(0.5, 0.0, polygon)
        ... # Attention: edge case, this should be True
        False

        >>> is_inside_polygon(0.5, 0.5, polygon)
        True

        >>> is_inside_polygon(1.0, 0.5, polygon)
        True

        >>> is_inside_polygon(0.5, 1.0, polygon)
        True

        >>> is_inside_polygon(1.0, 1.0, polygon)
        ... # Attention: edge case, this should be True
        False

        >>> is_inside_polygon(2.0, 0.0, polygon)
        False

        >>> is_inside_polygon(0.0, 2.0, polygon)
        False

        >>> is_inside_polygon(-1.0, -1.0, polygon)
        False

    Beware:
        - latitude is `y` and longitude is `x`
        - coordinate and `polygon` must use the same geodesic projection system
        - this implementation (delibrately) fails for certain edge cases

    This function implements the ray casting algorithm.
    """

    # _infinity is used to act as infinity if we divide by zero
    _infinity = float('+inf')

    # _offset is used to make sure points are not on the same line as vertexes
    _offset = 0.00000001

    # used a few lines below
    _length = len(polygon)

    # we start on the outside of the polygon
    inside = False
    for index, point in enumerate(polygon):
        A = point
        B = polygon[(index + 1) % _length]

        # Make sure A is the lower point of the edge
        if A[1] > B[1]:
            A, B = B, A

        # Make sure point is not at same height as vertex
        if y == A[1]:
            A = (A[0], A[1] - _offset)
        elif y == B[1]:
            B = (B[0], B[1] + _offset)

        if (y > B[1] or y < A[1] or x > max(A[0], B[0])):
            # The horizontal ray does not intersect with the edge
            continue

        if x < min(A[0], B[0]):
            # The ray intersects with the edge
            inside = not inside
            continue

        try:
            edge = (B[1] - A[1]) / (B[0] - A[0])
        except ZeroDivisionError:
            edge = _infinity

        try:
            point = (y - A[1]) / (x - A[0])
        except ZeroDivisionError:
            point = _infinity

        if point >= edge:
            # The ray intersects with the edge
            inside = not inside
            continue

    return inside


def is_on_polygon(x, y, polygon, bounds=None):
    """
    Check if the given `x`/`y` coordinate is on the given `polygon`.
    The `bounds` can given be given as `(minx, miny, maxx, maxy)` to
    speed up the algorithm.

        >>> polygon = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))

        >>> is_on_polygon(0.0, 0.0, polygon)
        True

        >>> is_on_polygon(0.0, 0.5, polygon)
        True

        >>> is_on_polygon(0.5, 0.0, polygon)
        True

        >>> is_on_polygon(0.5, 0.5, polygon)
        True

        >>> is_on_polygon(1.0, 0.5, polygon)
        True

        >>> is_on_polygon(0.5, 1.0, polygon)
        True

        >>> is_on_polygon(1.0, 1.0, polygon)
        True

        >>> is_on_polygon(2.0, 0.0, polygon)
        False

        >>> is_on_polygon(0.0, 2.0, polygon)
        False

        >>> is_on_polygon(-1.0, -1.0, polygon)
        False

    Beware:
        - latitude is `y` and longitude is `x`
        - coordinate and `polygon` must use the same geodesic projection system
    """
    if is_a_vertex_of_polygon(x, y, polygon):
        return True

    if bounds is None:
        minx, maxx = float('+inf'), float('-inf')
        miny, maxy = minx, maxx
        for point in polygon:
            minx = min(minx, point[0])
            miny = min(miny, point[1])
            maxx = max(maxx, point[0])
            maxy = max(maxy, point[1])
    else:
        minx, miny, maxx, maxy = bounds

    if not is_within_bounding_box(x, y, minx, miny, maxx, maxy):
        return False

    if is_inside_polygon(x, y, polygon):
        return True

    # used a few lines below
    _length = len(polygon)

    # make sure point is not an egde case from is_inside_polygon
    for index, point in enumerate(polygon):
        A = point
        B = polygon[(index + 1) % _length]

        if is_on_line(x, y, A[0], A[1], B[0], B[1]):
            return True

    return False
