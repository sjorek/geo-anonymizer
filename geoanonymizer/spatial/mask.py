# -*- coding: utf-8 -*-

"""
Functions to mask spatial coordinates.

This implementation is inspired by section 7 of `Ensuring Confidentiality of
Geocoded Health Data: Assessing Geographic Masking Strategies for Individual-
Level Data <https://www.hindawi.com/journals/amed/2014/567049/#sec7>`.
"""

from geopy.point import Point
import math
import random


def _random_angle_in_radians():
    # This version uses human readable degrees, be reduces precision:
    # random.uniform(0, 360) * math.pi / 180

    # Therefore we simplfy implementaion by calculating directly in radians:
    return random.uniform(0, 2 * math.pi)


def limit_precision(point, precisions=(None, None, None)):
    """
    Masked points have a limited precision, hence we cut decimal places.

    In the given `precisions` tupel positive integers simply cut decimal places
    after the comma.  Negative integers define the amount decimals to keep
    before the comma, while cutting all decimal places after the comma.  In
    both cases standard mathematical rounding is applied to the first digit
    which won't be cut, before cutting the other digits.  The first value is
    the longitude's precision, the second value is the latitude's precision and
    the third value is the altitude's precision.

    If we define a coordinate like …

        >>> coordinate = Point(12.3456, 12.3456, 123.456)

    … and call this function like …

        >>> limit_precision(coordinate)
        Point(12.3456, 12.3456, 123.456)

        >>> limit_precision(coordinate, (0, 0, 0))
        Point(12.3456, 12.3456, 123.456)

        >>> limit_precision(coordinate, (None, None, None))
        Point(12.3456, 12.3456, 123.456)

    … the given point returns unchanged.

    If we assign to the second parameter tuple some positive integers the given
    point will return with altered decimal places after the comma and rounding
    applied:

        >>> limit_precision(coordinate, (1, 1, 1))
        Point(12.3, 12.3, 123.5)

        >>> limit_precision(coordinate, (2, 2, 2))
        Point(12.35, 12.35, 123.46)

        >>> limit_precision(coordinate, (3, 3, 3))
        Point(12.346, 12.346, 123.456)

    Assigning negative integers to the second parameter tuple will return a
    point with altered decimal places before the comma and all decimal places
    cut after the comma:

        >>> limit_precision(coordinate, (-1, -1, -1))
        Point(10.0, 10.0, 120.0)

        >>> limit_precision(coordinate, (-2, -2, -2))
        Point(10.0, 10.0, 100.0)

    Mind that decimals with less digits than the given absolute precision, keep
    the last remaining digit intact.

        >>> limit_precision(coordinate, (-3, -3, -3))
        Point(10.0, 10.0, 100.0)

    The mathematical rounding can lead to unexpected results, if applied before
    the comma:

        >>> limit_precision(Point(65.4321, 65.4321, 654.321), (-1, -1, -1))
        Point(70.0, 70.0, 650.0)

        >>> limit_precision(Point(65.4321, 65.4321, 654.321), (-2, -2, -2))
        Point(70.0, 70.0, 700.0)

    """
    def _limit(value, precision):
        if 0 < precision:
            value = round(value, precision)
        elif 0 > precision:
            calculus = 10 ** (-1 * precision)
            if calculus < value:
                value = round(value / calculus) * calculus
            else:
                value = _limit(value, precision + 1)
        return value

    return Point(
        _limit(point[0], precisions[0] or 0),
        _limit(point[1], precisions[1] or 0),
        _limit(point[2], precisions[2] or 0)
    )


def add_vector(point, vector=(None, None, None)):
    """
    Masked points are displaced by a fixed vector, hence we move the point.

    If we define a coordinate like …

        >>> coordinate = Point(12.3456, 12.3456, 12.3456)

    … and call this function like …

        >>> add_vector(coordinate)
        Point(12.3456, 12.3456, 12.3456)

        >>> add_vector(coordinate, (0, 0, 0))
        Point(12.3456, 12.3456, 12.3456)

        >>> add_vector(coordinate, (None, None, None))
        Point(12.3456, 12.3456, 12.3456)

    … the given point returns unchanged.

    In all other cases the given point will be moved by the given values:

        >>> add_vector(coordinate, (1.0, 1.0, 1.0))
        Point(13.3456, 13.3456, 13.3456)

    Mind that geodetic points with latitude, longitude, and altitude are used.
    This results in points with limited value range, hence we rotate the points
    around the globe:

        >>> add_vector(coordinate, (100.0, 100.0, 100.0))
        Point(-67.65440000000001, 112.3456, 112.3456)

        >>> add_vector(coordinate, (-100.0, -100.0, -100.0))
        Point(-87.6544, -87.6544, -87.6544)

    """

    return Point(
        point[0] + (vector[0] or 0.0),
        point[1] + (vector[1] or 0.0),
        point[2] + (vector[2] or 0.0)
    )


