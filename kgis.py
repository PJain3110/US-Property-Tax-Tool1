from urllib.parse import quote


KGIS_MAP_URL = "https://www.kgis.org/kgismaps/map.htm"


def build_kgis_address_url(address):
    """
    Build the official KGIS Maps address-search URL.
    """

    clean_address = address.strip()

    return (
        f"{KGIS_MAP_URL}"
        f"?address={quote(clean_address)}"
    )


def find_kgis_property(address):
    """
    Prepare an official KGIS address lookup.

    Direct ArcGIS REST requests from Streamlit are returning
    HTTP 403, so we do not treat the REST endpoint as usable.

    KGIS's public Maps application accepts an address through
    the address URL parameter and performs the actual search.
    """

    search_url = build_kgis_address_url(address)

    return {
        "source": "KGIS",
        "method": "Public KGIS Address Search",
        "results": [
            {
                "layer": "KGIS Public Address Search",
                "layer_id": None,
                "success": True,
                "response": {
                    "input_address": address,
                    "search_url": search_url,
                    "parcel_id": None,
                    "status": "External KGIS lookup required",
                    "message": (
                        "KGIS public search URL generated. "
                        "Direct automated ArcGIS access is blocked "
                        "with HTTP 403."
                    ),
                },
            }
        ],
    }
