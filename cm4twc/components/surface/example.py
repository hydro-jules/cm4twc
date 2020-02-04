from ..components import SurfaceComponent


class Dummy(SurfaceComponent):

    def __init__(self):
        super().__init__(driving_data_names=('rainfall', 'snowfall',
                                             'air_temperature',),
                         ancil_data_names=('vegetation_fraction',),
                         parameter_names=())

    def run(self, rainfall, snowfall, air_temperature,
            leaf_area_index,
            stomatal_resistance,
            **kwargs):

        return {
            'throughfall': None,
            'snowmelt': None,
            'transpiration': None,
            'evaporation_soil_surface': None,
            'evaporation_ponded_water': None,
            'evaporation_openwater': None
        }
