# 🚢 Cargo - 항공 화물 데이터 분석 대시보드

항공 화물 환적 데이터를 분석하고 시각화하는 Streamlit 웹 애플리케이션입니다.

## 🔧 개발 환경 설정

```bash
uv init                    # pyproject.toml 등 생성
uv venv                    # .venv 생성
uv add streamlit          # 라이브러리 추가
uv run streamlit run Route.py --server.port=8800  # 앱 실행
```

## 🚀 Synology NAS 배포

```bash
# Docker 컨테이너 빌드 및 실행
docker-compose up -d

# 접속 URL: http://[NAS-IP]:8800
```

## 📊 주요 기능

- **노선별 분석**: 출발/도착지별 화물량 분석 및 지도 시각화
- **항공사별 분석**: 점유율, 기종별 사용 현황, 전년 대비 분석
- **인터랙티브 필터**: 기간, 지역, 항공사, 기종 등 다양한 필터
- **시각화**: 선버스트 차트, 트리맵, 지도, 바차트 등