def displace_on_a_circle(point, radius=0.0):
    """
    Masked points are placed on a random location on a circle around the
    original location.  Masked points are not placed inside the circle itself.

    If we define a coordinate like …

        >>> coordinate = Point(0.0, 0.0, 0.0)

    … and call this function without any radius …

        >>> displace_on_a_circle(coordinate)
        Point(0.0, 0.0, 0.0)

        >>> displace_on_a_circle(coordinate, 0)
        Point(0.0, 0.0, 0.0)

        >>> displace_on_a_circle(coordinate, None)
        Point(0.0, 0.0, 0.0)

    … the given point returns unchanged.

    With a given radius, a randomly circular displaced point will return.  That
    implies the altitude always remains untouched.  The given coodinates are
    the circle's center, the given radius is the distance between given and
    resulting coodinate:

        >>> displace_on_a_circle(coordinate, 1) # doctest: +ELLIPSIS
        Point(..., 0.0)

        >>> displace_on_a_circle(coordinate, -1) # doctest: +ELLIPSIS
        Point(..., 0.0)

        >>> random.seed(1)
        >>> displace_on_a_circle(coordinate, 1)
        Point(0.6643029539301958, 0.7474634341555553, 0.0)

    """

    if radius is None or radius is 0:
        return point
    elif 0 > radius:
        radius *= -1

    a = _random_angle_in_radians()
    x = math.cos(a) * radius
    y = math.sin(a) * radius

    return add_vector(point, (x, y, 0))


def displace_on_a_sphere(point, radius=0.0):
    """
     Masked points are placed on a random location on a sphere around the
    original location.  Masked points are not placed inside the sphere itself.

    If we define a coordinate like …

        >>> coordinate = Point(0.0, 0.0, 0.0)

    … and call this function without any radius …

        >>> displace_on_a_sphere(coordinate)
        Point(0.0, 0.0, 0.0)

        >>> displace_on_a_sphere(coordinate, 0)
        Point(0.0, 0.0, 0.0)

        >>> displace_on_a_sphere(coordinate, None)
        Point(0.0, 0.0, 0.0)

    … the given point returns unchanged.

    With a given radius, a randomly spherical displaced point will return.  The
    given coodinates are the sphere's center, the given radius is the distance
    between given and resulting coodinate:

        >>> displace_on_a_sphere(coordinate, 1) # doctest: +ELLIPSIS
        Point(...)

        >>> displace_on_a_sphere(coordinate, -1) # doctest: +ELLIPSIS
        Point(...)

        >>> random.seed(1)
        >>> displace_on_a_sphere(coordinate, 1)
        Point(-0.5436582607079324, -0.6117158867827159, 0.5746645712253897)

    """

    if radius is None or radius is 0:
        return point
    elif 0 > radius:
        radius *= -1

    a1 = _random_angle_in_radians()
    a2 = _random_angle_in_radians()
    x = math.cos(a1) * math.sin(a2) * radius
    y = math.sin(a1) * math.sin(a2) * radius
    z = math.cos(a2) * radius

    return add_vector(point, Point(x, y, z))


def displace_within_a_circle(point, radius=0.0):
    """
    Masked locations are placed anywhere within a circular area around the
    original location.  Since every location within the circle is equally
    likely, masked locations are more likely to be placed at larger distances
    compared to small distances.  A variation on this technique is the use of
    random direction and random radius.  In this technique, masked points are
    displaced using a vector with random direction and random radius.  The
    radius is constrained by a maximum value. This effectively results in a
    circular area where masked locations can be placed, but the masked
    locations are as likely to be at large distances compared to small
    distances.  These two techniques therefore only differ slightly in the
    probability of how close masked locations are placed to the original
    locations.

    If we define a coordinate like …

        >>> coordinate = Point(0.0, 0.0, 0.0)

    … and call this function without any radius …

        >>> displace_within_a_circle(coordinate)
        Point(0.0, 0.0, 0.0)

        >>> displace_within_a_circle(coordinate, 0)
        Point(0.0, 0.0, 0.0)

        >>> displace_within_a_circle(coordinate, None)
        Point(0.0, 0.0, 0.0)

    … the given point returns unchanged.

    With a given radius, a randomly circular displaced point will return.  That
    implies the altitude always remains untouched.  The given coodinates are
    the circle's center, the given radius is the maximum distance between given
    and resulting coodinate:

        >>> displace_within_a_circle(coordinate, 1) # doctest: +ELLIPSIS
        Point(..., 0.0)

        >>> displace_within_a_circle(coordinate, -1) # doctest: +ELLIPSIS
        Point(..., 0.0)

        >>> random.seed(1)
        >>> displace_within_a_circle(coordinate, 1)
        Point(0.07721437073087664, -0.10996222555283103, 0.0)

    """

    if radius is None or radius is 0:
        return point
    elif 0 > radius:
        radius *= -1

    radius = random.uniform(0, radius)

    return displace_on_a_circle(point, radius)


