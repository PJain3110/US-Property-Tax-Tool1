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
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

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

    matches = data.get("result", {}).get("addressMatches", [])

    if not matches:
        return None

    match = matches[0]

    coordinates = match.get("coordinates", {})
    address_components = match.get("addressComponents", {})

    return {
        "matched_address": match.get("matchedAddress"),
        "longitude": coordinates.get("x"),
        "latitude": coordinates.get("y"),
        "state": address_components.get("state"),
        "county": address_components.get("countyName"),
        "city": address_components.get("city"),
        "zip": address_components.get("zip")
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

    state_sources = PARCEL_SOURCES.get(state.upper())

    if not state_sources:
        return None

    for county_name, source in state_sources.items():

        if county_name.lower() in county.lower():
            return source

    return None


if address:

    st.divider()

    with st.spinner("Searching property records..."):

        # ---------------------------------------------------------
        # STEP 1: Try Census
        # ---------------------------------------------------------

        location = None

        try:
            location = census_geocode(address)
        except Exception:
            location = None

        # ---------------------------------------------------------
        # STEP 2: Try OpenStreetMap
        # ---------------------------------------------------------

        if not location:

            try:
                location = nominatim_geocode(address)
            except Exception:
                location = None

        # ---------------------------------------------------------
        # STEP 3: Try configured parcel systems
        #
        # This is especially important when generic geocoders
        # cannot locate the property.
        # ---------------------------------------------------------

        parcel_result = None

        try:
            parcel_result = find_kgis_property(address)
        except Exception:
            parcel_result = None

        # ---------------------------------------------------------
        # DISPLAY LOCATION INFORMATION
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
        # DISPLAY PARCEL INFORMATION
        # ---------------------------------------------------------

        if parcel_result:

            st.divider()

            st.subheader("Parcel Information")

            st.success(
                f"Parcel source found: {parcel_result.get('source')}"
            )

            st.write(
                f"**Method:** "
                f"{parcel_result.get('method')}"
            )

            results = parcel_result.get("results", [])

            if results:

                for index, feature in enumerate(results, start=1):

                    attributes = feature.get("attributes", {})
                    geometry = feature.get("geometry", {})

                    st.write(f"### Parcel Result {index}")

                    # Display useful fields when available.
                    for field in [
                        "PARCELID",
                        "FULL_ADDRESS",
                        "OWNER",
                        "OWNER_NAME",
                        "SITE_ADDRESS"
                    ]:

                        value = attributes.get(field)

                        if value not in [None, ""]:
                            st.write(
                                f"**{field}:** {value}"
                            )

                    if geometry:

                        st.write(
                            "**Parcel geometry:** Available"
                        )

        elif not location:

            st.error(
                "The address could not be located through the "
                "available address and parcel systems."
            )

        # ---------------------------------------------------------
        # PARCEL SOURCE STATUS
        # ---------------------------------------------------------

        if location:

            state = location.get("state")
            county = location.get("county")

            parcel_source = get_parcel_source(
                state,
                county
            )

            st.divider()

            st.subheader("Parcel Data Source")

            if parcel_source:

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

                st.info(
                    "A county-specific parcel provider has not "
                    "yet been configured for this location."
                )
