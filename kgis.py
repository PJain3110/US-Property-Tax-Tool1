from urllib.parse import quote


KGIS_MAP_URL = "https://www.kgis.org/kgismaps/map.htm"


def build_kgis_address_url(address):
    """
    Build the official KGIS Maps address-search URL.

    KGIS documents that the ?address= parameter
    automatically initiates an address search.
    """

    clean_address = address.strip()

    return (
        f"{KGIS_MAP_URL}"
        f"?address={quote(clean_address)}"
    )


def find_kgis_property(address):
    """
    Prepare an official KGIS address search.

    Direct KGIS ArcGIS REST requests currently return
    HTTP 403 from the Streamlit server, so we do not
    attempt those requests here.

    The public KGIS Maps application accepts an address
    through the ?address= URL parameter.
    """

    kgis_url = build_kgis_address_url(address)

    return {
        "source": "KGIS",
        "method": "KGIS Public Address Search",
        "results": [
            {
                "layer": "Public KGIS Address Search",
                "layer_id": None,
                "success": True,
                "response": {
                    "address": address,
                    "kgis_search_url": kgis_url,
                    "status": (
                        "KGIS public address search URL "
                        "generated successfully."
                    ),
                    "note": (
                        "Direct KGIS ArcGIS REST parcel "
                        "requests are currently blocked "
                        "with HTTP 403 from the application server."
                    )
                }
            }
        ]
    }
