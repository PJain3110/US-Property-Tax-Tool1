import streamlit as st
import requests

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
    url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"

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

    # Try Census first
    census_data = census_geocode(address)

    census_matches = (
        census_data
        .get("result", {})
        .get("addressMatches", [])
    )

    if census_matches:

        match = census_matches[0]

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
            "components": match.get(
                "addressComponents",
                {}
            ),
            "geographies": match.get(
                "geographies",
                {}
            )
        }

    # Try OpenStreetMap second
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
            "latitude": result.get("lat"),
            "longitude": result.get("lon"),
            "components": {
                "city": (
                    result_address.get("city")
                    or result_address.get("town")
                    or result_address.get("village")
                ),
                "state": result_address.get(
                    "state"
                ),
                "zip": result_address.get(
                    "postcode"
                )
            },
            "geographies": {}
        }

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

                st.info(
                    "The next version will use "
                    "county-level parcel GIS data "
                    "for properties that cannot be "
                    "resolved through standard "
                    "address geocoding."
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

                st.header(
                    "Property Location"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "State",
                        location[
                            "components"
                        ].get(
                            "state",
                            "—"
                        )
                    )

                with col2:

                    st.metric(
                        "City",
                        location[
                            "components"
                        ].get(
                            "city",
                            "—"
                        )
                    )

                with col3:

                    st.metric(
                        "ZIP Code",
                        location[
                            "components"
                        ].get(
                            "zip",
                            "—"
                        )
                    )

                st.header(
                    "Coordinates"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Latitude",
                        location[
                            "latitude"
                        ]
                        or "—"
                    )

                with col2:

                    st.metric(
                        "Longitude",
                        location[
                            "longitude"
                        ]
                        or "—"
                    )

                st.header(
                    "Standardized Address"
                )

                st.info(
                    location[
                        "address"
                    ]
                )

                st.header(
                    "Tax Jurisdiction Analysis"
                )

                st.warning(
                    "Parcel and taxing-jurisdiction "
                    "research will be added in the "
                    "next step."
                )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Address service error: {e}"
            )

        except Exception as e:

            st.error(
                f"Unexpected error: {e}"
            )
