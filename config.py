# Configuration file for cargo analysis
from pathlib import Path
import os

# File paths - NAS 환경변수 우선, 로컬 fallback
DATA_DIR = Path(os.getenv("DATA_DIR", "/Volumes/teamflexa.synology.me/data"))
CARGO_DATA_FILE = DATA_DIR / "fois-cargo" / "cargo_transfer.parquet"
OAG_REF_FILE = DATA_DIR / "oag_ref.xlsx"

# Column names
class Columns:
    # 화물 데이터
    FLIGHT_DATE = "운항일자"
    FLIGHT_NUM = "편명"
    TOTAL_WEIGHT = "총중량"
    DEPARTURE = "전"
    ARRIVAL = "후"
    AIRLINE = "항공사"
    AIRCRAFT_TYPE = "서브기종"
    PASSENGER_CARGO = "여객/화물"
    
    # 공항 참조 데이터 (원본)
    IATA = "IATA"
    AIRPORT_NAME = "Airport Name"
    CITY_NAME = "City Name"
    COUNTRY_NAME = "Country Name"
    REGION_NAME = "Region Name"
    ROUTE_NAME = "Route Name"
    LONGITUDE = "Longitude"
    LATITUDE = "Latitude"
    
    # 항공사 참조 데이터 (원본)
    AIRLINE_NAME_ORIG = "Airline Name"  # 원본 Excel 컬럼명
    COUNTRY_NAME_ORIG = "Country Name"  # 원본 Excel 컬럼명
    
    # 항공사 참조 데이터 (변환 후)
    AIRLINE_NAME = "항공사명"
    AIRLINE_COUNTRY = "항공사국적"

# Route mapping
ROUTE_MAPPING = {
    "Japan": "일본",
    "China": "중국",
    "South East Asia": "동남아",
    "North East Asia": "동북아",
    "North America": "미주",
    "Europe": "유럽",
    "Middle East": "중동",
    "Southwest Pacific": "대양주",
}

# Region code mapping
REGION_CODE_MAPPING = {
    "AF1": "North Africa",
    "AF2": "Southern Africa", 
    "AF3": "Central/Western Africa",
    "AF4": "Eastern Africa",
    "EU1": "Western Europe",
    "EU2": "Eastern/Central Europe",
    "AS1": "South Asia",
    "AS2": "Central Asia",
    "AS3": "South East Asia",
    "AS4": "North East Asia",
    "LA1": "Caribbean",
    "LA2": "Central America",
    "LA3": "Upper South America",
    "LA4": "Lower South America",
    "NA1": "North America",
    "ME1": "Middle East",
    "SW1": "Southwest Pacific",
}

# Route filter options
ROUTE_LIST = [
    "",
    "일본",
    "중국", 
    "동남아",
    "동북아",
    "미주",
    "유럽",
    "중동",
    "대양주",
    "기타",
]

# Chart settings
class ChartConfig:
    MAPBOX_STYLE = "carto-darkmatter"
    COLOR_SCALE = "Pinkyl"
    PIE_CHART_HEIGHT = 700
    MAP_HEIGHT = 400
    TREEMAP_HEIGHT = 600
    DEFAULT_ZOOM = 2
    
# Default filter settings
class DefaultFilters:
    DEP_ROUTE_INDEX = 3  # 동남아
    ARR_ROUTE_INDEX = 5  # 미주
    PIE_CHART_DEFAULTS = ["출발지역", "출발국가", "도착국가"]
    TREEMAP_DEFAULTS = ["여객/화물", "항공사명"]
