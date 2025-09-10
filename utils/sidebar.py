import streamlit as st
import pandas as pd
import numpy as np
from config import (
    Columns, 
    ROUTE_MAPPING, 
    ROUTE_LIST,
    DefaultFilters
)


# --- Common ---
def filter_by_area(df, cols, key_prefix=""):
    # df = df[df[cols[-1]].notnull()] # 아래 selections 하고 같이 켜고 꺼야합니다.
    for col in cols:
        # selections = [""] + list(sorted(df[col].unique()))
        selections = [""] + list(sorted(df[col].dropna().unique()))
        selected = st.sidebar.selectbox(
            f"{col.split(' ')[0]} ({df[col].nunique():,.0f})",
            selections,
            key=f"{key_prefix}_{col}",
        )
        if selected != "":
            df = df[(df[col] == selected)]
    return df


def filter_by_days(df, day_column, key_prefix=""):
    st.sidebar.markdown("---")  # 구분선 추가
    st.sidebar.header("🗓️ 기간")
    try:
        df[day_column] = pd.to_datetime(df[day_column])
    except:
        pass
    year_filter = df[day_column].dt.year
    years = list(sorted(year_filter.unique()))
    # year = st.sidebar.selectbox("Year", years, key="year", placeholder="")
    year = st.sidebar.selectbox("Year", years, key=f"{key_prefix}_year")
    df = df[(year_filter == year)]
    quarter_filter = df[day_column].dt.quarter
    quarters = [f"{q}Q" for q in sorted(quarter_filter.unique())]  # Add 'Q' suffix
    # quarter = st.sidebar.multiselect("Quarter", quarters, key="quarter", placeholder="")
    quarter = st.sidebar.multiselect("Quarter", quarters, key=f"{key_prefix}_quarter")
    quarter2 = [int(value.split("Q")[0]) for value in quarter]
    if len(quarter2) != 0:
        df = df[quarter_filter.isin(quarter2)]
    month_filter = df[day_column].dt.month
    months = list(sorted(month_filter.unique()))
    # month = st.sidebar.multiselect("Month", months, key="month", placeholder="")
    month = st.sidebar.multiselect("Month", months, key=f"{key_prefix}_month")
    if len(month) != 0:
        df = df[month_filter.isin(month)]
    day_filter = df[day_column].dt.date
    days = list(sorted(day_filter.unique()))
    # day = st.sidebar.multiselect("Day", days, key="day", placeholder="")
    day = st.sidebar.multiselect("Day", days, key=f"{key_prefix}_day")
    if len(day) != 0:
        df = df[day_filter.isin(day)]
    return df


def add_custom_route_col_on_airport_ref(df, route_dict={}):
    df["Route Name"] = None
    for key, value in route_dict.items():
        df.loc[
            (
                (df["Country Name"] == key)
                | (df["SubRegion Name"] == key)
                | (df["Region Name"] == key)
            )
            & (df["Route Name"].isna()),
            "Route Name",
        ] = value
    df["Route Name"] = df["Route Name"].fillna("기타")
    return df


# --- Cargo.py ---
def merge_cargo_data_with_ref(df, airline_ref, airport_ref, aircraft_ref):
    # 항공사 정보 병합
    df = pd.merge(df, airline_ref, on=Columns.AIRLINE, how="left")
    
    # 항공기 정보 병합
    df = pd.merge(df, aircraft_ref, left_on=Columns.AIRCRAFT_TYPE, right_on=Columns.IATA, how="left")
    df.drop([Columns.IATA], axis=1, inplace=True)
    
    # 공항 참조 데이터에 노선 정보 추가
    airport_ref = add_custom_route_col_on_airport_ref(airport_ref, route_dict=ROUTE_MAPPING)
    airport_ref_cols = [
        Columns.IATA,
        Columns.CITY_NAME,
        Columns.COUNTRY_NAME,
        Columns.REGION_NAME,
        Columns.ROUTE_NAME,
        Columns.LONGITUDE,
        Columns.LATITUDE,
    ]
    airport_ref = airport_ref[airport_ref_cols]
    
    # 출발지 공항 정보 병합
    df = pd.merge(df, airport_ref, left_on=Columns.DEPARTURE, right_on=Columns.IATA, how="left", suffixes=("", "_dep"))
    
    # 도착지 공항 정보 병합
    df = pd.merge(df, airport_ref, left_on=Columns.ARRIVAL, right_on=Columns.IATA, how="left", suffixes=("_x", "_y"))
    
    # 경로 조합 컬럼 생성
    for col in [Columns.IATA, Columns.CITY_NAME, Columns.COUNTRY_NAME, Columns.REGION_NAME, Columns.ROUTE_NAME]:
        if f"{col}_x" in df.columns and f"{col}_y" in df.columns:
            df[f"{col}_z"] = df[f"{col}_x"] + " - " + df[f"{col}_y"]
    
    # 완전한 경로 데이터만 필터링
    df = df[df[f"{Columns.REGION_NAME}_x"].notnull() & df[f"{Columns.REGION_NAME}_y"].notnull()]
    return df


