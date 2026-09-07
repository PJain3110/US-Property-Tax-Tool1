import requests


KGIS_GEOCORTEX_LAYER_URL = (
    "https://www.kgis.org/geocortex/essentials/rest/sites/"
    "City_Public_Service_Dept/map/mapservices/14/layers/27"
)


def search_kgis_parcel(address):
    """
    Search the KGIS parcel layer using the Geocortex REST API.

    This is the KGIS parcel layer identified from the official
    KGIS REST directory. The layer is queryable and exposes
    parcel/address, owner, tax district, and assessment fields.
    """

    # Keep the search focused on the street address portion.
    clean_address = address.strip()

    params = {
        "where": f"FULL_ADDRESS LIKE '%{clean_address}%'",
        "outFields": (
            "PARCELID,"
            "FULL_ADDRESS,"
            "KGIS_OWNER,"
            "TAX_DISTRICT,"
            "APPRAISED_LAND,"
            "APPRAISED_BLDG,"
            "APPRAISED_TOTAL,"
            "ASSESSED_TOTAL"
        ),
        "returnGeometry": "true",
        "f": "json",
    }

    response = requests.get(
        f"{KGIS_GEOCORTEX_LAYER_URL}/query",
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data


def find_kgis_property(address):
    """
    Find the parcel associated with an address through KGIS.
    """

    try:
        data = search_kgis_parcel(address)

        features = data.get("features", [])

        return {
            "source": "KGIS",
            "method": "Geocortex Parcel Layer",
            "results": features,
            "raw_response": data,
        }

    except Exception as e:

        return {
            "source": "KGIS",
            "method": "Geocortex Parcel Layer",
            "results": [],
            "error": str(e),
        }
