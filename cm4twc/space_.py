import numpy as np
import cf


class SpaceDomain(object):
    """SpaceDomain characterises a spatial dimension that is needed by a
    `Component`. Any supported spatial configuration for a `Component`
    is a subclass of SpaceDomain.

    TODO: create a XYGrid subclass for Cartesian coordinates
    TODO: deal with sub-grid heterogeneity schemes (e.g. tiling, HRUs)
    """

    def __init__(self):
        self._f = cf.Field()

    @property
    def shape(self):
        return None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.is_space_equal_to(other._f)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_space_equal_to(self, *args):
        raise TypeError("An instance of {} cannot be used to "
                        "characterise a spatial configuration directly, "
                        "please use a subclass of it instead.")

    def to_field(self):
        """Return the inner cf.Field used to characterise the
        SpaceDomain.
        """
        return self._f


class Grid(SpaceDomain):
    """Grid is a `SpaceDomain` subclass which represents space as
    a regular grid. Any supported regular grid for a `Component` is a
    subclass of Grid.
    """

    def __init__(self):
        super(Grid, self).__init__()

    @property
    def shape(self):
        """Return the size of each of the dimension coordinates of
         the SpaceDomain instance as a `tuple`, corresponding, in order,
         to {Z, Y, X} if the Z-axis exists, to {Y, X} otherwise."""
        has_altitude = self._f.has_construct('altitude')
        return (
            (self._f.construct('Z').shape if has_altitude else ())
            + self._f.construct('Y').shape
            + self._f.construct('X').shape
        )

    @property
    def Z(self):
        """Return the Z-axis of the SpaceDomain instance as a `cf.Data`
        instance if the Z-axis exists, otherwise return None.
        """
        if self._f.has_construct('Z'):
            return self._f.construct('Z').data
        else:
            return None

    @property
    def Y(self):
        """Return the Y-axis of the SpaceDomain instance as a `cf.Data`
        instance.
        """
        return self._f.construct('Y').data

    @property
    def X(self):
        """Return the X-axis of the SpaceDomain instance as a `cf.Data`
        instance.
        """
        return self._f.construct('X').data

    @property
    def Z_bounds(self):
        """Return the bounds of the Z-axis of the SpaceDomain instance
        as a `cf.Data` instance if the Z-axis exists, otherwise
        return None.
        """
        if self._f.has_construct('Z'):
            return self._f.construct('Z').bounds.data
        else:
            return None

    @property
    def Y_bounds(self):
        """Return the bounds of the Y-axis of the SpaceDomain instance
        as a `cf.Data` instance.
        """
        return self._f.construct('Y').bounds.data

    @property
    def X_bounds(self):
        """Return the bounds of the X-axis of the SpaceDomain instance
        as a `cf.Data` instance.
        """
        return self._f.construct('X').bounds.data

    def _set_space(self, dimension, dimension_bounds, name, units, axis):
        if not isinstance(dimension, np.ndarray):
            dimension = np.asarray(dimension)
        dimension = np.squeeze(dimension)
        if not isinstance(dimension_bounds, np.ndarray):
            dimension_bounds = np.asarray(dimension_bounds)
        dimension_bounds = np.squeeze(dimension_bounds)
        if dimension.ndim > 1:
            raise RuntimeError("Error when initialising a {}: the "
                               "{} array given is not convertible to a "
                               "1D-array.".format(
                                    name, self.__class__.__name__))
        if dimension_bounds.shape != (*dimension.shape, 2):
            raise RuntimeError("Error when initialising a {}: the {} bounds "
                               "array given is not compatible in size with "
                               "the {} array given.".format(
                                    self.__class__.__name__, name, name))
        axis_lat = self._f.set_construct(cf.DomainAxis(dimension.size))
        self._f.set_construct(
            cf.DimensionCoordinate(
                properties={
                    'standard_name': name,
                    'units': units,
                    'axis': axis
                },
                data=cf.Data(dimension),
                bounds=cf.Bounds(data=cf.Data(dimension_bounds))),
            axes=axis_lat
        )

    def __repr__(self):
        has_altitude = self._f.has_construct('altitude')
        return "\n".join(
            ["{}(".format(self.__class__.__name__)]
            + ["    shape {}: {}".format("{Z, Y, X}" if has_altitude
                                         else "{Y, X}", self.shape)]
            + (["    Z, %s %s: %s" %
                (self._f.construct('Z').standard_name,
                 self._f.construct('Z').data.shape,
                 self._f.construct('Z').data)] if has_altitude else [])
            + ["    Y, %s %s: %s" %
               (self._f.construct('Y').standard_name,
                self._f.construct('Y').data.shape,
                self._f.construct('Y').data)]
            + ["    X, %s %s: %s" %
               (self._f.construct('X').standard_name,
                self._f.construct('X').data.shape,
                self._f.construct('X').data)]
            + (["    Z_bounds %s: %s" %
                (self._f.construct('Z').bounds.data.shape,
                 self._f.construct('Z').bounds.data)] if has_altitude else [])
            + ["    Y_bounds %s: %s" %
               (self._f.construct('Y').bounds.data.shape,
                self._f.construct('Y').bounds.data)]
            + ["    X_bounds %s: %s" %
               (self._f.construct('X').bounds.data.shape,
                self._f.construct('X').bounds.data)]
            + [")"]
        )


