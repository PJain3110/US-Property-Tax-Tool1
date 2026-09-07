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


def parse_address(address):
    """
    Parse a standard U.S. address into:
    street, city, state, ZIP.
    """

    parts = [
        part.strip()
        for part in address.split(",")
    ]

    if len(parts) < 3:
        return None

    street = parts[0]
    city = parts[1]

    state_zip = parts[2].split()

    if len(state_zip) < 1:
        return None

    state = state_zip[0]

    zip_code = ""

    if len(state_zip) >= 2:
        zip_code = state_zip[1]

    return {
        "street": street,
        "city": city,
        "state": state,
        "zip": zip_code,
    }


def census_geocode(address):
    """
    Geocode an address using the Census structured
    address endpoint.
    """

    parsed = parse_address(address)

    if not parsed:
        return None

    url = (
        f"{CENSUS_GEOCODER_URL}/locations/address"
    )

    params = {
        "street": parsed["street"],
        "city": parsed["city"],
        "state": parsed["state"],
        "zip": parsed["zip"],
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
    Retrieve Census geographic jurisdictions
    for an address.
    """

    url = (
        f"{CENSUS_GEOCODER_URL}/geographies/"
        "address"
    )

    parsed = parse_address(address)

    if not parsed:
        return None

    params = {
        "street": parsed["street"],
        "city": parsed["city"],
        "state": parsed["state"],
        "zip": parsed["zip"],
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

            location = census_geocode(
                address
            )

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

            st.json(
                geography_data
            )

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

    st.divider()

    st.subheader(
        "Free Geocoder Diagnostic"
    )

    with st.spinner(
        "Checking Photon..."
    ):

        try:

            parcel_result = find_kgis_property(
                address
            )

        except Exception as e:

            parcel_result = {
                "source": "Photon",
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
                f"Geocoder error: "
                f"{parcel_result.get('error')}"
            )

        results = parcel_result.get(
            "results",
            []
        )

        if results:

            for item in results:

                st.write(
                    "### Geocoder Result"
                )

                st.write(
                    f"**Address:** "
                    f"{item.get('address')}"
                )

                st.write(
                    f"**Latitude:** "
                    f"{item.get('latitude')}"
                )

                st.write(
                    f"**Longitude:** "
                    f"{item.get('longitude')}"
                )

        else:

            st.warning(
                "No geocoder results found."
            )
