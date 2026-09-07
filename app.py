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
    placeholder="1600 Pennsylvania Avenue NW, Washington, DC 20500"
)


def geocode_address(address):
    url = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"

    params = {
        "address": address,
        "benchmark": "Public_AR_Current",
        "vintage": "Current_Current",
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    return response.json()


if st.button("Find Property", type="primary"):

    if not address.strip():
        st.warning("Please enter a property address.")

    else:

        try:
            with st.spinner("Looking up property..."):

                data = geocode_address(address.strip())

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
                    "addressComponents", {}
                )

                coordinates = match.get(
                    "coordinates", {}
                )

                geographies = match.get(
                    "geographies", {}
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

                st.success("Property located successfully.")

                st.divider()

                st.header("Property Location")

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "State",
                        address_components.get("state", "—")
                    )

                    st.metric(
                        "County",
                        county_geo.get("NAME", "—")
                        if county_geo else "—"
                    )

                with col2:

                    st.metric(
                        "City",
                        address_components.get("city", "—")
                    )

                    st.metric(
                        "ZIP Code",
                        address_components.get("zip", "—")
                    )

                with col3:

                    st.metric(
                        "Latitude",
                        coordinates.get("y", "—")
                    )

                    st.metric(
                        "Longitude",
                        coordinates.get("x", "—")
                    )

                st.header("Geographic Identifiers")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "State FIPS",
                        state_geo.get("STATE", "—")
                        if state_geo else "—"
                    )

                with col2:
                    st.metric(
                        "County FIPS",
                        county_geo.get("COUNTY", "—")
                        if county_geo else "—"
                    )

                with col3:
                    st.metric(
                        "Place FIPS",
                        place_geo.get("PLACE", "—")
                        if place_geo else "—"
                    )

                st.header("Standardized Address")

                st.info(
                    match.get(
                        "matchedAddress",
                        "No standardized address returned."
                    )
                )

        except requests.exceptions.RequestException as e:

            st.error(
                f"Unable to connect to the Census Geocoder: {e}"
            )

        except Exception as e:

            st.error(
                f"An unexpected error occurred: {e}"
            )
