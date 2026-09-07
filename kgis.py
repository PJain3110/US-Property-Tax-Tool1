import requests


KGIS_PROPERTY_URL = (
    "https://www.kgis.org/arcgis/rest/services/"
    "Maps/Property/MapServer"
)

KGIS_PARCEL_LAYER = 2


def query_kgis_parcels(params):
    """
    Query the KGIS Property > Parcels layer.
    """

    url = f"{KGIS_PROPERTY_URL}/{KGIS_PARCEL_LAYER}/query"

    base_params = {
        "f": "json",
        "outFields": "*",
        "returnGeometry": "true",
    }

    base_params.update(params)

    response = requests.get(
        url,
        params=base_params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def find_kgis_property(address):
    """
    Search the KGIS parcel layer using the property address.
    """

    try:

        data = query_kgis_parcels(
            {
                "where": (
                    "FULL_ADDRESS LIKE "
                    f"'%{address.split(',')[0]}%'"
                )
            }
        )

        return {
            "source": "KGIS",
            "method": "Property Parcels Layer",
            "response": data,
        }

    except Exception as e:

        return {
            "source": "KGIS",
            "method": "Property Parcels Layer",
            "error": str(e),
        }
