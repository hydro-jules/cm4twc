from cfunits import Units

from .time_ import TimeDomain
from .space_ import SpaceDomain, Grid
from .data_ import DataBase
from .components import SurfaceLayerComponent, SubSurfaceComponent, \
    OpenWaterComponent, DataComponent, NullComponent, _Component


class Model(object):
    """
    DOCSTRING REQUIRED
    """

    def __init__(self, surfacelayer, subsurface, openwater):

        self._surfacelayer = self._process_component_type(
            surfacelayer, SurfaceLayerComponent)

        self._subsurface = self._process_component_type(
            subsurface, SubSurfaceComponent)

        self._openwater = self._process_component_type(
            openwater, OpenWaterComponent)

    def simulate(self, surfacelayer_domain, subsurface_domain,
                 openwater_domain, surfacelayer_data=None,
                 subsurface_data=None, openwater_data=None,
                 surfacelayer_parameters=None, subsurface_parameters=None,
                 openwater_parameters=None):
        """
        DOCSTRING REQUIRED
        """

        # check that the context given for each component is a tuple
        # (TimeDomain instance, SpaceDomain instance)
        self._check_component_domain(self._surfacelayer, *surfacelayer_domain)
        self._check_component_domain(self._subsurface, *subsurface_domain)
        self._check_component_domain(self._openwater, *openwater_domain)

        if (surfacelayer_domain[0] != subsurface_domain[0]) \
                or (surfacelayer_domain[0] != openwater_domain[0]):
            raise NotImplementedError(
                "Currently, the modelling framework does not allow "
                "for components to work on different TimeDomains.")

        if (surfacelayer_domain[1] != subsurface_domain[1]) \
                or (surfacelayer_domain[1] != openwater_domain[1]):
            raise NotImplementedError(
                "Currently, the modelling framework does not allow "
                "for components to work on different SpaceDomains.")

        # check that the required parameters are provided
        if not surfacelayer_parameters:
            surfacelayer_parameters = {}
        self._check_component_parameters(self._surfacelayer, surfacelayer_parameters)
        if not subsurface_parameters:
            subsurface_parameters = {}
        self._check_component_parameters(self._subsurface, subsurface_parameters)
        if not openwater_parameters:
            openwater_parameters = {}
        self._check_component_parameters(self._openwater, openwater_parameters)

        # check that the required data is available in a DataBase instance
        if not surfacelayer_data:
            surfacelayer_data = DataBase()
        self._check_component_data(self._surfacelayer, surfacelayer_data,
                                   *surfacelayer_domain)
        if not subsurface_data:
            subsurface_data = DataBase()
        self._check_component_data(self._subsurface, subsurface_data,
                                   *subsurface_domain)
        if not openwater_data:
            openwater_data = DataBase()
        self._check_component_data(self._openwater, openwater_data,
                                   *openwater_domain)

        interface_ = {}

        # initialise components
        interface_.update(
            self._surfacelayer.initialise()
        )

        interface_.update(
            self._subsurface.initialise()
        )

        interface_.update(
            self._openwater.initialise()
        )

        # run components
        for t in range(surfacelayer_domain[0].construct('time').size):
            # use the time domain of surfacelayer for now, because the time
            # domains of the three components are checked for equality, but
            # eventually need to implement a time-stepping object to deal with
            # components operating at different temporal (and spatial for that
            # matter) resolution(s)
            interface_.update(
                self._surfacelayer(
                    t=t,
                    db=surfacelayer_data,
                    **surfacelayer_parameters,
                    **interface_
                )
            )

            interface_.update(
                self._subsurface(
                    t=t,
                    db=subsurface_data,
                    **subsurface_parameters,
                    **interface_
                )
            )

            interface_.update(
                self._openwater(
                    t=t,
                    db=openwater_data,
                    **openwater_parameters,
                    **interface_
                )
            )

        # finalise components
        self._surfacelayer.finalise()

        self._subsurface.finalise()

        self._openwater.finalise()

        return interface_

    @staticmethod
    def _process_component_type(component, expected_component):

        if issubclass(component, expected_component):
            # check inwards interface
            # check outwards interface
            return component()
        elif issubclass(component, (DataComponent, NullComponent)):
            return component(expected_component)
        else:
            raise TypeError(
                "The '{}' component given must either be a subclass of the "
                "class {}, the class {}, or the class {}.".format(
                    expected_component.category,
                    SurfaceLayerComponent.__name__, DataComponent.__name__,
                    NullComponent.__name__)
            )

    @staticmethod
    def _check_component_domain(component, timedomain, spacedomain):
        """
        The purpose of this method is to check that the elements in the
        tuple given for a given component category are of the right type
        (i.e. ([TimeDomain] instance and [SpaceDomain] instance)

        :param component: instance of the component whose domain is
        being checked
        :type component: _Component
        :param timedomain: object being given as 1st element of the domain
        tuple during the call of the [simulate] method for the given component
        :type timedomain: object
        :param spacedomain: object being given as 2nd element of the domain
        tuple during the call of the [simulate] method for the given component
        :type spacedomain: object

        :return: None
        """
        if not isinstance(timedomain, TimeDomain):
            raise TypeError("The 1st domain item for the '{}' component "
                            "must be an instance of {}.".format(
                                component.category, TimeDomain.__name__))

        if not isinstance(spacedomain, SpaceDomain):
            raise TypeError("The 2nd domain item for the '{}' component "
                            "must be an instance of {}.".format(
                                component.category, TimeDomain.__name__))
        else:
            if not isinstance(spacedomain, Grid):
                raise NotImplementedError("The only {} subclass currently "
                                          "supported by the framework is "
                                          "{}.".format(SpaceDomain.__name__,
                                                       Grid.__name__))

    @staticmethod
    def _check_component_parameters(component, parameters):
        """
        The purpose of this method is to check that parameter values are given
        for the corresponding component.

        :param component: instance of the component whose domain is
        being checked
        :type component: _Component
        :param parameters: a dictionary containing the parameter values given
        during the call of the [simulate] method for the given component
        :type parameters: dict

        :return: None
        """

        # check that all parameters are provided
        if not all([i in parameters for i in component.parameters_info]):
            raise RuntimeError(
                "One or more parameters are missing in {} component '{}': "
                "{} are all required.".format(
                    component.category, component.__class__.__name__,
                    component.parameters_info)
            )

    @staticmethod
    def _check_component_data(component, database, timedomain, spacedomain):
        """
        The purpose of this method is to check that:
            - the object given for the database is an instance of [DataBase]
            - the database contains [Variable] instances for all the driving
            and ancillary data the component requires
            - the domain of each variable complies with the component's domain

        :param component: instance of the component whose data is being checked
        :type component: _Component
        :param database: object being given as the database for the given
        component category
        :type database: object
        :param timedomain: instance of [TimeDomain] for the given
        component category
        :type timedomain: TimeDomain
        :param spacedomain: instance of [SpaceDomain] for the given
        component category
        :type spacedomain: SpaceDomain

        :return: None
        """

        # check that the data is an instance of DataBase
        if not isinstance(database, DataBase):
            raise TypeError(
                "The database object given for the {} component '{}' must "
                "be an instance of {}.".format(
                    component.category, component.__class__.__name__,
                    DataBase.__name__))

        # check driving data for time and space compatibility with component
        for data_name, data_unit in component.driving_data_info.items():
            # check that all driving data are available in DataBase
            if data_name not in database:
                raise KeyError(
                    "There is no data '{}' available in the database "
                    "for the {} component '{}'.".format(
                        data_name, component.category,
                        component.__class__.__name__))
            # check that driving data units are compliant with component units
            if hasattr(database[data_name], 'units'):
                if not Units(data_unit).equals(
                        Units(database[data_name].units)):
                    raise ValueError(
                        "The units of the variable '{}' in the {} DataBase "
                        "are not equal to the units required by the {} "
                        "component '{}': {} are required.".format(
                            data_name, component.category, component.category,
                            component.__class__.__name__, data_unit))
            else:
                raise AttributeError("The variable '{}' in the DataBase for "
                                     "the {} component is missing a 'units' "
                                     "attribute.".format(data_name,
                                                         component.category))

            # check that the data and component time domains are compatible
            if not timedomain.is_matched_in(database[data_name]):
                raise ValueError(
                    "The time domain of the data '{}' is not compatible with "
                    "the time domain of the {} component '{}'.".format(
                        data_name, component.category,
                        component.__class__.__name__))
            # check that the data and component space domains are compatible
            if not spacedomain.is_matched_in(database[data_name]):
                raise ValueError(
                    "The space domain of the data '{}' is not compatible with "
                    "the space domain of the {} component '{}'.".format(
                        data_name, component.category,
                        component.__class__.__name__))

        # check ancillary data for space compatibility with component
        for data_name, data_unit in component.ancil_data_info.items():
            # check that all ancillary data are available in DataBase
            if data_name not in database:
                raise KeyError(
                    "There is no data '{}' available in the database "
                    "for the {} component '{}'.".format(
                        data_name, component.category,
                        component.__class__.__name__))
            # check that driving data units are compliant with component units
            if hasattr(database[data_name], 'units'):
                if not Units(data_unit).equals(
                        Units(database[data_name].units)):
                    raise ValueError(
                        "The units of the variable '{}' in the {} DataBase "
                        "are not equal to the units required by the {} "
                        "component '{}': {} are required.".format(
                            data_name, component.category, component.category,
                            component.__class__.__name__, data_unit))
            else:
                raise AttributeError("The variable '{}' in the DataBase for "
                                     "the {} component is missing a 'units' "
                                     "attribute.".format(data_name,
                                                         component.category))
            # check that the data and component space domains are compatible
            if not spacedomain.is_matched_in(database[data_name]):
                raise ValueError(
                    "The space domain of the data '{}' is not compatible with "
                    "the space domain of the {} component '{}'.".format(
                        data_name, component.category,
                        component.__class__.__name__))