class LatLonGrid(Grid):
    """LatLonGrid characterises the spatial dimension for a `Component`
    as a regular grid on a spherical domain whose coordinates are
    latitudes and longitudes, and whose rotation axis is aligned with
    the North pole.
    """

    def __init__(self, latitude, longitude, latitude_bounds,
                 longitude_bounds, altitude=None, altitude_bounds=None):
        """**Initialisation**

        :Parameters:

            latitude: one-dimensional array-like object
                The array of latitude coordinates in degrees North
                defining the temporal dimension. May be any type that
                can be cast to a `numpy.array`. Must contain numerical
                values.

                *Parameter example:*
                    ``latitude=[15, 45, 75]``
                *Parameter example:*
                    ``latitude=(-60, 0, 60)``
                *Parameter example:*
                    ``latitude=numpy.arange(-89.5, 90.5, 1)``

            longitude: one-dimensional array-like object
                The array of longitude coordinates in degrees East
                defining the temporal dimension. May be any type that
                can be cast to a `numpy.array`. Must contain numerical
                values.

                *Parameter example:*
                    ``longitude=[30, 90, 150]``
                *Parameter example:*
                    ``longitude=(-150, -90, -30, 30, 90, 150)``
                *Parameter example:*
                    ``longitude=numpy.arange(-179.5, 180.5, 1)``

            latitude_bounds: two-dimensional array-like object
                The array of latitude coordinate bounds in degrees North
                defining the extent of the grid cell around the
                coordinate. May be any type that can be cast to a
                `numpy.array`. Must be two dimensional with the first
                dimension equal to the size of `latitude` and the second
                dimension equal to 2. Must contain numerical values.

                *Parameter example:*
                    ``latitude_bounds=[[0, 30], [30, 60], [60, 90]]``
                *Parameter example:*
                    ``latitude_bounds=((-90, -30), (-30, 30), (30, 90))``
                *Parameter example:*
                    ``latitude_bounds=numpy.column_stack(
                        (numpy.arange(-90, 90, 1),
                         numpy.arange(-89, 91, 1))
                    )``

            longitude_bounds: two-dimensional array-like object
                The array of longitude coordinate bounds in degrees
                East defining the extent of the grid cell around the
                coordinate. May be any type that can be cast to a
                `numpy.array`. Must feature two dimensional with the
                first dimension equal to the size of `longitude` and the
                second dimension equal to 2. Must contain numerical
                values.

                *Parameter example:*
                    ``longitude_bounds=[[0, 60], [60, 120], [120, 180]]``
                *Parameter example:*
                    ``longitude_bounds=((-180, -120), (-120, -60), (-60, 0)
                                        (0, 60), (60, 120), (120, 180))``
                *Parameter example:*
                    ``longitude_bounds=numpy.column_stack(
                        (numpy.arange(-180, 180, 1),
                         numpy.arange(-179, 181, 1))
                    )``

            altitude: one-dimensional array-like object, optional
                The array of altitude coordinates in metres defining the
                temporal dimension. May be any type that can be cast to
                a `numpy.array`. Must contain numerical values. Ignored
                if `altitude_bounds` not also provided.

                *Parameter example:*
                    ``altitude=[10]``

            altitude_bounds: two-dimensional array-like object, optional
                The array of altitude coordinate bounds in metres
                defining the extent of the grid cell around the
                coordinate. May be any type that can be cast to a
                `numpy.array`. Must be two dimensional with the first
                dimension equal to the size of `altitude` and the second
                dimension equal to 2. Must contain numerical values.
                Ignored if `altitude` not also provided.

                *Parameter example:*
                    ``altitude=[[0, 20]]``

        **Examples**

        >>> import numpy
        >>> sd = LatLonGrid(
        ...     latitude=[15, 45, 75],
        ...     longitude=[30, 90, 150],
        ...     latitude_bounds=[[0, 30], [30, 60], [60, 90]],
        ...     longitude_bounds=[[0, 60], [60, 120], [120, 180]]
        ... )
        >>> print(sd)
        LatLonGrid(
            shape {Y, X}: (3, 3)
            Y, latitude (3,): [15, 45, 75] degrees_north
            X, longitude (3,): [30, 90, 150] degrees_east
            Y_bounds (3, 2): [[0, ..., 90]] degrees_north
            X_bounds (3, 2): [[0, ..., 180]] degrees_east
        )
        >>> sd = LatLonGrid(
        ...     latitude=numpy.arange(-89.5, 90.5, 1),
        ...     longitude=numpy.arange(-179.5, 180.5, 1),
        ...     latitude_bounds=numpy.column_stack(
        ...         (numpy.arange(-90, 90, 1),
        ...          numpy.arange(-89, 91, 1))
        ...     ),
        ...     longitude_bounds=numpy.column_stack(
        ...         (numpy.arange(-180, 180, 1),
        ...          numpy.arange(-179, 181, 1))
        ...     ),
        ...     altitude=[10],
        ...     altitude_bounds=[[0, 10]]
        ... )
        >>> print(sd)
        LatLonGrid(
            shape {Z, Y, X}: (1, 180, 360)
            Z, altitude (1,): [10] m
            Y, latitude (180,): [-89.5, ..., 89.5] degrees_north
            X, longitude (360,): [-179.5, ..., 179.5] degrees_east
            Z_bounds (1, 2): [[0, 10]] m
            Y_bounds (180, 2): [[-90, ..., 90]] degrees_north
            X_bounds (360, 2): [[-180, ..., 180]] degrees_east
        )
        """
        super(LatLonGrid, self).__init__()

        if altitude is not None and altitude_bounds is not None:
            self._set_space(altitude, altitude_bounds,
                            name='altitude', units='m', axis='Z')
            self._f.construct('Z').set_property('positive', 'up')

        self._set_space(latitude, latitude_bounds,
                        name='latitude', units='degrees_north', axis='Y')
        self._set_space(longitude, longitude_bounds,
                        name='longitude', units='degrees_east', axis='X')

    def is_space_equal_to(self, field, ignore_altitude=False):
        # check if latitude match, check if longitude
        lat_lon = (
            self._f.construct('latitude').equals(
                field.construct('latitude', default=None),
                ignore_data_type=True)
            and self._f.construct('longitude').equals(
                field.construct('longitude', default=None),
                ignore_data_type=True)
        )
        # check whether altitude constructs are identical
        if ignore_altitude:
            alt = True
        else:
            if self._f.has_construct('altitude'):
                alt = self._f.construct('altitude').equals(
                    field.construct('altitude', default=None),
                    ignore_data_type=True)
            else:
                alt = True

        return lat_lon and alt

    @classmethod
    def from_field(cls, field):
        """Initialise a `LatLonGrid` from a cf.Field instance.

        :Parameters:

            field: cf.Field object
                The field object who will be used to initialise a
                'LatLonGrid` instance. This field must feature a
                'latitude' and a 'longitude' constructs, and these
                constructs must feature bounds. This field may
                optionally feature an 'altitude' construct alongside its
                bounds (both required otherwise ignored).

        **Examples**

        >>> import cf
        >>> f = cf.Field()
        >>> lat = f.set_construct(
        ...     cf.DimensionCoordinate(
        ...         properties={'standard_name': 'latitude',
        ...                     'units': 'degrees_north',
        ...                     'axis': 'Y'},
        ...         data=cf.Data([15, 45, 75]),
        ...         bounds=cf.Bounds(data=cf.Data([[0, 30], [30, 60], [60, 90]]))
        ...     ),
        ...     axes=f.set_construct(cf.DomainAxis(size=3))
        ... )
        >>> lon = f.set_construct(
        ...     cf.DimensionCoordinate(
        ...         properties={'standard_name': 'longitude',
        ...                     'units': 'degrees_east',
        ...                     'axis': 'X'},
        ...         data=cf.Data([30, 90, 150]),
        ...         bounds=cf.Bounds(data=cf.Data([[0, 60], [60, 120], [120, 180]]))
        ...     ),
        ...     axes=f.set_construct(cf.DomainAxis(size=3))
        ... )
        >>> alt = f.set_construct(
        ...     cf.DimensionCoordinate(
        ...         properties={'standard_name': 'altitude',
        ...                     'units': 'm',
        ...                     'axis': 'Z'},
        ...         data=cf.Data([10]),
        ...         bounds=cf.Bounds(data=cf.Data([[0, 20]]))
        ...         ),
        ...     axes=f.set_construct(cf.DomainAxis(size=1))
        ... )
        >>> sd = LatLonGrid.from_field(f)
        >>> print(sd)
        LatLonGrid(
            shape {Z, Y, X}: (1, 3, 3)
            Z, altitude (1,): [10] m
            Y, latitude (3,): [15, 45, 75] degrees_north
            X, longitude (3,): [30, 90, 150] degrees_east
            Z_bounds (1, 2): [[0, 20]] m
            Y_bounds (3, 2): [[0, ..., 90]] degrees_north
            X_bounds (3, 2): [[0, ..., 180]] degrees_east
        )
        """
        # check constructs
        if not field.has_construct('latitude'):
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "no 'latitude' construct found.".format(
                                   cls.__name__))
        lat = field.construct('latitude')
        if not field.has_construct('longitude'):
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "no 'longitude' construct found.".format(
                                   cls.__name__))
        lon = field.construct('longitude')
        alt = None
        alt_bounds = None
        if field.has_construct('altitude'):
            if field.construct('altitude').has_bounds():
                alt = field.construct('altitude').array
                alt_bounds = field.construct('altitude').bounds.array

        # check units
        if lat.units not in ['degrees_north', 'degree_north', 'degrees_N',
                             'degree_N', 'degreesN', 'degreeN']:
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "the units of 'latitude' construct are "
                               "not in degrees north.".format(cls.__name__))
        if lon.units not in ['degrees_east', 'degree_east', 'degrees_E',
                             'degree_E', 'degreesE', 'degreeE']:
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "the units of 'longitude' construct are "
                               "not in degrees east.".format(cls.__name__))

        # check bounds
        if not lat.has_bounds():
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "the 'latitude' construct has "
                               "no bounds.".format(cls.__name__))
        if not lon.has_bounds():
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "the 'longitude' construct has "
                               "no bounds.".format(cls.__name__))

        return cls(latitude=lat.array, longitude=lon.array,
                   latitude_bounds=lat.bounds.array,
                   longitude_bounds=lon.bounds.array, altitude=alt,
                   altitude_bounds=alt_bounds)

    @classmethod
    def from_extent_and_resolution(cls, latitude_extent, longitude_extent,
                                   latitude_resolution, longitude_resolution,
                                   location='centre'):
        """Initialise a `LatLonGrid` from the extent and the resolution
        of latitude and longitude coordinates.

        :Parameters:

            latitude_extent: pair of `float` or `int`
                The extent of latitude coordinates in degrees North
                for the desired grid. The first element of the pair is
                the location of the start of the extent along the
                latitude coordinate, the second element of the pair is
                the location of the end of the extent along the latitude
                coordinate (included). May be any type that can be
                unpacked (e.g. `tuple`, `list`, `numpy.array`).

                *Parameter example:*
                    ``latitude_extent=(30, 70)``

            longitude_extent: pair of `float` or `int`
                The extent of longitude coordinates in degrees East
                for the desired grid. The first element of the pair is
                the location of the start of the extent along the
                longitude coordinate, the second element of the pair is
                the location of the end of the extent along the
                longitude coordinate (included). May be any type that
                can be unpacked (e.g. `tuple`, `list`, `numpy.array`).

                *Parameter example:*
                    ``longitude_extent=(0, 90)``

            latitude_resolution: `float` or `int`
                The spacing between two consecutive latitude coordinates
                in degrees North for the desired grid.

                *Parameter example:*
                    ``latitude_resolution=10``

            longitude_resolution: `float` or `int`
                The spacing between two consecutive longitude
                coordinates in degrees East for the desired grid.

                *Parameter example:*
                    ``longitude_resolution=10``

            location: `str` or `int`, optional
                The location of the latitude and longitude coordinates
                in relation to their grid cells (i.e. their bounds).
                This information is required to generate the latitude
                and longitude bounds for each grid coordinate. If not
                provided, set to default 'centre'.

                The directions left and right are related to the
                longitude coordinates(X-axis), while the directions
                lower and upper are related to the latitude coordinates
                (X-axis). The orientation of the coordinate system
                considered is detailed below.

                    Y, latitude (degrees North)
                    ↑
                    ·
                    * · → X, longitude (degrees East)

                This parameter can be set using the labels (as a `str`)
                or the indices (as an `int`) detailed in the table
                below.

                ================  =====  ===============================
                label             index  description
                ================  =====  ===============================
                ``'centre'``      ``0``  The latitude and longitude
                                         bounds span equally on both
                                         sides of the coordinate along
                                         the two axes, of a length equal
                                         to half the  resolution along
                                         the given axis.

                ``'lower left'``  ``1``  The latitude bounds extent
                                         northwards of a length equal to
                                         the latitude resolution. The
                                         longitude bounds extend
                                         eastwards of a length equal to
                                         the longitude resolution.

                ``'upper left'``  ``2``  The latitude bounds extent
                                         southwards of a length equal to
                                         the latitude resolution. The
                                         longitude bounds extend
                                         eastwards of a length equal to
                                         the longitude resolution.

                ``'lower right'`` ``3``  The latitude bounds extent
                                         northwards of a length equal to
                                         the latitude resolution. The
                                         longitude bounds extend
                                         westwards of a length equal to
                                         the longitude resolution.

                ``'upper right'`` ``4``  The latitude bounds extent
                                         southwards of a length equal to
                                         the latitude resolution. The
                                         longitude bounds extend
                                         westwards of a length equal to
                                         the longitude resolution.
                ================  =====  ===============================

                The indices defining the location of the coordinate in
                relation to its grid cell are made explicit below, where
                the '+' characters depict the coordinates, and the '·'
                characters delineate the relative location of the grid
                cell whose height and width are determined using the
                latitude and longitude resolutions, respectively.

                    2             4               northwards
                     +  ·  ·  ·  +                    ↑
                     ·           ·                    ·
                     ·   0 +     ·      westwards ← · * · → eastwards
                     ·           ·                    ·
                     +  ·  ·  ·  +                    ↓
                    1             3               southwards

                *Parameter example:*
                    ``location='centre``
                    ``location=0`

        **Examples**

        >>> sd = LatLonGrid.from_extent_and_resolution(
        ...     grid_latitude_extent=(30, 70),
        ...     grid_longitude_extent=(0, 90),
        ...     grid_latitude_resolution=5,
        ...     grid_longitude_resolution=10
        ... )
        >>> print(sd)
        LatLonGrid(
            shape {Y, X}: (8, 9)
            Y, latitude (8,): [32.5, ..., 67.5] degrees_north
            X, longitude (9,): [5.0, ..., 85.0] degrees_east
            Y_bounds (8, 2): [[30.0, ..., 70.0]] degrees_north
            X_bounds (9, 2): [[0.0, ..., 90.0]] degrees_east
        )
        >>> sd = LatLonGrid.from_extent_and_resolution(
        ...     grid_latitude_extent=(30, 70),
        ...     grid_longitude_extent=(0, 90),
        ...     grid_latitude_resolution=5,
        ...     grid_longitude_resolution=10,
        ...     location='upper right'
        ... )
        >>> print(sd)
        LatLonGrid(
            shape {Y, X}: (8, 9)
            Y, latitude (8,): [35.0, ..., 70.0] degrees_north
            X, longitude (9,): [10.0, ..., 90.0] degrees_east
            Y_bounds (8, 2): [[30.0, ..., 70.0]] degrees_north
            X_bounds (9, 2): [[0.0, ..., 90.0]] degrees_east
        )
        """
        return cls(
            **grid_from_extent_and_resolution(
                latitude_extent, longitude_extent, latitude_resolution,
                longitude_resolution, location
            )
        )


