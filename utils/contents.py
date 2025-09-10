import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
from config import (
    Columns,
    ChartConfig,
    DefaultFilters
)


# --- Common Mapbox ---
def stream_data(strings):
    for char in strings:
        yield char
        time.sleep(0.01)


# --- Cargo Transfer.py ---
def make_cargo_route_pie_chart(df, airport_ref):
    grouped_df = (
        df.groupby([Columns.FLIGHT_DATE, Columns.DEPARTURE, Columns.ARRIVAL])[Columns.TOTAL_WEIGHT]
        .sum()
        .reset_index(name=Columns.TOTAL_WEIGHT)
    )
    
    for io in [Columns.DEPARTURE, Columns.ARRIVAL]:
        grouped_df = pd.merge(
            grouped_df,
            airport_ref,
            left_on=io,
            right_on=[Columns.IATA],
            how="left",
        )
    
    grouped_df = grouped_df[
        (grouped_df[f"{Columns.IATA}_x"].notnull()) & (grouped_df[f"{Columns.IATA}_y"].notnull())
    ]
    
    selected_checkboxes = st.multiselect(
        "-",
        [
            "출발지역",
            "출발국가", 
            "출발도시",
            "도착지역",
            "도착국가",
            "도착도시",
        ],
        key="cargo_route_pie_chart",
        default=DefaultFilters.PIE_CHART_DEFAULTS,
    )

    path_dict = {
        "출발지역": f"{Columns.REGION_NAME}_x",
        "출발국가": f"{Columns.COUNTRY_NAME}_x",
        "출발도시": f"{Columns.CITY_NAME}_x",
        "도착지역": f"{Columns.REGION_NAME}_y",
        "도착국가": f"{Columns.COUNTRY_NAME}_y",
        "도착도시": f"{Columns.CITY_NAME}_y",
    }
    
    path = [path_dict[checkbox] for checkbox in selected_checkboxes]
    
    if len(path) != 0:
        caption = " ➡️ ".join(selected_checkboxes)
        st.caption(f"[상세설명] {caption} 순으로 행선지를 표기합니다.")
        graph_df = grouped_df.groupby(path)[Columns.TOTAL_WEIGHT].sum().reset_index()
        fig = px.sunburst(
            graph_df,
            path=path,
            values=Columns.TOTAL_WEIGHT,
            height=ChartConfig.PIE_CHART_HEIGHT,
        )
        fig.update_traces(
            textinfo="label+value+percent parent",
            texttemplate="%{label} <br> %{value:,.0f}톤 <br> (%{percentRoot:.1%})",
        )
        fig = fig.update_layout(margin=dict(t=1, l=1, r=1, b=1))
        return fig
    return None


