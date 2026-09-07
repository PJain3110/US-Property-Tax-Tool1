import streamlit as st
import requests

st.set_page_config(
    page_title="US Property Tax Tool",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 US Property Tax Tool")
st.subheader("Step 1 — Property Location Identification")

address = st.text_input(
    "Property Address",
    placeholder="2165 Casablanca Way, Knoxville, TN 37932"
)


def geocode_address(address):

    # ---------------------------------
    # 1. Try U.S. Census Geocoder
    # ---------------------------------

    census_url = (
        "https://geocoding.geo.census.gov/"
        "geocoder/geographies/onelineaddress"
    )

    census_params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }

    response = requests.get(
        census_url,
        params=census_params,
        timeout=20
    )

    response.raise_for_status()

    census_data = response.json()

    census_matches = (
        census_data
        .get("result", {})
        .get("addressMatches", [])
    )

    if census_matches:
        return census_data, "U.S. Census Geocoder"


    # ---------------------------------
    # 2. If Census fails, try Nominatim
    # ---------------------------------

    nominatim_url = (
        "https://nominatim.openstreetmap.org/search"
    )

    nominatim_params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }

    nominatim_headers = {
        "User-Agent": "US-Property-Tax-Tool1"
    }

    response = requests.get(
        nominatim_url,
        params=nominatim_params,
        headers=nominatim_headers,
        timeout=20
    )

    response.raise_for_status()

    nominatim_data = response.json()

    if nominatim_data:

        result = nominatim_data[0]

        return {
            "result": {
                "addressMatches": [
                    {
                        "matchedAddress": result.get(
                            "display_name",
                            address
                        ),
                        "coordinates": {
                            "x": result.get("lon"),
                            "y": result.get("lat")
                        },
                        "addressComponents": {
                            "city": result.get(
                                "address", {}
                            ).get("city")
                            or result.get(
                                "address", {}
                            ).get("town")
                            or result.get(
                                "address", {}
                            ).get("village"),
                            "state": result.get(
                                "address", {}
                            ).get("state"),
                            "zip": result.get(
                                "address", {}
                            ).get("postcode")
                        },
                        "geographies": {}
                    }
                ]
            }
        }, "OpenStreetMap"


    # ---------------------------------
    # 3. Nothing found
    # ---------------------------------

    return {
        "result": {
            "addressMatches": []
        }
    }, None


if st.button("Find Property", type="primary"):

    if not address.strip():

        st.warning(
            "Please enter a property address."
        )

    else:

        try:

            with st.spinner(
                "Looking up property..."
            ):

                data, source = geocode_address(
                    address.strip()
                )

            matches = (
                data
                .get("result", {})
                .get("addressMatches", [])
            )

            if not matches:

                st.error(
                    "No matching address was found. "
                    "Please check the address and try again."
                )

            else:

                match = matches[0]

                address_components = match.get(
                    "addressComponents",
                    {}
                )

                coordinates = match.get(
                    "coordinates",
                    {}
                )

                geographies = match.get(
                    "geographies",
                    {}
                )

                state_geo = None
                county_geo = None
                place_geo = None

                for key, values in geographies.items():

                    if not values:
                        continue

                    if "States" in key:
                        state_geo = values[0]

                    elif "Counties" in key:
                        county_geo = values[0]

                    elif "Places" in key:
                        place_geo = values[0]


                st.success(
                    f"Property located successfully "
                    f"using {source}."
                )

                st.divider()

                st.header(
                    "Property Location"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "State",
                        address_components.get(
                            "state",
                            "—"
                        )
                    )

                    st.metric(
                        "County",
                        county_geo.get(
                            "NAME",
                            "—"
                        )
                        if county_geo
                        else "Not available"
                    )

                with col2:

                    st.metric(
                        "City",
                        address_components.get(
                            "city",
                            "—"
                        )
                    )

                    st.metric(
                        "ZIP Code",
                        address_components.get(
                            "zip",
                            "—"
                        )
                    )

                with col3:

                    st.metric(
                        "Latitude",
                        coordinates.get(
                            "y",
                            "—"
                        )
                    )

                    st.metric(
                        "Longitude",
                        coordinates.get(
                            "x",
                            "—"
                        )
                    )


                st.header(
                    "Geographic Identifiers"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "State FIPS",
                        state_geo.get(
                            "STATE",
                            "—"
                        )
                        if state_geo
                        else "Not available"
                    )

                with col2:

                    st.metric(
                        "County FIPS",
                        county_geo.get(
                            "COUNTY",
                            "—"
                        )
                        if county_geo
                        else "Not available"
                    )

                with col3:

                    st.metric(
                        "Place FIPS",
                        place_geo.get(
                            "PLACE",
                            "—"
                        )
                        if place_geo
                        else "Not available"
                    )


                st.header(
                    "Standardized Address"
                )

                st.info(
                    match.get(
                        "matchedAddress",
                        "No standardized address returned."
                    )
                )


        except requests.exceptions.RequestException as e:

            st.error(
                f"Unable to connect to the "
                f"address service: {e}"
            )

        except Exception as e:

            st.error(
                f"An unexpected error occurred: {e}"
            )
