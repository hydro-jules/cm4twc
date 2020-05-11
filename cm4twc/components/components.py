import abc
import numpy as np
from cfunits import Units

from ..time_ import TimeDomain
from ..space_ import SpaceDomain, Grid
from ..data_ import DataSet


class _Component(metaclass=abc.ABCMeta):
    """
    DOCSTRING REQUIRED
    """

    _kind = None
    _ins = None
    _outs = None

    def __init__(self, category,
                 timedomain, spacedomain, dataset, parameters, constants,
                 driving_data_info, ancil_data_info,
                 parameters_info, constants_info, states_info, solver_history,
                 inwards, outwards):

        # category attribute
        self.category = category

        # definition attributes
        self.driving_data_info = \
            driving_data_info if driving_data_info else {}
        self.ancil_data_info = \
            ancil_data_info if ancil_data_info else {}
        self.parameters_info = \
            parameters_info if parameters_info else {}
        self.constants_info = \
            constants_info if constants_info else {}
        self.states_info = \
            states_info if states_info else {}
        self.solver_history = solver_history

        # interface attributes
        self.inwards = inwards
        self.outwards = outwards

        # time attributes
        self._check_timedomain(timedomain)
        self.timedomain = timedomain
        self.timestepinseconds = self.timedomain.timedelta.total_seconds()

        # space attributes
        self._check_spacedomain(spacedomain)
        self.spacedomain = spacedomain
        self.spaceshape = self.spacedomain.shape_

        # data attributes
        dataset = DataSet() if dataset is None else dataset
        self._check_dataset(dataset, timedomain, spacedomain)
        self.dataset = dataset

        # parameters attribute
        parameters = {} if parameters is None else parameters
        self._check_parameters(parameters)
        self.parameters = parameters

        # constants attribute
        constants = {} if constants is None else constants
        self.constants = constants  # no check because they are optional

        # states attribute
        self.states = {}

    def _check_timedomain(self, timedomain):
        """
        The purpose of this method is to check that the timedomain is
        of the right type.

        :param timedomain: object being given as timedomain during the
        call of the [simulate] method for the given component
        :type timedomain: object

        :return: None
        """
        if not isinstance(timedomain, TimeDomain):
            raise TypeError("The 1st domain item for the '{}' component "
                            "must be an instance of {}.".format(
                self.category, TimeDomain.__name__))

    def _check_spacedomain(self, spacedomain):
        """
        The purpose of this method is to check that the spacedomain is
        of the right type.

        :param spacedomain: object being given as spacedomain during the
        call of the [simulate] method for the given component
        :type spacedomain: object

        :return: None
        """
        if not isinstance(spacedomain, SpaceDomain):
            raise TypeError("The 2nd domain item for the '{}' component "
                            "must be an instance of {}.".format(
                self.category, TimeDomain.__name__))
        else:
            if not isinstance(spacedomain, Grid):
                raise NotImplementedError("The only {} subclass currently "
                                          "supported by the framework is "
                                          "{}.".format(SpaceDomain.__name__,
                                                       Grid.__name__))

    def _check_dataset(self, dataset, timedomain, spacedomain):
        """
        The purpose of this method is to check that:
            - the object given for the dataset is an instance of
              [DataSet]
            - the dataset contains [Variable] instances for all the
              driving and ancillary data the component requires
            - the domain of each variable complies with the component's
              domain

        :param dataset: object being given as the dataset for the given
        component category
        :type dataset: object
        :param timedomain: instance of [TimeDomain] for the given
        component category
        :type timedomain: TimeDomain
        :param spacedomain: instance of [SpaceDomain] for the given
        component category
        :type spacedomain: SpaceDomain

        :return: None
        """

        # check that the dataset is an instance of DataSet
        if not isinstance(dataset, DataSet):
            raise TypeError(
                "The dataset object given for the {} component '{}' must "
                "be an instance of {}.".format(
                    self.category, self.__class__.__name__,
                    DataSet.__name__))

        # check driving data for time and space compatibility with component
        for data_name, data_unit in self.driving_data_info.items():
            # check that all driving data are available in DataSet
            if data_name not in dataset:
                raise KeyError(
                    "There is no data '{}' available in the {} "
                    "for the {} component '{}'.".format(
                        data_name, DataSet.__name__, self.category,
                        self.__class__.__name__))
            # check that driving data units are compliant with component units
            if hasattr(dataset[data_name], 'units'):
                if not Units(data_unit).equals(
                        Units(dataset[data_name].units)):
                    raise ValueError(
                        "The units of the variable '{}' in the {} {} "
                        "are not equal to the units required by the {} "
                        "component '{}': {} are required.".format(
                            data_name, self.category, DataSet.__name__,
                            self.category, self.__class__.__name__,
                            data_unit))
            else:
                raise AttributeError("The variable '{}' in the {} for "
                                     "the {} component is missing a 'units' "
                                     "attribute.".format(
                                        data_name, DataSet.__name__,
                                        self.category))

            # check that the data and component time domains are compatible
            # using _truncation=-1 to remove requirement for last datetime
            # of TimeDomain to be available which is not required
            if not timedomain.is_time_equal_to(dataset[data_name],
                                               _trailing_truncation_idx=-1):
                raise ValueError(
                    "The time domain of the data '{}' is not compatible with "
                    "the time domain of the {} component '{}'.".format(
                        data_name, self.category, self.__class__.__name__))
            # check that the data and component space domains are compatible
            if not spacedomain.is_space_equal_to(dataset[data_name]):
                raise ValueError(
                    "The space domain of the data '{}' is not compatible with "
                    "the space domain of the {} component '{}'.".format(
                        data_name, self.category, self.__class__.__name__))

        # check ancillary data for space compatibility with component
        for data_name, data_unit in self.ancil_data_info.items():
            # check that all ancillary data are available in DataSet
            if data_name not in dataset:
                raise KeyError(
                    "There is no data '{}' available in the {} "
                    "for the {} component '{}'.".format(
                        data_name, DataSet.__name__, self.category,
                        self.__class__.__name__))
            # check that driving data units are compliant with component units
            if hasattr(dataset[data_name], 'units'):
                if not Units(data_unit).equals(
                        Units(dataset[data_name].units)):
                    raise ValueError(
                        "The units of the variable '{}' in the {} {} "
                        "are not equal to the units required by the {} "
                        "component '{}': {} are required.".format(
                            data_name, self.category, DataSet.__name__,
                            self.category, self.__class__.__name__,
                            data_unit))
            else:
                raise AttributeError("The variable '{}' in the {} for "
                                     "the {} component is missing a 'units' "
                                     "attribute.".format(
                                        data_name, DataSet.__name__,
                                        self.category))
            # check that the data and component space domains are compatible
            if not spacedomain.is_space_equal_to(dataset[data_name]):
                raise ValueError(
                    "The space domain of the data '{}' is not compatible with "
                    "the space domain of the {} component '{}'.".format(
                        data_name, self.category, self.__class__.__name__))

    def _check_parameters(self, parameters):
        """
        The purpose of this method is to check that parameter values are given
        for the corresponding component.

        :param parameters: a dictionary containing the parameter values given
        during the call of the [simulate] method for the given component
        :type parameters: dict

        :return: None
        """
        # check that all parameters are provided
        if not all([i in parameters for i in self.parameters_info]):
            raise RuntimeError(
                "One or more parameters are missing in {} component '{}': "
                "{} are all required.".format(
                    self.category, self.__class__.__name__,
                    self.parameters_info))

    def __call__(self, timeindex, datetime, **kwargs):

        # collect required ancillary data from dataset
        for data in self.ancil_data_info:
            kwargs[data] = self.dataset[data].array[...]

        # collect required driving data from dataset
        for data in self.driving_data_info:
            kwargs[data] = self.dataset[data].array[timeindex, ...]

        # run simulation for the component
        return self.run(datetime=datetime, **self.parameters, **self.constants,
                        **self.states, **kwargs)

    def initialise_states(self):
        states = self.initialise(**self.constants)
        for s in self.states_info.keys():
            if s in states:
                self.states[s] = State(*states[s])
            else:
                raise KeyError(
                    "The state '{}' of the {} component was "
                    "not initialised.".format(s, self._kind)
                )

    def increment_states(self):
        for s in self.states.keys():
            # determine first index in the State
            # (function of solver's history)
            first_index = -len(self.states[s]) + 1
            # prepare the left-hand side of the name re-binding
            lhs = [t for t in self.states[s]]
            # prepare the right-hand side of the name re-binding
            rhs = [t for t in self.states[s][first_index+1:]] + \
                [self.states[s][first_index]]
            # carry out the permutation (i.e. name re-binding)
            # to avoid new object creations
            lhs[:] = rhs[:]
            # apply new name bindings to the State
            self.states[s][:] = lhs

            # re-initialise current timestep of State to zero
            self.states[s][0][:] = 0.0

    def finalise_states(self):
        self.finalise(**self.states)

    @classmethod
    def get_class_kind(cls):
        return cls._kind

    @classmethod
    def get_class_inwards(cls):
        return cls._ins

    @classmethod
    def get_class_outwards(cls):
        return cls._outs

    @abc.abstractmethod
    def initialise(self, **kwargs):

        raise NotImplementedError(
            "The {} class '{}' does not feature an 'initialise' "
            "method.".format(self.category, self.__class__.__name__))

    @abc.abstractmethod
    def run(self, **kwargs):

        raise NotImplementedError(
            "The {} class '{}' does not feature a 'run' "
            "method.".format(self.category, self.__class__.__name__))

    @abc.abstractmethod
    def finalise(self, **kwargs):

        raise NotImplementedError(
            "The {} class '{}' does not feature a 'finalise' "
            "method.".format(self.category, self.__class__.__name__))


