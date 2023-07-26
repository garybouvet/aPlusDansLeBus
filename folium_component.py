import streamlit.components.v1 as components

def st_folium(m, width=700, height=500, **kwargs):
    """
    Create a Streamlit Folium component.
    """
    # Serialize the Folium map to a JSON string
    json_map = m.to_json()

    # Create a unique key for the component to avoid duplicate rendering
    key = f"folium_map_{hash(json_map)}"

    # Set up the component with the given properties
    component_value = components.declare_component(
        "folium_map",
        json_map=json_map,
        key=key,
        width=width,
        height=height,
        **kwargs
    )

    return component_value