def displace_within_a_sphere(point, radius=0.0):
    """
    Masked locations are placed anywhere within a spherical space around the
    original location.  Since every location within the sphere is equally
    likely, masked locations are more likely to be placed at larger distances
    compared to small distances.  A variation on this technique is the use of
    random direction and random radius.  In this technique, masked points are
    displaced using a vector with random direction and random radius.  The
    radius is constrained by a maximum value. This effectively results in a
    spherical space where masked locations can be placed, but the masked
    locations are as likely to be at large distances compared to small
    distances.  These two techniques therefore only differ slightly in the
    probability of how close masked locations are placed to the original
    locations.

    If we define a coordinate like …

        >>> coordinate = Point(0.0, 0.0, 0.0)

    … and call this function with any radius …

        >>> displace_within_a_sphere(coordinate)
        Point(0.0, 0.0, 0.0)

        >>> displace_within_a_sphere(coordinate, 0)
        Point(0.0, 0.0, 0.0)

        >>> displace_within_a_sphere(coordinate, None)
        Point(0.0, 0.0, 0.0)

    … the given point returns unchanged.

    With a given radius, a randomly spherical displaced point will return.  The
    given coodinates are the sphere's center, the given radius is the maximum
    distance between given and resulting coodinate:

        >>> displace_within_a_sphere(coordinate, 1) # doctest: +ELLIPSIS
        Point(...)

        >>> displace_within_a_sphere(coordinate, -1) # doctest: +ELLIPSIS
        Point(...)

        >>> random.seed(1)
        >>> displace_within_a_sphere(coordinate, 1)
        Point(-0.07692535867829137, 0.10955063884671598, 0.011614508874230087)

    """

    if radius is None or radius is 0:
        return point
    elif 0 > radius:
        radius *= -1

    radius = random.uniform(0, radius)

    return displace_on_a_sphere(point, radius)


def displace_within_a_circular_donut(point,
                                     radius_inner=0.5,
                                     radius_outer=1.0):
    """
    This technique is similar to random displacement within a circle, but a
    smaller internal circle is utilized within which displacement is not
    allowed.  In effect, this sets a minimum and maximum level for the
    displacement.  Masked locations are placed anywhere within the allowable
    area.  A slightly different approach to donut masking is the use of a
    random direction and two random radii: one for maximum and one for minimum
    displacement.  These two techniques only differ slightly in the probability
    of how close masked locations are placed to the original locations.  Both
    approaches enforce a minimum amount of displacement.

    With a given radius, a randomly circular displaced point will return.  That
    implies the altitude always remains untouched.  The given coodinates are
    the circle's center, the given radii are the minimum and maximum distance
    between given and resulting coodinate:

        >>> coordinate = Point(0.0, 0.0, 0.0)

        >>> random.seed(1)
        >>> displace_within_a_circular_donut(coordinate)
        Point(0.32593947097813314, -0.4641756357658914, 0.0)

        >>> random.seed(1)
        >>> displace_within_a_circular_donut(coordinate, 0.5, 1.0)
        Point(0.32593947097813314, -0.4641756357658914, 0.0)

    """

    radius = random.uniform(radius_inner, radius_outer)

    return displace_on_a_circle(point, radius)


def displace_within_a_spherical_donut(point,
                                      radius_inner=0.5,
                                      radius_outer=1.0):
    """
    This technique is similar to random displacement within a sphere, but a
    smaller internal sphere is utilized within which displacement is not
    allowed.  In effect, this sets a minimum and maximum level for the
    displacement.  Masked locations are placed anywhere within the allowable
    space.  A slightly different approach to donut masking is the use of a
    random direction and two random radii: one for maximum and one for minimum
    displacement.  These two techniques only differ slightly in the probability
    of how close masked locations are placed to the original locations.  Both
    approaches enforce a minimum amount of displacement.

    With a given radius, a randomly spherical displaced point will return.  The
    given coodinates are the sphere's center, the given radii are the minimum
    and maximum distance between given and resulting coodinate:

        >>> coordinate = Point(0.0, 0.0, 0.0)

        >>> random.seed(1)
        >>> displace_within_a_spherical_donut(coordinate)
        Point(-0.32471948518229893, 0.4624382343989833, 0.049027491156171304)

        >>> random.seed(1)
        >>> displace_within_a_spherical_donut(coordinate, 0.5, 1.0)
        Point(-0.32471948518229893, 0.4624382343989833, 0.049027491156171304)

    """

    radius = random.uniform(radius_inner, radius_outer)

    return displace_on_a_sphere(point, radius)


