from drf_spectacular.utils import extend_schema_view


@extend_schema_view(tags=["General"])
def placeholder(request=None):
    # The actual schema endpoints are wired in api/urls.py using drf-spectacular.
    # This module is kept as a hook for future schema customizations.
    return None

