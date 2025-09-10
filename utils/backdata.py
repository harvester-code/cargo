import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from config import (
    CARGO_DATA_FILE, 
    OAG_REF_FILE, 
    Columns, 
    REGION_CODE_MAPPING
)


# --- CSS ---
def load_css():
    st.set_page_config(
        page_title="Cargo - 항공 화물 분석",
        page_icon="✈️",
        layout="wide",
        initial_sidebar_state="auto",
    )
    # Custom CSS can be added here if needed
    css = """<style></style>"""
    return st.markdown(css, unsafe_allow_html=True)


# --- Raw Data ---
@st.cache_resource
def load_cargo_data():
    df = pd.read_parquet(CARGO_DATA_FILE)
    # 날짜 형식 정리 및 변환
    df[Columns.FLIGHT_DATE] = df[Columns.FLIGHT_DATE].str.replace("-", "")
    df[Columns.FLIGHT_DATE] = pd.to_datetime(df[Columns.FLIGHT_DATE], format="%Y%m%d")
    df = df.sort_values(by=[Columns.FLIGHT_DATE, Columns.FLIGHT_NUM]).reset_index(drop=True)
    
    # 중량 데이터 처리 (kg -> 톤, 환적이므로 X2)
    df[Columns.TOTAL_WEIGHT] = df[Columns.TOTAL_WEIGHT].astype(int)
    df[Columns.TOTAL_WEIGHT] = df[Columns.TOTAL_WEIGHT] / 1000 * 2
    return df


# --- Reference Data ---
@st.cache_resource
def load_airport_ref():
    df = pd.read_excel(OAG_REF_FILE, sheet_name="Airport Code")
    df = df[
        [
            Columns.IATA,
            Columns.AIRPORT_NAME,
            Columns.CITY_NAME,
            Columns.COUNTRY_NAME,
            Columns.REGION_NAME,
            "Region Code",
            Columns.LONGITUDE,
            Columns.LATITUDE,
        ]
    ]
    df["SubRegion Name"] = df["Region Code"].map(REGION_CODE_MAPPING)
    df.drop(["Region Code"], axis=1, inplace=True)
    return df


@st.cache_resource
def load_airline_ref():
    df = pd.read_excel(OAG_REF_FILE, sheet_name="Airline Code")
    df = df[df[Columns.IATA].notnull()]
    df["Eff To"] = df["Eff To"].apply(
        lambda x: x.replace(year=x.year + 100) if x.year == 1938 else x
    )
    df = df[pd.to_datetime(df["Eff To"]) > datetime.now()]
    df = df.sort_values(by=[Columns.AIRLINE_NAME_ORIG, "Eff From"])
    df = df.drop_duplicates(subset=[Columns.AIRLINE_NAME_ORIG], keep="last")[
        [Columns.IATA, Columns.AIRLINE_NAME_ORIG, Columns.COUNTRY_NAME_ORIG]
    ].reset_index(drop=True)
    df.columns = [Columns.AIRLINE, Columns.AIRLINE_NAME, Columns.AIRLINE_COUNTRY]
    return df


@st.cache_resource
def load_aircraft_ref():
    df = pd.read_excel(OAG_REF_FILE, sheet_name="Aircraft Code")
    df = df[[Columns.IATA, "Manufacturer", "Acft Name", "Cat Name", "Class"]]
    df[Columns.IATA] = df[Columns.IATA].astype(str)
    return df
