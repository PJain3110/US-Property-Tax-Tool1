import requests
from urllib.parse import urlencode


KGIS_SERVICE_URL = (
    "https://www.kgis.org/arcgis/rest/services/"
    "Maps/Property/MapServer/2"
)

KGIS_PROXY_URL = (
    "https://www.kgis.org/portalproxy/proxy.ashx"
)


def query_kgis(params):
    """
    Query the KGIS parcel service through the KGIS proxy.
    """

    query_string = urlencode(params)

    target_url = (
        f"{KGIS_SERVICE_URL}/query"
        f"?{query_string}"
    )

    proxy_request_url = (
        f"{KGIS_PROXY_URL}?{target_url}"
    )

    response = requests.get(
        proxy_request_url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def find_kgis_property(address):
    """
    Search the KGIS Property > Parcels layer.

    This version uses the KGIS portal proxy rather
    than directly calling the ArcGIS REST endpoint.
    """

    street_address = address.split(",")[0].strip()

    params = {
        "f": "json",
        "where": (
            "FULL_ADDRESS LIKE "
            f"'%{street_address}%'"
        ),
        "outFields": "*",
        "returnGeometry": "true",
    }

    try:

        data = query_kgis(params)

        return {
            "source": "KGIS",
            "method": "Property Parcels via KGIS Proxy",
            "results": [
                {
                    "layer": "Property Parcels",
                    "layer_id": 2,
                    "success": True,
                    "response": data,
                }
            ],
        }

    except Exception as e:

        return {
            "source": "KGIS",
            "method": "Property Parcels via KGIS Proxy",
            "results": [
                {
                    "layer": "Property Parcels",
                    "layer_id": 2,
                    "success": False,
                    "error": str(e),
                }
            ],
        }
