from fastapi import APIRouter, Query
from ..models.schemas import WeatherContext
from ..services.weather_service import WeatherService

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("", response_model=WeatherContext)
def get_weather_context(
    mode: str = Query("mild", description="Weather mode: mild, hot, cold, or rainy")
):
    """
    Retrieve real-time or simulated weather context with fabric and styling advice.
    """
    data = WeatherService.get_weather_context(mode)
    return WeatherContext(
        condition=data["condition"],
        temperature_c=data["temperature_c"],
        humidity=data["humidity"],
        rain_probability=data["rain_probability"],
        styling_advice=data["styling_advice"]
    )
