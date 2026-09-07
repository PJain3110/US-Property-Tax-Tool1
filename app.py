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


def census_geocode(address):
    url = (
        "https://geocoding.geo.census.gov/geocoder/"
        "locations/onelineaddress"
    )

    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    matches = data.get(
        "result",
        {}
    ).get(
        "addressMatches",
        []
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
        "matched_address": match.get("matchedAddress"),
        "longitude": coordinates.get("x"),
        "latitude": coordinates.get("y"),
        "state": components.get("state"),
        "county": components.get("countyName"),
        "city": components.get("city"),
        "zip": components.get("zip")
    }


def nominatim_geocode(address):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }

    headers = {
        "User-Agent": "US-Property-Tax-Tool/1.0"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        return None

    result = results[0]
    details = result.get("address", {})

    return {
        "matched_address": result.get("display_name"),
        "longitude": result.get("lon"),
        "latitude": result.get("lat"),
        "state": details.get("state"),
        "county": details.get("county"),
        "city": (
            details.get("city")
            or details.get("town")
            or details.get("village")
            or details.get("municipality")
        ),
        "zip": details.get("postcode")
    }


def get_parcel_source(state, county):

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

    # ---------------------------------------------------------
    # LOCATION SEARCH
    # ---------------------------------------------------------

    location = None

    with st.spinner("Searching address..."):

        try:
            location = census_geocode(address)
        except Exception:
            location = None

        if not location:

            try:
                location = nominatim_geocode(address)
            except Exception:
                location = None

    # ---------------------------------------------------------
    # KGIS SEARCH
    # ---------------------------------------------------------

    with st.spinner("Searching parcel records..."):

        try:

            parcel_result = find_kgis_property(
                address
            )

        except Exception as e:

            parcel_result = {
                "source": "KGIS",
                "error": str(e)
            }

    # ---------------------------------------------------------
    # LOCATION
    # ---------------------------------------------------------

    if location:

        st.success("Address located.")

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

    # ---------------------------------------------------------
    # KGIS RAW DIAGNOSTIC
    # ---------------------------------------------------------

    st.divider()

    st.subheader("KGIS Diagnostic")

    if parcel_result:

        st.write(
            f"**Source:** "
            f"{parcel_result.get('source')}"
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

                st.write(
                    f"### Layer: "
                    f"{item.get('layer')}"
                )

                st.write(
                    f"**Layer ID:** "
                    f"{item.get('layer_id')}"
                )

                st.write(
                    f"**Success:** "
                    f"{item.get('success')}"
                )

                if item.get("error"):

                    st.error(
                        item.get("error")
                    )

                if item.get("response"):

                    response = item.get(
                        "response"
                    )

                    st.json(response)

        else:

            st.warning(
                "KGIS returned no diagnostic results."
            )

    else:

        st.error(
            "No response was returned by the KGIS connector."
        )