def circular_gaussian_displacement(point, mu=1.0, sigma=1.0):
    """
    The direction of displacement is random, but the distance follows a
    Gaussian distribution, where `mu` is the mean and `sigma` is the standard
    deviation.  The dispersion of the distribution can be varied based on other
    parameters of interest, such as local population density.

    With a given radius, a randomly circular displaced point will return.  That
    implies the altitude always remains untouched.  The given coodinates are
    the circle's center:

        >>> coordinate = Point(0.0, 0.0, 0.0)

        >>> random.seed(1)
        >>> circular_gaussian_displacement(coordinate)
        Point(0.19779177337662887, -2.279620117247094, 0.0)

        >>> random.seed(1)
        >>> circular_gaussian_displacement(coordinate, 1.0, 1.0)
        Point(0.19779177337662887, -2.279620117247094, 0.0)

    """

    radius = random.gauss(mu, sigma)

    return displace_on_a_circle(point, radius)


def spherical_gaussian_displacement(point, mu=1.0, sigma=1.0):
    """
    The direction of displacement is random, but the distance follows a
    Gaussian distribution, where `mu` is the mean and `sigma` is the standard
    deviation.  The dispersion of the distribution can be varied based on other
    parameters of interest, such as local population density.

    With a given radius, a randomly spherical displaced point will return.  The
    given coodinates are the sphere's center:

        >>> coordinate = Point(0.0, 0.0, 0.0)

        >>> random.seed(1)
        >>> spherical_gaussian_displacement(coordinate)
        Point(0.19769146198725365, -2.278463993019554, -0.07286551271936394)

        >>> random.seed(1)
        >>> spherical_gaussian_displacement(coordinate, 1.0, 1.0)
        Point(0.19769146198725365, -2.278463993019554, -0.07286551271936394)

    """

    radius = random.gauss(mu, sigma)

    return displace_on_a_sphere(point, radius)


def circular_bimodal_gaussian_displacement(point,
                                           inner_mu=1.0,
                                           inner_sigma=1.0,
                                           outer_mu=2.0,
                                           outer_sigma=1.0):
    """
    This is a variation on the Gaussian masking technique, employing a bimodal
    Gaussian distribution for the random distance function.  In effect, this
    approximates donut masking, but with a less uniform probability of
    placement.

    With a given radius, a randomly circular displaced point will return.  That
    implies the altitude always remains untouched.  The given coodinates are
    the circle's center:

        >>> coordinate = Point(0.0, 0.0, 0.0)

        >>> random.seed(1)
        >>> circular_bimodal_gaussian_displacement(coordinate)
        Point(-0.10110949606778825, 3.1735160345853632, 0.0)

        >>> random.seed(1)
        >>> circular_bimodal_gaussian_displacement(coordinate,
        ...                                        1.0, 1.0, 2.0, 1.0)
        Point(-0.10110949606778825, 3.1735160345853632, 0.0)

    """

    inner_radius = random.gauss(inner_mu, inner_sigma)
    outer_radius = random.gauss(outer_mu, outer_sigma)

    return displace_within_a_circular_donut(point, inner_radius, outer_radius)


def spherical_bimodal_gaussian_displacement(point,
                                            inner_mu=1.0,
                                            inner_sigma=1.0,
                                            outer_mu=2.0,
                                            outer_sigma=1.0):
    """
    This is a variation on the Gaussian masking technique, employing a bimodal
    Gaussian distribution for the random distance function.  In effect, this
    approximates donut masking, but with a less uniform probability of
    placement.

    With a given radius, a randomly spherical displaced point will return.  The
    given coodinates are the sphere's center:

        >>> coordinate = Point(0.0, 0.0, 0.0)

        >>> random.seed(1)
        >>> spherical_bimodal_gaussian_displacement(coordinate)
        Point(-0.002899644539981792, 0.09101092182341257, -3.173820372380246)

        >>> random.seed(1)
        >>> spherical_bimodal_gaussian_displacement(coordinate,
        ...                                         1.0, 1.0, 2.0, 1.0)
        Point(-0.002899644539981792, 0.09101092182341257, -3.173820372380246)

    """

    inner_radius = random.gauss(inner_mu, inner_sigma)
    outer_radius = random.gauss(outer_mu, outer_sigma)

    return displace_within_a_spherical_donut(point, inner_radius, outer_radius)
