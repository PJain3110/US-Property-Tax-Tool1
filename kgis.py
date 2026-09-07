import requests


PHOTON_URL = "https://photon.komoot.io/api/"


def photon_geocode(address):
    """
    Free OpenStreetMap-based geocoder using Photon.
    """

    params = {
        "q": address.strip(),
        "limit": 5,
    }

    headers = {
        "User-Agent": (
            "US-Property-Tax-Tool/1.0 "
            "(property-tax-research-tool)"
        )
    }

    response = requests.get(
        PHOTON_URL,
        params=params,
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def find_kgis_property(address):
    """
    Temporarily use Photon to test the free
    address-to-coordinate portion of the workflow.

    Parcel identification will be added after
    the coordinate lookup is confirmed.
    """

    try:

        data = photon_geocode(address)

        features = data.get(
            "features",
            []
        )

        results = []

        for feature in features:

            geometry = feature.get(
                "geometry",
                {}
            )

            properties = feature.get(
                "properties",
                {}
            )

            coordinates = geometry.get(
                "coordinates",
                []
            )

            results.append({
                "address": properties.get(
                    "name"
                ),
                "street": properties.get(
                    "street"
                ),
                "housenumber": properties.get(
                    "housenumber"
                ),
                "city": properties.get(
                    "city"
                ),
                "state": properties.get(
                    "state"
                ),
                "postcode": properties.get(
                    "postcode"
                ),
                "country": properties.get(
                    "country"
                ),
                "longitude": (
                    coordinates[0]
                    if len(coordinates) >= 2
                    else None
                ),
                "latitude": (
                    coordinates[1]
                    if len(coordinates) >= 2
                    else None
                ),
                "raw": feature,
            })

        return {
            "source": "Photon / OpenStreetMap",
            "method": "Photon Geocoder",
            "results": results,
            "raw_response": data,
        }

    except Exception as e:

        return {
            "source": "Photon / OpenStreetMap",
            "method": "Photon Geocoder",
            "results": [],
            "error": str(e),
        }
