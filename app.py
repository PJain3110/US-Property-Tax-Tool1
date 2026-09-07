import streamlit as st
import requests

from parcel_sources import PARCEL_SOURCES


st.set_page_config(
    page_title="US Property Tax Tool",
    page_icon="🏠",
    layout="wide"
)


st.title("🏠 US Property Tax Tool")
st.subheader("Property Location & Tax Jurisdiction Research")


address = st.text_input(
    "Property Address",
    placeholder="2165 Casablanca Way, Knoxville, TN 37932"
)


def census_geocode(address):

    url = (
        "https://geocoding.geo.census.gov/"
        "geocoder/geographies/onelineaddress"
    )

    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def nominatim_geocode(address):

    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }

    headers = {
        "User-Agent": "US-Property-Tax-Tool1"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def find_location(address):

    # ---------------------------------------------------------
    # CENSUS GEOCODER
    # ---------------------------------------------------------

    census_data = census_geocode(address)

    matches = (
        census_data
        .get("result", {})
        .get("addressMatches", [])
    )

    if matches:

        match = matches[0]

        components = match.get(
            "addressComponents",
            {}
        )

        geographies = match.get(
            "geographies",
            {}
        )

        county_data = {}
        state_data = {}
        place_data = {}

        for key, value in geographies.items():

            if isinstance(value, list) and value:
                value = value[0]

            if not isinstance(value, dict):
                continue

            if "County" in key:
                county_data = value

            if (
                "State" in key
                and "County" not in key
            ):
                state_data = value

            if "Place" in key:
                place_data = value

        return {
            "source": "U.S. Census Geocoder",

            "address": match.get(
                "matchedAddress",
                address
            ),

            "latitude": match.get(
                "coordinates",
                {}
            ).get("y"),

            "longitude": match.get(
                "coordinates",
                {}
            ).get("x"),

            "state": components.get(
                "state"
            ),

            "county": components.get(
                "county"
            ),

            "city": components.get(
                "city"
            ),

            "zip": components.get(
                "zip"
            ),

            "state_fips": (
                state_data.get("GEOID")
                or state_data.get("STATE")
            ),

            "county_fips": (
                county_data.get("GEOID")
                or county_data.get("COUNTY")
            ),

            "place_fips": (
                place_data.get("GEOID")
                or place_data.get("PLACE")
            )
        }

    # ---------------------------------------------------------
    # OPENSTREETMAP FALLBACK
    # ---------------------------------------------------------

    osm_data = nominatim_geocode(address)

    if osm_data:

        result = osm_data[0]

        result_address = result.get(
            "address",
            {}
        )

        return {
            "source": "OpenStreetMap",

            "address": result.get(
                "display_name",
                address
            ),

            "latitude": result.get(
                "lat"
            ),

            "longitude": result.get(
                "lon"
            ),

            "state": result_address.get(
                "state"
            ),

            "county": result_address.get(
                "county"
            ),

            "city": (
                result_address.get("city")
                or result_address.get("town")
                or result_address.get("village")
                or result_address.get("municipality")
            ),

            "zip": result_address.get(
                "postcode"
            ),

            "state_fips": None,
            "county_fips": None,
            "place_fips": None
        }

    return None


def get_parcel_source(state, county):

    if not state or not county:
        return None

    state_sources = PARCEL_SOURCES.get(
        state.upper(),
        {}
    )

    # Try exact county name first
    source = state_sources.get(
        county
    )

    if source:
        return source

    # Try county name without "County"
    county_without_suffix = (
        county
        .replace(" County", "")
        .strip()
    )

    for name, source_data in state_sources.items():

        clean_name = (
            name
            .replace(" County", "")
            .strip()
        )

        if clean_name.lower() == county_without_suffix.lower():
            return source_data

    return None


if st.button(
    "Find Property",
    type="primary"
):

    if not address.strip():

        st.warning(
            "Please enter a property address."
        )

    else:

        try:

            with st.spinner(
                "Identifying property..."
            ):

                location = find_location(
                    address.strip()
                )

            if location is None:

                st.error(
                    "The address could not be "
                    "located by the available "
                    "geocoding services."
                )

            else:

                st.success(
                    "Address located successfully."
                )

                st.caption(
                    f"Location source: "
                    f"{location['source']}"
                )

                st.divider()

                # -------------------------------------------------
                # PROPERTY LOCATION
                # -------------------------------------------------

                st.header(
                    "Property Location"
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "State",
                        location["state"] or "—"
                    )

                with col2:
                    st.metric(
                        "County",
                        location["county"] or "—"
                    )

                with col3:
                    st.metric(
                        "City",
                        location["city"] or "—"
                    )

                with col4:
                    st.metric(
                        "ZIP Code",
                        location["zip"] or "—"
                    )

                # -------------------------------------------------
                # COORDINATES
                # -------------------------------------------------

                st.header(
                    "Coordinates"
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Latitude",
                        location["latitude"] or "—"
                    )

                with col2:
                    st.metric(
                        "Longitude",
                        location["longitude"] or "—"
                    )

                # -------------------------------------------------
                # GEOGRAPHIC IDENTIFIERS
                # -------------------------------------------------

                st.header(
                    "Government Geographic Identifiers"
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "State FIPS",
                        location["state_fips"] or "—"
                    )

                with col2:
                    st.metric(
                        "County FIPS",
                        location["county_fips"] or "—"
                    )

                with col3:
                    st.metric(
                        "Place FIPS",
                        location["place_fips"] or "—"
                    )

                # -------------------------------------------------
                # STANDARDIZED ADDRESS
                # -------------------------------------------------

                st.header(
                    "Standardized Address"
                )

                st.info(
                    location["address"]
                )

                # -------------------------------------------------
                # PARCEL SOURCE
                # -------------------------------------------------

                st.header(
                    "Parcel Research"
                )

                parcel_source = get_parcel_source(
                    location["state"],
                    location["county"]
                )

                if parcel_source:

                    st.success(
                        "A parcel data source is "
                        "configured for this county."
                    )

                    st.write(
                        f"**Provider:** "
                        f"{parcel_source['provider']}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{parcel_source['status']}"
                    )

                    st.caption(
                        parcel_source["notes"]
                    )

                else:

                    st.warning(
                        "No parcel data source is "
                        "currently configured for "
                        "this county."
                    )

                    st.caption(
                        "The application is designed "
                        "to support county-specific "
                        "parcel sources as they are added."
                    )

                # -------------------------------------------------
                # TAX JURISDICTION ANALYSIS
                # -------------------------------------------------

                st.header(
                    "Tax Jurisdiction Analysis"
                )

                st.info(
                    "Parcel-level jurisdiction "
                    "analysis will be performed "
                    "after the parcel GIS connection "
                    "is added."
                )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Address service error: {e}"
            )

        except Exception as e:

            st.error(
                f"Unexpected error: {e}"
            )
