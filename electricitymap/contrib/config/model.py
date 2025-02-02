import json
from typing import Callable, Dict, List, NewType, Tuple, Optional

from pydantic import BaseModel, Field, NonNegativeInt, PositiveInt
from pydantic.utils import import_string

from electricitymap.contrib.config import EXCHANGES_CONFIG, ZONES_CONFIG

# we could cast this to a NamedTuple with x/y accessors
Point = NewType("Point", Tuple[float, float])


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class Capacity(StrictBaseModel):
    # TODO: if zone.json used underscores for keys we didn't need the Field()
    battery_storage: Optional[NonNegativeInt] = Field(None, alias="battery storage")
    biomass: Optional[NonNegativeInt]
    coal: Optional[NonNegativeInt]
    gas: Optional[NonNegativeInt]
    geothermal: Optional[NonNegativeInt]
    hydro_storage: Optional[NonNegativeInt] = Field(None, alias="hydro storage")
    hydro: Optional[NonNegativeInt]
    nuclear: Optional[NonNegativeInt]
    oil: Optional[NonNegativeInt]
    solar: Optional[NonNegativeInt]
    unknown: Optional[NonNegativeInt]
    wind: Optional[NonNegativeInt]


class Parsers(StrictBaseModel):
    consumption: Optional[str]
    consumptionForecast: Optional[str]
    generationForecast: Optional[str]
    productionPerModeForecast: Optional[str]
    price: Optional[str]
    production: Optional[str]
    productionPerUnit: Optional[str]

    def get_function(self, type: str) -> Optional[Callable]:
        """Lazy load parser functions.

        This requires the consumer to have install all parser dependencies.

        Returns:
            Optional[Callable]: parser function
        """
        function_str = getattr(self, type)
        if function_str:
            return import_string(f"electricitymap.contrib.parsers.{function_str}")


class Delays(StrictBaseModel):
    consumption: Optional[PositiveInt]
    consumptionForecast: Optional[PositiveInt]
    generationForecast: Optional[PositiveInt]
    price: Optional[PositiveInt]
    production: Optional[PositiveInt]
    productionPerModeForecast: Optional[PositiveInt]
    productionPerUnit: Optional[PositiveInt]


class Zone(StrictBaseModel):
    bounding_box: Optional[List[Point]]
    capacity: Optional[Capacity]
    comment: Optional[str] = Field(None, alias="_comment")
    contributors: Optional[List[str]]
    delays: Optional[Delays]
    disclaimer: Optional[str]
    flag_file_name: Optional[str]
    parsers: Optional[Parsers]
    subZoneNames: Optional[List[str]]
    timezone: Optional[str]

    class Config:
        # To allow for both comment and _comment.
        # TODO: stick to one of them
        allow_population_by_field_name = True


class ExchangeParsers(StrictBaseModel):
    exchange: Optional[str]
    exchangeForecast: Optional[str]


class Exchange(StrictBaseModel):
    capacity: Optional[Tuple[int, int]]
    comment: Optional[str] = Field(None, alias="_comment")
    lonlat: Optional[Tuple[float, float]]
    parsers: Optional[ExchangeParsers]
    rotation: Optional[int]

    class Config:
        # To allow for both comment and _comment.
        # TODO: stick to one of them
        allow_population_by_field_name = True


class ConfigModel(StrictBaseModel):
    exchanges: Dict[str, Exchange]
    zones: Dict[str, Zone]
    # TODO: maybe extend with config/co2eq_parameters.json


def load_model() -> ConfigModel:
    return ConfigModel(exchanges=EXCHANGES_CONFIG, zones=ZONES_CONFIG)
