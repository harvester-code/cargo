import streamlit as st

from config import Columns
from utils.backdata import *
from utils.sidebar import *
from utils.contents import *
from authentication import initialize_auth

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
    compare_df = cargo_df.copy()
    airport_ref = load_airport_ref()
    airline_ref = load_airline_ref()
    aircraft_ref = load_aircraft_ref()

    # --------------------- SideBar Start ---------------------
    cargo_df, compare_df = filter_by_cargo_airline(
        cargo_df, airport_ref, airline_ref, aircraft_ref
    )
    # --------------------- SideBar End ---------------------

    # --------------------- Contents Start ---------------------
    make_cargo_airline_stream_text(cargo_df)
    st.markdown("---")
    # --------------------- Contents End ---------------------

    # --------------------- Contents Start ---------------------
    st.caption(f"주요 사용 기재")
    fig = make_cargo_airline_treemap(cargo_df)
    st.plotly_chart(fig, use_container_width=True)
    # --------------------- Contents End ---------------------

    # --------------------- Contents Start ---------------------
    for col in [f"{Columns.ROUTE_NAME}_z", f"{Columns.COUNTRY_NAME}_z", f"{Columns.CITY_NAME}_z"]:
        fig, rank_df = make_cargo_airline_ranking_bar(cargo_df, compare_df, col)
        st.caption(f"Top 20 순위 ({col.split('_')[0]} 기준)")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f" * (참고) 전체 데이터")
        st.dataframe(rank_df, use_container_width=True)
    # --------------------- Contents End ---------------------