class SurfaceLayerComponent(_Component, metaclass=abc.ABCMeta):

    _kind = 'surfacelayer'
    _ins = {
        'soil_water_stress': '1'
    }
    _outs = {
        'throughfall': 'kg m-2 s-1',
        'snowmelt': 'kg m-2 s-1',
        'transpiration': 'kg m-2 s-1',
        'evaporation_soil_surface': 'kg m-2 s-1',
        'evaporation_ponded_water': 'kg m-2 s-1',
        'evaporation_openwater': 'kg m-2 s-1'
    }

    def __init__(self, timedomain, spacedomain, dataset, parameters, constants,
                 solver_history, driving_data_info=None, ancil_data_info=None,
                 parameters_info=None, constants_info=None, states_info=None):

        super(SurfaceLayerComponent, self).__init__(
            self._kind,
            timedomain, spacedomain, dataset, parameters, constants,
            driving_data_info, ancil_data_info,
            parameters_info, constants_info, states_info, solver_history,
            self._ins, self._outs)


class SubSurfaceComponent(_Component, metaclass=abc.ABCMeta):

    _kind = 'subsurface'
    _ins = {
        'evaporation_soil_surface': 'kg m-2 s-1',
        'evaporation_ponded_water': 'kg m-2 s-1',
        'transpiration': 'kg m-2 s-1',
        'throughfall': 'kg m-2 s-1',
        'snowmelt': 'kg m-2 s-1'
    }
    _outs = {
        'runoff': 'kg m-2 s-1',
        'soil_water_stress': '1'
    }

    def __init__(self, timedomain, spacedomain, dataset, parameters, constants,
                 solver_history, driving_data_info=None, ancil_data_info=None,
                 parameters_info=None, constants_info=None, states_info=None):

        super(SubSurfaceComponent, self).__init__(
            self._kind,
            timedomain, spacedomain, dataset, parameters, constants,
            driving_data_info, ancil_data_info,
            parameters_info, constants_info, states_info, solver_history,
            self._ins, self._outs)


