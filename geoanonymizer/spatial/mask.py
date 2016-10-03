# -*- coding: utf-8 -*-

from geopy.point import Point
import random

def mask_by_limiting_precision(point, precisions = Point(0.0, 0.0, 0.0)):
    """
    Masked points have a limited precision, hence we cut decimal places.
    """
    def _limit_precision(value, precision):
        if 0 is precision or 0 < precision:
            value  = round(value,  int(precision))
        else if 0 > precision:
            precision *= -10
            latitude  = round(value  / precision) * precision
        return value

    latitude,  longitude,  altitude  = point
    platitude, plongitude, paltitude = precisions

    latitude  = _limit_precision(latitude,  platitude)
    longitude = _limit_precision(longitude, plongitude)
    altitude  = _limit_precision(altitude,  paltitude)

    return Point(latitude, longitude, altitude)

def mask_by_fixed_vector(point, vector = Point(1.0, 1.0, 1.0)):
    """
    Masked points are displaced by a fixed vector, hence we move the point.
    """
    latitude,  longitude,  altitude  = point
    vlatitude, vlongitude, valtitude = vector
    return Point(latitude  + vlatitude,
                 longitude + vlongitude,
                 altitude  + valtitude)

###
# The following implementations are partially based upon the descriptions from
# section 7 of `Ensuring Confidentiality of Geocoded Health Data: Assessing
# Geographic Masking Strategies for Individual-Level Data
# <https://www.hindawi.com/journals/amed/2014/567049/#sec7>`.
###

def mask_by_random_direction_and_fixed_radius_on_a_circle(point, radius = 1.0):
    """
    Masked points are placed on a random location on a circle around the
    original location.  Masked points are not placed inside the circle itself.
    """
    latitude, longitude, altitude = point

    s = random.uniform(0, 360) * Math.PI / 180
    x = radius * cos(s)
    y = radius * sin(s)

    return mask_by_fixed_vector(point, Point(x, y, 0))

def mask_by_random_direction_and_fixed_radius_on_a_sphere(point, radius = 1.0):
    """
     Masked points are placed on a random location on a sphere around the
    original location.  Masked points are not placed inside the sphere itself.
    """
    latitude, longitude, altitude = point

    s = random.uniform(0, 360) * Math.PI / 180
    t = random.uniform(0, 360) * Math.PI / 180
    x = radius * cos(s) * sin(t)
    y = radius * sin(s) * sin(t)
    z = radius * cos(t)

    return mask_by_fixed_vector(point, Point(x, y, z))

def mask_by_random_perturbation_within_a_circle(point, radius = 1.0):
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
    """
    radius = random.uniform(0, radius)
    return mask_by_random_direction_and_fixed_radius_on_a_circle(point, radius)

def mask_by_random_perturbation_within_a_sphere(point, radius = 1.0):
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
    """
    radius = random.uniform(0, radius)
    return mask_by_random_direction_and_fixed_radius_on_a_sphere(point, radius)

def mask_by_circular_gaussian_displacement(point, mean = 1.0, sigma = 1.0):
    """
    The direction of displacement is random, but the distance follows a Gaussian
    distribution.  The dispersion of the distribution can be varied based on
    other parameters of interest, such as local population density.
    """
    radius = random.gauss(mean, sigma)
    return mask_by_random_direction_and_fixed_radius_on_a_circle(point, radius)

def mask_by_spherical_gaussian_displacement(point, mean = 1.0, sigma = 1.0):
    """
    The direction of displacement is random, but the distance follows a Gaussian
    distribution.  The dispersion of the distribution can be varied based on
    other parameters of interest, such as local population density.
    """
    radius = random.gauss(mean, sigma)
    return mask_by_random_direction_and_fixed_radius_on_a_sphere(point, radius)

def mask_by_random_perturbation_within_a_circular_donut(point,
                                                        radius_inner = 0.5,
                                                        radius_outer = 1.0):
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
    """
    radius = random.uniform(radius_inner, radius_outer)
    return mask_by_random_direction_and_fixed_radius_on_a_circle(point, radius)

def mask_by_random_perturbation_within_a_spherical_donut(point,
                                                         radius_inner = 0.5,
                                                         radius_outer = 1.0):
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
    """
    radius = random.uniform(radius_inner, radius_outer)
    return mask_by_random_direction_and_fixed_radius_on_a_sphere(point, radius)

def mask_by_circular_bimodal_gaussian_displacement(point,
                                                   inner_mean = 1.0,
                                                   inner_sigma = 1.0,
                                                   outer_mean = 2.0,
                                                   outer_sigma = 1.0):
    """
    This is a variation on the Gaussian masking technique, employing a bimodal
    Gaussian distribution for the random distance function.  In effect, this
    approximates donut masking, but with a less uniform probability of
    placement.
    """
    inner_radius = random.gauss(inner_mean, inner_sigma)
    outer_radius = random.gauss(outer_mean, outer_sigma)
    return mask_by_random_perturbation_within_a_circular_donut(point,
                                                               inner_radius,
                                                               outer_radius)

def mask_by_spherical_bimodal_gaussian_displacement(point,
                                                   inner_mean = 1.0,
                                                   inner_sigma = 1.0,
                                                   outer_mean = 2.0,
                                                   outer_sigma = 1.0):
    """
    This is a variation on the Gaussian masking technique, employing a bimodal
    Gaussian distribution for the random distance function.  In effect, this
    approximates donut masking, but with a less uniform probability of
    placement.
    """
    inner_radius = random.gauss(inner_mean, inner_sigma)
    outer_radius = random.gauss(outer_mean, outer_sigma)
    return mask_by_random_perturbation_within_a_spherical_donut(point,
                                                                inner_radius,
                                                                outer_radius)
