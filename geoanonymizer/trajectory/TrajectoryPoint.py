# -*- coding: utf-8 -*-

"""
:class:`.TrajectoryPoint` represents points in time.
"""

from geopy.point import Point
from geopy.compat import string_compare, py3k


class TrajectoryPoint(object):  # pylint: disable=R0903,R0921
    """
    Contains a trajectory point, ie. a point in time.  Can be iterated over as
    (timestamp<float>, (latitude<float>, longitude<float>, altitude<float>)).
    Or one can access the properties `timestamp`, `latitude`, `longitude` or
    `altitude`.
    """

    __slots__ = ("_timestamp", "_point", "_tuple", "_raw")

    def __init__(self, timestamp=None, point=None):
        self._timestamp = timestamp
        if point is None:
            self._point = (None, None, None)
        elif isinstance(point, Point):
            self._point = point
        elif isinstance(point, string_compare):
            self._point = Point(point)
        elif isinstance(point, (tuple, list)):
            self._point = Point(point)
        else:
            raise TypeError(
                "point an unsupported type: %r; use %r or Point",
                type(point), type(string_compare)
            )
        self._tuple = (self._timestamp,
                       (self._point[0], self._point[1], self._point[2]))

    @property
    def timestamp(self):
        """
        Timestamp as a float.

        :rtype: float or None
        """
        return self._timestamp

    @property
    def latitude(self):
        """
        Location's latitude.

        :rtype: float or None
        """
        return self._point[0]

    @property
    def longitude(self):
        """
        Location's longitude.

        :rtype: float or None
        """
        return self._point[1]

    @property
    def altitude(self):
        """
        Location's altitude.

        :rtype: float or None
        """
        return self._point[2]

    @property
    def point(self):
        """
        :class:`geopy.point.Point` instance representing the location's
        latitude, longitude, and altitude.

        :rtype: :class:`geopy.point.Point` or None
        """
        return self._point if self._point != (None, None, None) else None

    def __getitem__(self, index):
        """
        Backwards compatibility with geopy<0.98 tuples.
        """
        return self._tuple[index]

    def __repr__(self):
        return "TrajectoryPoint(%s, (%s, %s, %s))" % (
            self._timestamp, self.latitude, self.longitude, self.altitude
        )

    __unicode__ = __repr__

    __str__ = __unicode__

    def __iter__(self):
        return iter(self._tuple)

    def __eq__(self, other):
        return (
            isinstance(other, TrajectoryPoint) and
            self._timestamp == other._timestamp and  # pylint: disable=W0212
            self._point == other._point
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):  # pragma: no cover
        return len(self._tuple)