class OpenWaterComponent(_Component, metaclass=abc.ABCMeta):

    _kind = 'openwater'
    _ins = {
        'evaporation_openwater': 'kg m-2 s-1',
        'runoff': 'kg m-2 s-1'
    }
    _outs = {
        'discharge': 'kg m-2 s-1'
    }

    def __init__(self, timedomain, spacedomain, dataset, parameters, constants,
                 solver_history, driving_data_info=None, ancil_data_info=None,
                 parameters_info=None, constants_info=None, states_info=None):

        super(OpenWaterComponent, self).__init__(
            self._kind,
            timedomain, spacedomain, dataset, parameters, constants,
            driving_data_info, ancil_data_info,
            parameters_info, constants_info, states_info, solver_history,
            self._ins, self._outs)


class DataComponent(_Component):

    _kind = 'data'
    _ins = {}
    _outs = {}

    def __init__(self, timedomain, spacedomain, dataset, substituting_class):

        super(DataComponent, self).__init__(
            substituting_class.get_class_kind(),
            timedomain, spacedomain, dataset, None, None,
            substituting_class.get_class_outwards(), None,
            None, None, None, 0,
            self._ins, self._outs)

    def initialise(self, **kwargs):

        return {}

    def run(self, **kwargs):

        return {n: kwargs[n] for n in self.driving_data_info}

    def finalise(self, **kwargs):

        pass


class NullComponent(_Component):

    _kind = 'null'
    _ins = {}
    _outs = {}

    def __init__(self, timedomain, spacedomain, substituting_class):

        super(NullComponent, self).__init__(
            substituting_class.get_class_kind(),
            timedomain, spacedomain, None, None, None,
            None, None,
            None, None, None, 0,
            self._ins, substituting_class.get_class_outwards())

    def initialise(self, **kwargs):

        return {}

    def run(self, **kwargs):

        null_array = np.zeros(self.spaceshape, np.float32)

        return {n: null_array for n in self.outwards}

    def finalise(self, **kwargs):

        pass


class State(object):
    """
    The State class behaves like a list which stores the values of a
    given component state for several consecutive timesteps (in
    chronological order, i.e. the oldest timestep is the first item,
    the most recent is the last item).

    Although, unlike a list, its indexing is shifted so that the last
    item has index 0, and all previous items are accessible via a
    negative integer (e.g. -1 for the 2nd-to-last, -2 for the
    3rd-to-last, etc.). The first item (i.e. the oldest timestep stored)
    is accessible at the index equals to minus the length of the list
    plus one. Since the list remains in chronological order, it means
    that for a given timestep t, index -1 corresponds to timestep t-1,
    index -2 to timestep t-2, etc. Current timestep t is accessible at
    index 0.
    """
    def __init__(self, *args):
        self.history = list(args)

    def __getitem__(self, index):
        index = self.shift_index(index)
        return self.history[index]

    def __setitem__(self, index, item):
        index = self.shift_index(index)
        self.history[index] = item

    def shift_index(self, index):
        if isinstance(index, int):
            index = index + len(self) - 1
        elif isinstance(index, slice):
            start, stop = index.start, index.stop
            if start is not None:
                start = start + len(self) - 1
            if stop is not None:
                stop = stop + len(self) - 1
            index = slice(start, stop, index.step)
        return index

    def __delitem__(self, index):
        index = self.shift_index(index)
        del self.history[index]

    def __len__(self):
        return len(self.history)

    def __iter__(self):
        return iter(self.history)

    def __repr__(self):
        return "%r" % self.history
