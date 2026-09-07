import requests


KGIS_GLOBAL_SEARCH_URL = (
    "https://www.kgis.org/arcgis/rest/services/"
    "Maps/GlobalSearch/MapServer"
)


def run_query(layer_id, where):
    """
    Run a standard ArcGIS REST query against a KGIS layer.
    """

    url = f"{KGIS_GLOBAL_SEARCH_URL}/{layer_id}/query"

    params = {
        "where": where,
        "outFields": "*",
        "returnGeometry": "true",
        "returnDistinctValues": "false",
        "f": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        return []

    return data.get("features", [])


def search_kgis_address(address):
    """
    Search the KGIS Address layer.

    First try the complete address, then try
    progressively broader address components.
    """

    clean_address = address.strip().upper()

    results = []

    # ---------------------------------------------------------
    # Exact-ish address search
    # ---------------------------------------------------------

    conditions = [
        f"UPPER(FULL_ADDRESS) LIKE '%{clean_address}%'",
        f"UPPER(ADDRESS) LIKE '%{clean_address}%'",
        f"UPPER(SITE_ADDRESS) LIKE '%{clean_address}%'"
    ]

    for condition in conditions:

        try:
            results = run_query(1, condition)
        except Exception:
            results = []

        if results:
            return results

    # ---------------------------------------------------------
    # Extract street number and street name
    # ---------------------------------------------------------

    parts = clean_address.split(",")

    if parts:

        first_part = parts[0].strip()

        words = first_part.split()

        if len(words) >= 2:

            street_number = words[0]
            street_name = " ".join(words[1:])

            street_condition = (
                "UPPER(FULL_ADDRESS) LIKE "
                f"'%{street_number}%{street_name}%'"
            )

            try:
                results = run_query(
                    1,
                    street_condition
                )
            except Exception:
                results = []

            if results:
                return results

    return []


def search_kgis_parcel_by_address(address):
    """
    Search the KGIS Parcel layer using the address.
    """

    clean_address = address.strip().upper()

    conditions = [
        f"UPPER(FULL_ADDRESS) LIKE '%{clean_address}%'",
        f"UPPER(ADDRESS) LIKE '%{clean_address}%'",
        f"UPPER(SITE_ADDRESS) LIKE '%{clean_address}%'"
    ]

    for condition in conditions:

        try:
            results = run_query(0, condition)
        except Exception:
            results = []

        if results:
            return results

    # ---------------------------------------------------------
    # Try street number + street name
    # ---------------------------------------------------------

    parts = clean_address.split(",")

    if parts:

        first_part = parts[0].strip()
        words = first_part.split()

        if len(words) >= 2:

            street_number = words[0]
            street_name = " ".join(words[1:])

            condition = (
                "UPPER(FULL_ADDRESS) LIKE "
                f"'%{street_number}%{street_name}%'"
            )

            try:
                results = run_query(
                    0,
                    condition
                )
            except Exception:
                results = []

            if results:
                return results

    return []


def find_kgis_property(address):
    """
    Search KGIS Address first, then Parcel.
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