class RotatedLatLonGrid(Grid):
    """LatLonGrid characterises the spatial dimension for a `Component`
    as a regular grid on a spherical domain whose coordinates are
    latitudes and longitudes, and whose rotation axis is not aligned
    with the North pole.
    """

    def __init__(self, grid_latitude, grid_longitude, grid_latitude_bounds,
                 grid_longitude_bounds, earth_radius, grid_north_pole_latitude,
                 grid_north_pole_longitude, altitude=None,
                 altitude_bounds=None):
        """**Initialisation**

        :Parameters:

            grid_latitude: one-dimensional array-like object
                The array of latitude coordinates in degrees defining
                the temporal dimension. May be any type that can be cast
                to a `numpy.array`. Must contain numerical values.

                *Parameter example:*
                    ``grid_latitude=[0.88, 0.44, 0., -0.44, -0.88]``

            grid_longitude: one-dimensional array-like object
                The array of longitude coordinates in degrees defining
                the temporal dimension. May be any type that can be cast
                to a `numpy.array`. Must contain numerical values.

                *Parameter example:*
                    ``grid_longitude=[-2.5, -2.06, -1.62, -1.18]``

            grid_latitude_bounds: two-dimensional array-like object
                The array of latitude coordinate bounds in degrees
                defining the extent of the grid cell around the
                coordinate. May be any type that can be cast to a
                `numpy.array`. Must be two dimensional with the first
                dimension equal to the size of `grid_latitude` and the
                second dimension equal to 2. Must contain numerical
                values.

                *Parameter example:*
                    ``grid_latitude_bounds=[[1.1, 0.66], [0.66, 0.22],
                                            [0.22, -0.22], [-0.22, -0.66],
                                            [-0.66, -1.1]]``

            grid_longitude_bounds: two-dimensional array-like object
                The array of longitude coordinate bounds in degrees
                defining the extent of the grid cell around the
                coordinate. May be any type that can be cast to a
                `numpy.array`. Must feature two dimensional with the
                first dimension equal to the size of `grid_longitude`
                and the second dimension equal to 2. Must contain
                numerical values.

                *Parameter example:*
                    ``grid_longitude_bounds=[[-2.72, -2.28], [-2.28, -1.84],
                                             [-1.84, -1.4], [-1.4, -0.96]]```

            earth_radius: `int` or `float`
                The radius of the spherical figure used to approximate
                the shape of the Earth in metres. This parameter is
                required to project the rotated grid into a true
                latitude-longitude coordinate system.

            grid_north_pole_latitude: `int` or `float`
                The true latitude of the north pole of the rotated grid
                in degrees North. This parameter is required to project
                the rotated grid into a true latitude-longitude
                coordinate system.

            grid_north_pole_longitude: `int` or `float`
                The true longitude of the north pole of the rotated grid
                in degrees East. This parameter is required to project
                the rotated grid into a true latitude-longitude
                coordinate system.

            altitude: one-dimensional array-like object, optional
                The array of altitude coordinates in metres defining the
                temporal dimension. May be any type that can be cast to
                a `numpy.array`. Must contain numerical values. Ignored
                if `altitude_bounds` not also provided.

                *Parameter example:*
                    ``altitude=[10]``

            altitude_bounds: two-dimensional array-like object, optional
                The array of altitude coordinate bounds in metres
                defining the extent of the grid cell around the
                coordinate. May be any type that can be cast to a
                `numpy.array`. Must be two dimensional with the first
                dimension equal to the size of `altitude` and the second
                dimension equal to 2. Must contain numerical values.
                Ignored if `altitude` not also provided.

                *Parameter example:*
                    ``altitude=[[0, 20]]``

        **Examples**

        >>> sd = RotatedLatLonGrid(
        ...     grid_latitude=[0.88, 0.44, 0., -0.44, -0.88],
        ...     grid_longitude=[-2.5, -2.06, -1.62, -1.18],
        ...     grid_latitude_bounds=[[1.1, 0.66], [0.66, 0.22], [0.22, -0.22],
        ...                           [-0.22, -0.66], [-0.66, -1.1]],
        ...     grid_longitude_bounds=[[-2.72, -2.28], [-2.28, -1.84],
        ...                            [-1.84, -1.4], [-1.4, -0.96]],
        ...     earth_radius=6371007,
        ...     grid_north_pole_latitude=38.0,
        ...     grid_north_pole_longitude=190.0,
        ...     altitude=[10],
        ...     altitude_bounds=[[0, 20]]
        ... )
        >>> print(sd)
        RotatedLatLonGrid(
            shape {Z, Y, X}: (1, 5, 4)
            Z, altitude (1,): [10] m
            Y, grid_latitude (5,): [0.88, ..., -0.88] degrees
            X, grid_longitude (4,): [-2.5, ..., -1.18] degrees
            Z_bounds (1, 2): [[0, 20]] m
            Y_bounds (5, 2): [[1.1, ..., -1.1]] degrees
            X_bounds (4, 2): [[-2.72, ..., -0.96]] degrees
        )
        """
        super(RotatedLatLonGrid, self).__init__()

        if altitude is not None and altitude_bounds is not None:
            self._set_space(altitude, altitude_bounds,
                            name='altitude', units='m', axis='Z')
            self._f.construct('Z').set_property('positive', 'up')

        self._set_space(grid_latitude, grid_latitude_bounds,
                        name='grid_latitude', units='degrees', axis='Y')
        self._set_space(grid_longitude, grid_longitude_bounds,
                        name='grid_longitude', units='degrees', axis='X')

        self._set_rotation_parameters(earth_radius, grid_north_pole_latitude,
                                      grid_north_pole_longitude)

    def _set_rotation_parameters(self, earth_radius, grid_north_pole_latitude,
                                 grid_north_pole_longitude):
        coord_conversion = cf.CoordinateConversion(
            parameters={'grid_mapping_name': 'rotated_latitude_longitude',
                        'grid_north_pole_latitude':
                            grid_north_pole_latitude,
                        'grid_north_pole_longitude':
                            grid_north_pole_longitude})
        self._f.set_construct(
            cf.CoordinateReference(
                datum=cf.Datum(
                    parameters={'earth_radius': earth_radius}),
                coordinate_conversion=coord_conversion,
                coordinates=['grid_latitude', 'grid_longitude'])
        )

    def is_space_equal_to(self, field, ignore_altitude=False):
        # check whether latitude and longitude constructs are identical
        # by checking if grid_latitude match, if grid_longitude match
        # and if coordinate_reference match (by checking its
        # coordinate_conversion and its datum separately, because
        # coordinate_reference.equals() would also check the size of the
        # collections of coordinates)
        lat_lon = (
            self._f.construct('grid_latitude').equals(
                field.construct('grid_latitude', default=None),
                ignore_data_type=True)
            and self._f.construct('grid_longitude').equals(
                field.construct('grid_longitude', default=None),
                ignore_data_type=True)
            and self._f.coordinate_reference(
                'rotated_latitude_longitude').coordinate_conversion.equals(
                field.coordinate_reference(
                    'rotated_latitude_longitude',
                    default=None).coordinate_conversion)
            and self._f.coordinate_reference(
                'rotated_latitude_longitude').datum.equals(
                field.coordinate_reference(
                    'rotated_latitude_longitude',
                    default=None).datum)
        )
        # check whether altitude constructs are identical
        if ignore_altitude:
            alt = True
        else:
            if self._f.has_construct('altitude'):
                alt = self._f.construct('altitude').equals(
                    field.construct('altitude', default=None),
                    ignore_data_type=True)
            else:
                alt = True

        return lat_lon and alt

    @classmethod
    def from_field(cls, field):
        """Initialise a `RotatedLatLonGrid` from a cf.Field instance.

        :Parameters:

            field: cf.Field object
                The field object who will be used to initialise a
                'RotatedLatLonGrid` instance. This field must feature a
                'latitude' and a 'longitude' constructs, and these
                constructs must feature bounds. In addition, the
                parameters required for the conversion of the grid to a
                true latitude-longitude reference system must be set
                (i.e. earth_radius, grid_north_pole_latitude,
                grid_north_pole_longitude). This field may optionally
                feature an 'altitude' construct alongside its bounds
                (both required otherwise ignored).

        **Examples**

        >>> import cf
        >>> f = cf.Field()
        >>> lat = f.set_construct(
        ...     cf.DimensionCoordinate(
        ...         properties={'standard_name': 'grid_latitude',
        ...                     'units': 'degrees',
        ...                     'axis': 'Y'},
        ...         data=cf.Data([0.88, 0.44, 0., -0.44, -0.88]),
        ...         bounds=cf.Bounds(data=cf.Data([[1.1, 0.66], [0.66, 0.22],
        ...                                        [0.22, -0.22], [-0.22, -0.66],
        ...                                        [-0.66, -1.1]]))
        ...     ),
        ...     axes=f.set_construct(cf.DomainAxis(size=5))
        ... )
        >>> lon = f.set_construct(
        ...     cf.DimensionCoordinate(
        ...         properties={'standard_name': 'grid_longitude',
        ...                     'units': 'degrees',
        ...                     'axis': 'X'},
        ...         data=cf.Data([-2.5, -2.06, -1.62, -1.18]),
        ...         bounds=cf.Bounds(data=cf.Data([[-2.72, -2.28], [-2.28, -1.84],
        ...                                        [-1.84, -1.4], [-1.4, -0.96]]))
        ...     ),
        ...     axes=f.set_construct(cf.DomainAxis(size=4))
        ... )
        >>> alt = f.set_construct(
        ...     cf.DimensionCoordinate(
        ...         properties={'standard_name': 'altitude',
        ...                     'units': 'm',
        ...                     'axis': 'Z'},
        ...         data=cf.Data([10]),
        ...         bounds=cf.Bounds(data=cf.Data([[0, 20]]))
        ...         ),
        ...     axes=f.set_construct(cf.DomainAxis(size=1))
        ... )
        >>> crs = f.set_construct(
        ...     cf.CoordinateReference(
        ...         datum=cf.Datum(parameters={'earth_radius': 6371007.}),
        ...         coordinate_conversion=cf.CoordinateConversion(
        ...             parameters={'grid_mapping_name': 'rotated_latitude_longitude',
        ...                         'grid_north_pole_latitude': 38.0,
        ...                         'grid_north_pole_longitude': 190.0}),
        ...         coordinates=(lat, lon)
        ...     )
        ... )
        >>> sd = RotatedLatLonGrid.from_field(f)
        >>> print(sd)
        RotatedLatLonGrid(
            shape {Z, Y, X}: (1, 5, 4)
            Z, altitude (1,): [10] m
            Y, grid_latitude (5,): [0.88, ..., -0.88] degrees
            X, grid_longitude (4,): [-2.5, ..., -1.18] degrees
            Z_bounds (1, 2): [[0, 20]] m
            Y_bounds (5, 2): [[1.1, ..., -1.1]] degrees
            X_bounds (4, 2): [[-2.72, ..., -0.96]] degrees
        )
        """
        # check constructs
        if not field.has_construct('grid_latitude'):
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "no 'grid_latitude' construct found.".format(
                                   cls.__name__))
        grid_lat = field.construct('grid_latitude')
        if not field.has_construct('grid_longitude'):
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "no 'grid_longitude' construct found.".format(
                                   cls.__name__))
        grid_lon = field.construct('grid_longitude')
        alt = None
        alt_bounds = None
        if field.has_construct('altitude'):
            if field.construct('altitude').has_bounds():
                alt = field.construct('altitude').array
                alt_bounds = field.construct('altitude').bounds.array

        # check units
        if grid_lat.units not in ['degrees', 'degree']:
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "the units of 'grid_latitude' construct are "
                               "not in degrees.".format(cls.__name__))
        if grid_lon.units not in ['degrees', 'degree']:
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "the units of 'grid_longitude' construct are "
                               "not in degrees.".format(cls.__name__))

        # check bounds
        if not grid_lat.has_bounds():
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "the 'grid_latitude' construct has "
                               "no bounds.".format(cls.__name__))
        if not grid_lon.has_bounds():
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "the 'grid_longitude' construct has "
                               "no bounds.".format(cls.__name__))

        # check conversion parameters
        if field.has_construct('grid_mapping_name:rotated_latitude_longitude'):
            crs = field.construct(
                'grid_mapping_name:rotated_latitude_longitude')
        else:
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "no coordinate reference found with coordinate "
                               "conversion whose 'grid_mapping_name' is set as "
                               "'rotated_latitude_longitude'.".format(
                                   cls.__name__))
        if crs.datum.has_parameter('earth_radius'):
            earth_radius = crs.datum.get_parameter('earth_radius')
        else:
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "coordinate reference has no datum property "
                               "named 'earth_radius'.".format(cls.__name__))
        if crs.coordinate_conversion.has_parameter('grid_north_pole_latitude'):
            north_pole_lat = crs.coordinate_conversion.get_parameter(
                'grid_north_pole_latitude')
        else:
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "coordinate conversion has no property named "
                               "'grid_north_pole_latitude'.".format(
                                   cls.__name__))
        if crs.coordinate_conversion.has_parameter('grid_north_pole_longitude'):
            north_pole_lon = crs.coordinate_conversion.get_parameter(
                'grid_north_pole_longitude')
        else:
            raise RuntimeError("Error when initialising a {} from a Field: "
                               "coordinate conversion has no property named "
                               "'grid_north_pole_longitude'.".format(
                                   cls.__name__))

        return cls(grid_latitude=grid_lat.array, grid_longitude=grid_lon.array,
                   grid_latitude_bounds=grid_lat.bounds.array,
                   grid_longitude_bounds=grid_lon.bounds.array,
                   earth_radius=earth_radius,
                   grid_north_pole_latitude=north_pole_lat,
                   grid_north_pole_longitude=north_pole_lon,
                   altitude=alt, altitude_bounds=alt_bounds)

    @classmethod
    def _from_extent_and_resolution(cls, grid_latitude_extent,
                                    grid_longitude_extent,
                                    grid_latitude_resolution,
                                    grid_longitude_resolution,
                                    earth_radius, grid_north_pole_latitude,
                                    grid_north_pole_longitude,
                                    location='centre'):
        """Initialise a `RotatedLatLonGrid` from the extent and the
        resolution of grid_latitude and grid_longitude coordinates.
        """
        return type(cls)(
            **grid_from_extent_and_resolution(
                grid_latitude_extent, grid_longitude_extent, grid_latitude_resolution,
                grid_longitude_resolution, location
            ),
            earth_radius=earth_radius,
            grid_north_pole_latitude=grid_north_pole_latitude,
            grid_north_pole_longitude=grid_north_pole_longitude
        )