def make_cargo_mapbox(df, airport_ref, io):
    grouped_df = df.groupby([io])[Columns.TOTAL_WEIGHT].sum().reset_index(name=Columns.TOTAL_WEIGHT)
    grouped_df = pd.merge(
        grouped_df,
        airport_ref,
        left_on=io,
        right_on=[Columns.IATA],
        how="left",
    )
    
    px_path = [
        Columns.REGION_NAME,
        Columns.COUNTRY_NAME,
        Columns.CITY_NAME,
        Columns.IATA,
        Columns.LATITUDE,
        Columns.LONGITUDE,
    ]
    
    mapbox_df = grouped_df.groupby(px_path)[Columns.TOTAL_WEIGHT].sum().reset_index(name=Columns.TOTAL_WEIGHT)
    hover_data = [
        Columns.IATA,
        Columns.CITY_NAME,
        Columns.COUNTRY_NAME,
        Columns.TOTAL_WEIGHT,
    ]

    fig = px.scatter_mapbox(
        mapbox_df,
        lat=Columns.LATITUDE,
        lon=Columns.LONGITUDE,
        mapbox_style=ChartConfig.MAPBOX_STYLE,
        color=Columns.TOTAL_WEIGHT,
        color_continuous_scale=getattr(px.colors.sequential, ChartConfig.COLOR_SCALE),
        size=Columns.TOTAL_WEIGHT,
        hover_data=hover_data,
        zoom=ChartConfig.DEFAULT_ZOOM,
        height=ChartConfig.MAP_HEIGHT,
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    return fig


def make_cargo_treemap(df):
    selected_checkboxes = st.multiselect(
        "-",
        [Columns.PASSENGER_CARGO, Columns.AIRLINE_NAME, "Acft Name"],
        default=DefaultFilters.TREEMAP_DEFAULTS,
    )
    st.caption("* 선택한 순서대로 하위 그룹을 표기합니다.")
    
    path = selected_checkboxes
    if len(path) != 0:
        graph_df = df.groupby(path)[Columns.TOTAL_WEIGHT].sum().reset_index()
        fig = px.treemap(
            graph_df,
            path=path,
            values=Columns.TOTAL_WEIGHT,
            height=ChartConfig.TREEMAP_HEIGHT,
        )
        fig.update_traces(
            textinfo="label+value+percent parent",
            texttemplate="%{label} <br> %{value:,.0f}톤 <br> (%{percentRoot:.1%})",
            textfont=dict(size=16),
            hoverinfo="label+value+percent parent", 
            textposition="middle center",
        )
        fig = fig.update_layout(margin=dict(t=1, l=1, r=1, b=1))
        return fig


# --- Cargo Airline Analysis Functions ---
def make_cargo_airline_stream_text(df):
    """항공사별 화물 분석 요약 텍스트 출력"""
    st.subheader(f"👨🏽 Summary")
    화물기총량 = df[df[Columns.PASSENGER_CARGO] == "화물"][Columns.TOTAL_WEIGHT].sum()
    여객기총량 = df[df[Columns.PASSENGER_CARGO] == "여객"][Columns.TOTAL_WEIGHT].sum()
    총량 = df[Columns.TOTAL_WEIGHT].sum()
    text = f"""
        * [기간] {df[Columns.FLIGHT_DATE].dt.date.min()} ~ {df[Columns.FLIGHT_DATE].dt.date.max()}
        * [운항편수] {len(df[[Columns.FLIGHT_DATE, Columns.FLIGHT_NUM]].drop_duplicates()):,}편
        * [총 환적중량] {총량:,.0f}톤 (화물: {화물기총량/총량*100:,.1f}%, 여객: {여객기총량/총량*100:,.1f}%)
        """
    st.write_stream(stream_data(text))


def make_cargo_airline_treemap(df):
    """항공사별 기종 사용 현황 트리맵"""
    path = ["Acft Name"]
    graph_df = df.groupby(path)[Columns.TOTAL_WEIGHT].sum().reset_index()
    graph_df[Columns.TOTAL_WEIGHT] = graph_df[Columns.TOTAL_WEIGHT].astype(int)
    fig = px.treemap(
        graph_df,
        path=path,
        values=Columns.TOTAL_WEIGHT,
        height=ChartConfig.TREEMAP_HEIGHT,
    )
    fig.update_traces(
        textinfo="label+value+percent parent",
        texttemplate="%{label} <br> %{value:,.0f}톤 <br> (%{percentRoot:.1%})",
        textfont=dict(size=16),
        hoverinfo="label+value+percent parent",
        textposition="middle center",
    )
    fig = fig.update_layout(margin=dict(t=1, l=1, r=1, b=1))
    return fig


def make_cargo_airline_ranking_bar(df, compare_df, col):
    """항공사별 순위 바 차트 (전년 대비)"""
    integer_input = 20
    rank_figure = (
        df.groupby([col])[Columns.TOTAL_WEIGHT]
        .sum()
        .reset_index()
        .sort_values(by=Columns.TOTAL_WEIGHT, ascending=False)
    )
    total = rank_figure[Columns.TOTAL_WEIGHT].sum()
    compare_rank = (
        compare_df.groupby([col])[Columns.TOTAL_WEIGHT].sum().reset_index(name="전년실적")
    )
    rank_figure["점유율(%)"] = round(rank_figure[Columns.TOTAL_WEIGHT] / total * 100, 2)
    rank_figure2 = pd.merge(rank_figure, compare_rank, on=col, how="left")
    rank_figure2["전년대비증가율(%)"] = round(
        (rank_figure2[Columns.TOTAL_WEIGHT] - rank_figure2["전년실적"])
        / rank_figure2["전년실적"]
        * 100,
        2,
    )
    rank_figure2[Columns.TOTAL_WEIGHT] = rank_figure2[Columns.TOTAL_WEIGHT].fillna(0).astype(int)
    rank_figure2["전년실적"] = rank_figure2["전년실적"].fillna(0).astype(int)
    
    # 데이터프레임 표시용 포맷팅 적용
    rank_figure2_display = rank_figure2.copy()
    rank_figure2_display[Columns.TOTAL_WEIGHT] = rank_figure2_display[Columns.TOTAL_WEIGHT].apply(lambda x: f"{x:,}")
    rank_figure2_display["전년실적"] = rank_figure2_display["전년실적"].apply(lambda x: f"{x:,}")
    
    # 전년대비증가율 포맷팅 (NaN, inf 값 처리)
    def format_growth_rate(x):
        if pd.isna(x) or x == float('inf') or x == float('-inf'):
            return "No Data"
        else:
            return f"{x:,.1f}%"
    
    rank_figure2_display["전년대비증가율(%)"] = rank_figure2_display["전년대비증가율(%)"].apply(format_growth_rate)
    
    # 점유율 포맷팅
    rank_figure2_display["점유율(%)"] = rank_figure2_display["점유율(%)"].apply(lambda x: f"{x:.1f}%" if not pd.isna(x) else "0.0%")
    
    figure_df = rank_figure2.head(integer_input)
    fig = px.bar(
        figure_df,
        x=Columns.TOTAL_WEIGHT,
        y=col,
        text=figure_df.apply(
            lambda x: f"{x[Columns.TOTAL_WEIGHT]:,.0f}톤 ({x['점유율(%)']}%)",
            axis=1,
        ),
        template="plotly_dark",
        color=col,
        hover_data=[Columns.TOTAL_WEIGHT],
        orientation="h",
        height=max(len(figure_df) * 40, 200),
    )
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
    )
    fig.update_traces(
        textfont=dict(color="white", family="Arial"),
        showlegend=False,
    )
    return fig, rank_figure2_display
