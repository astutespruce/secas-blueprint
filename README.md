# SECAS Southeast Conservation Blueprint Explorer

This application provides a simple user interface for exploring the [SECAS Southeast Conservation Blueprint](http://secassoutheast.org/blueprint.html).

## Architecture

This uses a data processing pipeline in Python to prepare all spatial data for use in this application.

The user interface is creating using GatsbyJS as a static web application.

The API is implemented in Python and provides summary reports for pre-defined summary units and user-defined areas.
