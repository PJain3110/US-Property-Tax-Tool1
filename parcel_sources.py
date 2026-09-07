# Parcel GIS source registry
#
# Each county will eventually have its own parcel
# data configuration. The application will use
# state + county to select the appropriate source.


PARCEL_SOURCES = {

    "TN": {

        "Knox County": {

            "provider": "KGIS",

            "status": "configured",

            "notes": (
                "Knox County parcel data is provided "
                "through the Knox County GIS system."
            )
        }

    }

}
