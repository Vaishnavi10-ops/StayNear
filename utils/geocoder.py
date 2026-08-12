from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

geolocator = Nominatim(
    user_agent="StayNear-Property-App"
)


def get_coordinates(address, area, city, pincode):

    location_text = f"{address}, {area}, {city}, {pincode}, India"

    try:
        location = geolocator.geocode(
            location_text,
            timeout=10
        )

        if location:
            return location.latitude, location.longitude

    except (GeocoderTimedOut, GeocoderServiceError):
        pass

    return None, None