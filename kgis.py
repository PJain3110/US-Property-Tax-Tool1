import requests
import re


KGIS_GLOBAL_SEARCH_URL = (
    "https://www.kgis.org/arcgis/rest/services/"
    "Maps/GlobalSearch/MapServer"
)


def kgis_query(layer_id, params):
    """
    Run a query against a KGIS ArcGIS layer.
    """

    url = f"{KGIS_GLOBAL_SEARCH_URL}/{layer_id}/query"

    base_params = {
        "outFields": "*",
        "returnGeometry": "true",
        "f": "json"
    }

    base_params.update(params)

    response = requests.get(
        url,
        params=base_params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        return []

    return data.get("features", [])


def normalize_address(address):
    """
    Normalize an address for comparison.
    """

    address = address.upper().strip()

    address = address.replace(",", " ")

    address = re.sub(r"\s+", " ", address)

    return address


def address_parts(address):
    """
    Extract street number and street name.
    """

    normalized = normalize_address(address)

    parts = normalized.split()

    if len(parts) < 2:
        return None, None

    street_number = parts[0]

    street_name_parts = []

    for part in parts[1:]:

        # Stop once we reach common city/state/ZIP components.
        if part in {
            "TN",
            "Tennessee",
            "NC",
            "North",
            "South",
            "East",
            "West"
        }:
            break

        if re.match(r"^\d{5}(-\d{4})?$", part):
            break

        street_name_parts.append(part)

    street_name = " ".join(street_name_parts)

    return street_number, street_name


def search_kgis_address(address):
    """
    Search KGIS Address layer using the ArcGIS
    text parameter against the searchable layer.
    """

    normalized = normalize_address(address)

    # ---------------------------------------------------------
    # Full address search
    # ---------------------------------------------------------

    results = kgis_query(
        1,
        {
            "text": normalized
        }
    )

    if results:
        return results

    # ---------------------------------------------------------
    # Street-number / street-name search
    # ---------------------------------------------------------

    street_number, street_name = address_parts(address)

    if street_number and street_name:

        results = kgis_query(
            1,
            {
                "text": f"{street_number} {street_name}"
            }
        )

        if results:
            return results

    return []


def search_kgis_parcel(address):
    """
    Search KGIS Parcels layer using the searchable
    FULL_ADDRESS field.
    """

    normalized = normalize_address(address)

    # ---------------------------------------------------------
    # Full address
    # ---------------------------------------------------------

    results = kgis_query(
        0,
        {
            "text": normalized
        }
    )

    if results:
        return results

    # ---------------------------------------------------------
    # Street-number / street-name
    # ---------------------------------------------------------

    street_number, street_name = address_parts(address)

    if street_number and street_name:

        results = kgis_query(
            0,
            {
                "text": f"{street_number} {street_name}"
            }
        )

        if results:
            return results

    return []


def find_kgis_property(address):
    """
    Find a property in KGIS.

    Address layer is checked first.
    Parcel layer is checked second.
    """

    address_results = search_kgis_address(address)

    if address_results:

        return {
            "source": "KGIS",
            "method": "Address Layer",
            "results": address_results
        }

    parcel_results = search_kgis_parcel(address)

    if parcel_results:

        return {
            "source": "KGIS",
            "method": "Parcel Layer",
            "results": parcel_results
        }

    return None