def grid_from_extent_and_resolution(latitude_extent, longitude_extent,
                                    latitude_resolution, longitude_resolution,
                                    location='centre'):
    # infer grid span in relation to coordinate from location
    if location in ('centre', 'center', '0', 0):
        lon_span, lat_span = [[-0.5, 0.5]], [[-0.5, 0.5]]
    elif location in ('lower_left', 'lower left', '1', 1):
        lon_span, lat_span = [[0, 1]], [[0, 1]]
    elif location in ('upper_left', 'upper left', '2', 2):
        lon_span, lat_span = [[0, 1]], [[-1, 0]]
    elif location in ('lower_right', 'lower right', '3', 3):
        lon_span, lat_span = [[-1, 0]], [[0, 1]]
    elif location in ('upper_right', 'upper right', '4', 4):
        lon_span, lat_span = [[-1, 0]], [[-1, 0]]
    else:
        raise ValueError("Error when generating grid from extent and "
                         "resolution: location '{}' not "
                         "supported.".format(location))

    # check compatibility between extent and resolution
    # (i.e. need to produce a whole number of grid cells)
    lat_start, lat_end = latitude_extent
    lon_start, lon_end = longitude_extent

    if not (lat_end - lat_start) % latitude_resolution == 0:
        raise RuntimeError("Error when generating grid from extent and "
                           "resolution: latitude extent and resolution "
                           "do not define a whole number of grid cells.")
    lat_size = (lat_end - lat_start) // latitude_resolution
    if not (lon_end - lon_start) % longitude_resolution == 0:
        raise RuntimeError("Error when generating grid from extent and "
                           "resolution: longitude extent and resolution "
                           "do not define a whole number of grid cells.")
    lon_size = (lon_end - lon_start) // longitude_resolution

    # determine latitude and longitude coordinates
    lat = (
        (np.arange(lat_size) + 0.5 - np.mean(lat_span))
        * latitude_resolution + lat_start
    )
    lon = (
        (np.arange(lon_size) + 0.5 - np.mean(lon_span))
        * longitude_resolution + lon_start
    )

    # determine latitude and longitude coordinate bounds
    lat_bounds = (
        lat.reshape((lat.size, -1)) +
        np.array(lat_span) * latitude_resolution
    )
    lon_bounds = (
        lon.reshape((lon.size, -1)) +
        np.array(lon_span) * longitude_resolution
    )

    return {'latitude': lat,
            'longitude': lon,
            'latitude_bounds': lat_bounds,
            'longitude_bounds': lon_bounds}