def filter_by_cargo_route(df, airport_ref, airline_ref, aircraft_ref, key_prefix=""):
    df = merge_cargo_data_with_ref(df, airline_ref, airport_ref, aircraft_ref)
    
    # --- 출발노선 필터 ---
    st.sidebar.header("🛫 출발노선")
    dep_route = st.sidebar.selectbox(
        "Route",
        ROUTE_LIST,
        index=DefaultFilters.DEP_ROUTE_INDEX,
        key=f"{key_prefix}_dep",
    )
    if dep_route != "":
        df = df[df[f"{Columns.ROUTE_NAME}_x"] == dep_route]
    df = filter_by_area(df, cols=[f"{Columns.COUNTRY_NAME}_x", f"{Columns.CITY_NAME}_x"])
    
    # --- 도착노선 필터 ---
    st.sidebar.header("🛬 도착노선")
    arr_route = st.sidebar.selectbox(
        "Route",
        ROUTE_LIST,
        index=DefaultFilters.ARR_ROUTE_INDEX,
        key=f"{key_prefix}_arr",
    )
    if arr_route != "":
        df = df[df[f"{Columns.ROUTE_NAME}_y"] == arr_route]
    df = filter_by_area(df, cols=[f"{Columns.COUNTRY_NAME}_y", f"{Columns.CITY_NAME}_y"])
    
    # --- 기간 필터 ---
    df = filter_by_days(df, Columns.FLIGHT_DATE).reset_index(drop=True)
    return df


def filter_by_cargo_airline(df, airport_ref, airline_ref, aircraft_ref, key_prefix=""):
    """항공사별 화물 데이터 필터링"""
    df = merge_cargo_data_with_ref(df, airline_ref, airport_ref, aircraft_ref)
    compare_df = df.copy()
    
    # --- 항공사 국적별 필터 ---
    st.sidebar.header("🌍 항공사")
    path = [Columns.AIRLINE_COUNTRY]
    grouped_df = df.groupby(path)[Columns.TOTAL_WEIGHT].sum().sort_values(ascending=False)
    nations = [""] + list(grouped_df.index)
    nation = st.sidebar.selectbox("Nation", nations, key=f"{key_prefix}_nation")
    if nation != "":
        df = df[(df[Columns.AIRLINE_COUNTRY] == nation)]
    
    # --- 항공사별 필터 ---
    path = [Columns.AIRLINE, Columns.AIRLINE_NAME, Columns.AIRLINE_COUNTRY]
    grouped_df = df.groupby(path)[Columns.TOTAL_WEIGHT].sum().sort_values(ascending=False)
    grouped_df = grouped_df.reset_index()
    airlines = [
        f"[{index}] {name} ({code}, {nation})"
        for index, (code, name, nation) in enumerate(
            zip(
                grouped_df[Columns.AIRLINE],
                grouped_df[Columns.AIRLINE_NAME],
                grouped_df[Columns.AIRLINE_COUNTRY],
            ),
            start=1,
        )
    ]
    airline = st.sidebar.multiselect("Airline", airlines, key=f"{key_prefix}_airline")
    airline2 = [value.split("] ")[1].split(" (")[0] for value in airline]
    if len(airline2) != 0:
        df = df[df[Columns.AIRLINE_NAME].isin(airline2)]
    
    # --- 기종 타입별 필터 ---
    types = ["", "화물기", "여객기"]
    type_selected = st.sidebar.selectbox("Type", types, key=f"{key_prefix}_type")
    if type_selected != "":
        df = df[(df[Columns.PASSENGER_CARGO] == type_selected[:2])]
    
    # --- 기간 필터 ---
    df = filter_by_days(df, Columns.FLIGHT_DATE).reset_index(drop=True)
    
    # --- 전년 동기 비교 데이터 생성 ---
    last_year = (df[Columns.FLIGHT_DATE] - pd.DateOffset(years=1)).unique()
    compare_df = compare_df[compare_df[Columns.FLIGHT_DATE].isin(last_year)]
    
    return df, compare_df
