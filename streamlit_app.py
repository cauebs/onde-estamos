import random

import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.figure import Figure
from geopandas import GeoSeries, GeoDataFrame
from shapely import Point


@st.cache(persist=True, allow_output_mutation=True)
def load_country_and_states() -> tuple[GeoSeries, GeoDataFrame]:
    states = GeoDataFrame.from_file("BC250_2017_Unidade_Federacao_A.shp")
    country = states.dissolve()
    return country, states


def random_location_in(geometry: GeoSeries) -> Point:
    # b = geometry.bounds
    # while True:
    #     lng = random.uniform(b["minx"], b["maxx"])
    #     lat = random.uniform(b["miny"], b["maxy"])
    #     point = Point(lng, lat)
    #     if geometry.contains(point).any():
    #         return point
    lng_min, lat_min, lng_max, lat_max = geometry.bounds

    while True:
        lng = random.uniform(lng_min, lng_max)
        lat = random.uniform(lat_min, lat_max)
        point = Point(lng, lat)
        if geometry.contains(point):
            return point


def find_span(point: Point, geometries: GeoDataFrame) -> GeoSeries:
    spans = geometries[geometries.contains(point)]
    assert len(spans) == 1
    return spans.iloc[0]


def plot_country(country: GeoSeries, point: Point) -> Figure:
    fig, ax = plt.subplots()

    country.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)
    GeoSeries(point).plot(ax=ax, color="red", markersize=5)

    return fig


def plot_states(states: GeoDataFrame, point: Point) -> Figure:
    fig, ax = plt.subplots()

    states.geometry.plot(ax=ax, color="white", edgecolor="black", linewidth=0.5)
    GeoSeries(point).plot(ax=ax, color="red", markersize=5)

    for _, row in states.iterrows():
        center = row.geometry.centroid
        ax.annotate(
            text=row["sigla"],
            xy=(center.x, center.y),
            fontsize=5,
            ha="center",
        )

    return fig


brasil, states = load_country_and_states()
assert len(brasil.geometry) == 1
brasil_geometry = brasil.geometry

map = st.empty()
with st.form("game", clear_on_submit=True):
    choices = ["", *sorted(states["nome"])]
    guess = st.selectbox("Estado", choices)

    if not guess:
        random_index = random.randrange(len(states))
        random_state = states.iloc[random_index]
        st.session_state.point = random_location_in(random_state.geometry)

    submitted = st.form_submit_button("Enviar")
    if not submitted:
        map.pyplot(plot_country(brasil, st.session_state.point))
    else:
        map.pyplot(plot_states(states, st.session_state.point))

        right_answer = find_span(st.session_state.point, states)["nome"]
        if guess == right_answer:
            st.success(f"Acertou! Era {right_answer}")
        else:
            st.error(f"Errou! Era {right_answer}")

        if st.form_submit_button("Mais uma vez", type="primary"):
            del st.session_state.point
