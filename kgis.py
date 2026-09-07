import requests


KGIS_GLOBAL_SEARCH_URL = (
    "https://www.kgis.org/arcgis/rest/services/"
    "Maps/GlobalSearch/MapServer"
)


def query_kgis(layer_id, params):
    """
    Query a KGIS ArcGIS layer and return the complete response.
    """

    url = f"{KGIS_GLOBAL_SEARCH_URL}/{layer_id}/query"

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
    Diagnostic KGIS search.

    We first query the Address layer and then
    the Parcels layer using ArcGIS text search.
    """

    results = []

    for layer_id, layer_name in [
        (1, "Address"),
        (0, "Parcels"),
    ]:

        try:

            data = query_kgis(
                layer_id,
                {
                    "text": address
                }
            )

            results.append(
                {
                    "layer": layer_name,
                    "layer_id": layer_id,
                    "success": True,
                    "response": data,
                }
            )

        except Exception as e:

            results.append(
                {
                    "layer": layer_name,
                    "layer_id": layer_id,
                    "success": False,
                    "error": str(e),
                }
            )

    return {
        "source": "KGIS",
        "results": results
    }
