import streamlit as st
import requests

from parcel_sources import PARCEL_SOURCES
from kgis import find_kgis_property


st.set_page_config(
    page_title="U.S. Property Tax Tool",
    layout="centered"
)

st.title("U.S. Property Tax Tool")

st.write(
    "Enter a U.S. property address to identify the property, "
    "county, and available parcel information."
)

address = st.text_input(
    "Property Address",
    placeholder="2165 Casablanca Way, Knoxville, TN 37932"
)


CENSUS_GEOCODER_URL = (
    "https://geocoding.geo.census.gov/geocoder"
)


def census_geocode(address):
    """
    Geocode an address using the free U.S. Census Geocoder.

    Returns latitude/longitude and the matched address.
    """

    url = (
        f"{CENSUS_GEOCODER_URL}/locations/onelineaddress"
    )

    params = {
        "address": address.strip(),
        "benchmark": "Public_AR_Current",
        "format": "json",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    matches = (
        data
        .get("result", {})
        .get("addressMatches", [])
    )

    if not matches:
        return None

    match = matches[0]

    coordinates = match.get(
        "coordinates",
        {}
    )

    components = match.get(
        "addressComponents",
        {}
    )

    return {
        "matched_address": match.get(
            "matchedAddress"
        ),
        "longitude": coordinates.get("x"),
        "latitude": coordinates.get("y"),
        "state": components.get("state"),
        "county": components.get("countyName"),
        "city": components.get("city"),
        "zip": components.get("zip"),
        "tigerline_id": (
            match.get("tigerLine", {})
            .get("tigerLineId")
        ),
        "tigerline_side": (
            match.get("tigerLine", {})
            .get("side")
        ),
    }


def census_geographies(address):
    """
    Retrieve Census geographic jurisdictions for an address.

    Layers:
        14 = Elementary School District
        16 = Secondary School District
        18 = Unified School District
    """

    url = (
        f"{CENSUS_GEOCODER_URL}/geographies/"
        "onelineaddress"
    )

    params = {
        "address": address.strip(),
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "layers": "14,16,18",
        "format": "json",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def extract_geography_results(data):
    """
    Convert Census geography response into a
    simpler structure for the application.
    """

    result = data.get("result", {})

    geographies = result.get(
        "addressMatches",
        []
    )

    if geographies:
        return geographies

    return []


def get_parcel_source(state, county):
    """
    Identify the configured parcel source
    for a state/county combination.
    """

    if not state or not county:
        return None

    state_sources = PARCEL_SOURCES.get(
        state.upper()
    )

    if not state_sources:
        return None

    for county_name, source in state_sources.items():

        if county_name.lower() in county.lower():
            return source

    return None


if address:

    st.divider()

    location = None
    geography_data = None

    with st.spinner(
        "Searching the U.S. Census Geocoder..."
    ):

        try:
            location = census_geocode(address)

        except Exception as e:

            st.error(
                f"Census geocoder error: {e}"
            )

    if location:

        st.success(
            "Address successfully geocoded."
        )

        st.subheader("Location")

        st.write(
            f"**Matched Address:** "
            f"{location.get('matched_address')}"
        )

        st.write(
            f"**State:** "
            f"{location.get('state') or 'Not available'}"
        )

        st.write(
            f"**County:** "
            f"{location.get('county') or 'Not available'}"
        )

        st.write(
            f"**City:** "
            f"{location.get('city') or 'Not available'}"
        )

        st.write(
            f"**ZIP:** "
            f"{location.get('zip') or 'Not available'}"
        )

        st.write(
            f"**Latitude:** "
            f"{location.get('latitude') or 'Not available'}"
        )

        st.write(
            f"**Longitude:** "
            f"{location.get('longitude') or 'Not available'}"
        )

        st.write(
            f"**TIGER Line ID:** "
            f"{location.get('tigerline_id') or 'Not available'}"
        )

        st.write(
            f"**TIGER Line Side:** "
            f"{location.get('tigerline_side') or 'Not available'}"
        )

        with st.spinner(
            "Identifying Census geographic jurisdictions..."
        ):

            try:
                geography_data = census_geographies(
                    address
                )

            except Exception as e:

                st.warning(
                    "Census geographic lookup failed: "
                    f"{e}"
                )

        if geography_data:

            st.subheader(
                "Census Geographic Jurisdictions"
            )

            st.json(geography_data)

        parcel_source = get_parcel_source(
            location.get("state"),
            location.get("county")
        )

        if parcel_source:

            st.subheader(
                "Parcel Source"
            )

            st.write(
                f"**Provider:** "
                f"{parcel_source.get('provider')}"
            )

            st.write(
                f"**Status:** "
                f"{parcel_source.get('status')}"
            )

            st.write(
                f"**Notes:** "
                f"{parcel_source.get('notes')}"
            )

    else:

        st.error(
            "The Census Geocoder could not locate "
            "this address."
        )

        st.info(
            "Try entering the address as "
            "street, city, state, ZIP."
        )

    st.divider()

    st.subheader("KGIS Diagnostic")

    with st.spinner(
        "Checking KGIS parcel source..."
    ):

        try:

            parcel_result = find_kgis_property(
                address
            )

        except Exception as e:

            parcel_result = {
                "source": "KGIS",
                "error": str(e)
            }

    if parcel_result:

        st.write(
            f"**Source:** "
            f"{parcel_result.get('source')}"
        )

        st.write(
            f"**Method:** "
            f"{parcel_result.get('method')}"
        )

        if parcel_result.get("error"):

            st.error(
                f"KGIS error: "
                f"{parcel_result.get('error')}"
            )

        raw_results = parcel_result.get(
            "results",
            []
        )

        if raw_results:

            for item in raw_results:

                if isinstance(item, dict):

                    st.write(
                        "### KGIS Result"
                    )

                    st.json(item)

                else:

                    st.write(item)

        else:

            st.warning(
                "KGIS returned no diagnostic results."
            )

        if parcel_result.get("raw_response"):

            st.write(
                "### Raw KGIS Response"
            )

            st.json(
                parcel_result.get(
                    "raw_response"
                )
            )

    else:

        st.error(
            "No response was returned "
            "by the KGIS connector."
        )
