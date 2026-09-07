import requests


KGIS_GLOBAL_SEARCH_URL = (
    "https://www.kgis.org/arcgis/rest/services/"
    "Maps/GlobalSearch/MapServer"
)


def search_kgis_address(address):
    """
    Search the KGIS Address layer using an address string.
    """

    url = f"{KGIS_GLOBAL_SEARCH_URL}/1/query"

    params = {
        "where": "1=1",
        "text": address,
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get("features", [])


def search_kgis_parcel_by_address(address):
    """
    Search the KGIS parcel layer using the address.
    """

    url = f"{KGIS_GLOBAL_SEARCH_URL}/0/query"

    params = {
        "where": "1=1",
        "text": address,
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get("features", [])


def find_kgis_property(address):
    """
    Try the KGIS Address layer first.
    If that does not produce a result,
    try the KGIS Parcel layer.
    """

    address_results = search_kgis_address(address)

    if address_results:

        return {
            "source": "KGIS",
            "method": "Address Layer",
            "results": address_results
        }

    parcel_results = search_kgis_parcel_by_address(address)

    if parcel_results:

        return {
            "source": "KGIS",
            "method": "Parcel Layer",
            "results": parcel_results
        }

    return None
