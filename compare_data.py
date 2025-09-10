import pandas as pd
import numpy as np

print("🔍 화물 데이터 비교 분석")
print("=" * 50)

# 1. 첫 번째 파일 로드 (flexa 원본)
print("📦 첫 번째 파일: flexa/data/icn/cargo/cargo_transfer2.snappy")
try:
    df1 = pd.read_parquet("../flexa/data/icn/cargo/cargo_transfer2.snappy")
    print(f"✅ 로딩 성공")
    print(f"   - 행 수: {len(df1):,}")
    print(f"   - 열 수: {len(df1.columns)}")
    print(f"   - 파일 크기: ~3.5MB")
except Exception as e:
    print(f"❌ 로딩 실패: {e}")
    df1 = None

print()

# 2. 두 번째 파일 로드 (cargo 프로젝트)  
print("📦 두 번째 파일: cargo/cargo/cargo_transfer.parquet")
try:
    df2 = pd.read_parquet("cargo/cargo_transfer.parquet")
    print(f"✅ 로딩 성공")
    print(f"   - 행 수: {len(df2):,}")
    print(f"   - 열 수: {len(df2.columns)}")  
    print(f"   - 파일 크기: ~2.9MB")
except Exception as e:
    print(f"❌ 로딩 실패: {e}")
    df2 = None

print()

if df1 is not None and df2 is not None:
    print("📊 상세 비교 분석")
    print("=" * 50)
    
    # 3. 열 이름 비교
    print("🏷️  열 이름 비교:")
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    
    if cols1 == cols2:
        print("   ✅ 열 이름이 동일합니다")
        print(f"   📋 공통 열: {len(cols1)}개")
    else:
        print("   ⚠️  열 이름이 다릅니다")
        print(f"   📋 첫 번째만: {cols1 - cols2}")
        print(f"   📋 두 번째만: {cols2 - cols1}")
        print(f"   📋 공통 열: {len(cols1 & cols2)}개")
    
    print(f"   🔤 열 이름 목록 (첫 번째): {list(df1.columns)}")
    print()
    
    # 4. 날짜 범위 비교 (운항일자 열이 있다면)
    date_cols = ['운항일자', 'date', 'Date', '날짜']
    date_col = None
    
    for col in date_cols:
        if col in df1.columns and col in df2.columns:
            date_col = col
            break
    
    if date_col:
        print(f"📅 날짜 범위 비교 ({date_col}):")
        try:
            # 날짜 형식 변환
            df1_date = pd.to_datetime(df1[date_col])
            df2_date = pd.to_datetime(df2[date_col]) 
            
            print(f"   📦 첫 번째: {df1_date.min().date()} ~ {df1_date.max().date()}")
            print(f"   📦 두 번째: {df2_date.min().date()} ~ {df2_date.max().date()}")
            
            # 중복 날짜 확인
            dates1 = set(df1_date.dt.date)
            dates2 = set(df2_date.dt.date)
            common_dates = dates1 & dates2
            
            print(f"   🔄 공통 날짜: {len(common_dates)}일")
            print(f"   ➕ 첫 번째만: {len(dates1 - dates2)}일")
            print(f"   ➕ 두 번째만: {len(dates2 - dates1)}일")
            
        except Exception as e:
            print(f"   ❌ 날짜 비교 실패: {e}")
    
    print()
    
    # 5. 데이터 타입 비교
    print("🔢 데이터 타입 비교:")
    common_cols = list(cols1 & cols2)
    
    for col in common_cols[:5]:  # 처음 5개 열만 표시
        type1 = str(df1[col].dtype)
        type2 = str(df2[col].dtype)
        status = "✅" if type1 == type2 else "⚠️"
        print(f"   {status} {col}: {type1} vs {type2}")
    
    if len(common_cols) > 5:
        print(f"   ... 및 {len(common_cols)-5}개 추가 열")
    
    print()
    
    # 6. 샘플 데이터 미리보기
    print("👀 샘플 데이터 미리보기:")
    print("📦 첫 번째 파일 (처음 3행):")
    print(df1.head(3))
    print()
    print("📦 두 번째 파일 (처음 3행):")  
    print(df2.head(3))
    
    # 7. 기본 통계
    print()
    print("📈 기본 통계 비교:")
    
    # 숫자형 열들의 기본 통계
    numeric_cols = df1.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        col = numeric_cols[0]  # 첫 번째 숫자형 열
        if col in df2.columns:
            print(f"   📊 {col} 열 통계:")
            print(f"      📦 첫 번째 - 평균: {df1[col].mean():.2f}, 합계: {df1[col].sum():.0f}")
            print(f"      📦 두 번째 - 평균: {df2[col].mean():.2f}, 합계: {df2[col].sum():.0f}")

else:
    print("❌ 두 파일을 모두 로딩할 수 없어서 비교를 진행할 수 없습니다.")

print()
print("🏁 비교 분석 완료!")
