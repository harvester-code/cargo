import streamlit as st
from config import Columns
from utils.backdata import *
from utils.sidebar import *
from utils.contents import *
from authentication import initialize_auth

# 페이지 설정
st.set_page_config(
    page_title="Cargo Route",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="auto",
)

# 인증 시스템 초기화
auth_manager = initialize_auth()

# Login check
if not auth_manager.is_logged_in():
    # Login screen
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # Render login widget
        auth_manager.render_login()
else:
    # Main application after successful login
    load_css()
    
    # Add user info and logout button in sidebar
    with st.sidebar:
        auth_manager.render_user_info()
    
    # --- Data Load ---
    cargo_df = load_cargo_data()
    airport_ref = load_airport_ref()
    airline_ref = load_airline_ref()
    aircraft_ref = load_aircraft_ref()

    # --------------------- SideBar Start ---------------------
    cargo_df = filter_by_cargo_route(cargo_df, airport_ref, airline_ref, aircraft_ref, key_prefix="main")
    # --------------------- SideBar End ---------------------

    # --------------------- Contents Start ---------------------
    st.subheader(f"👨🏽 Summary")
    text = f"""
            * [기간] {cargo_df[Columns.FLIGHT_DATE].dt.date.min()} ~ {cargo_df[Columns.FLIGHT_DATE].dt.date.max()}
            * [운항편수] {len(cargo_df[[Columns.FLIGHT_DATE, Columns.FLIGHT_NUM]].drop_duplicates()):,}편
            * [총 환적중량] {cargo_df[Columns.TOTAL_WEIGHT].sum():,.0f} 톤
            """
    st.write_stream(stream_data(text))
    # --------------------- Contents End ---------------------

    # --------------------- Contents Start ---------------------
    fig = make_cargo_route_pie_chart(cargo_df, airport_ref)
    if fig != None:
        st.plotly_chart(fig, width='stretch')
    # --------------------- Contents End ---------------------

    # --------------------- Contents Start ---------------------
    st.caption(f" * 인터넷 접속이 제한되어 배경지도가 나타나지 않을 수 있습니다.")
    tab1, tab2 = st.tabs(["출발도시", "도착도시"])
    with tab1:
        fig = make_cargo_mapbox(cargo_df, airport_ref, io="전")
        st.plotly_chart(fig, width='stretch')
    with tab2:
        fig = make_cargo_mapbox(cargo_df, airport_ref, io="후")
        st.plotly_chart(fig, width='stretch')
    # --------------------- Contents End ---------------------

    # --------------------- Contents Start ---------------------
    st.subheader(f"🛫 점유율 분석")
    fig = make_cargo_treemap(cargo_df)
    if fig != None:
        st.plotly_chart(fig, width='stretch')
    # --------------------- Contents End ---------------------