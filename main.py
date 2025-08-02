from mcp.server.fastmcp import FastMCP
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # GUI 없는 백엔드 사용
import os
import sys
from collections import Counter

# 한글 폰트 설정
try:
    plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans', 'sans-serif']
except:
    plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 새로운 MCP 서버 생성 (기존과 다른 이름)
mcp = FastMCP("Research_Trend_Analyzer")

# 파일 경로 설정
CSV_PATH = os.path.join(os.path.dirname(__file__), "통합문서1.csv")
GRAPH_FOLDER = os.path.join(os.path.dirname(__file__), "research_graphs")
os.makedirs(GRAPH_FOLDER, exist_ok=True)

def load_csv_data():
    """CSV 데이터를 안전하게 로드합니다."""
    try:
        encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr']
        for encoding in encodings:
            try:
                return pd.read_csv(CSV_PATH, encoding=encoding)
            except UnicodeDecodeError:
                continue
        raise Exception("모든 인코딩 시도 실패")
    except Exception as e:
        raise Exception(f"CSV 파일 로드 실패: {str(e)}")

@mcp.tool()
def yearly_keyword_analysis(params):
    """키워드의 연도별 출현 빈도를 분석하고 그래프를 생성합니다."""
    keyword = params.get("keyword", "").strip()
    if not keyword:
        return {"error": "키워드를 입력해주세요."}
    
    try:
        df = load_csv_data()
        
        # Author Keywords 컬럼 확인
        if 'Author Keywords' not in df.columns:
            return {"error": "Author Keywords 컬럼이 존재하지 않습니다."}
        
        if 'Publication Year' not in df.columns:
            return {"error": "Publication Year 컬럼이 존재하지 않습니다."}
        
        # 키워드 검색 (대소문자 구분 없음)
        mask = df['Author Keywords'].astype(str).str.lower().str.contains(keyword.lower(), na=False)
        filtered_data = df[mask]
        
        if filtered_data.empty:
            return {
                "keyword": keyword,
                "message": f"'{keyword}' 키워드를 포함한 논문이 없습니다.",
                "total_papers": 0
            }
        
        # 연도별 집계
        yearly_counts = filtered_data['Publication Year'].value_counts().sort_index()
        
        # 그래프 생성
        plt.figure(figsize=(12, 7))
        bars = plt.bar(yearly_counts.index, yearly_counts.values, 
                      color='steelblue', edgecolor='black', alpha=0.7)
        
        plt.title(f"'{keyword}' 키워드 연도별 논문 출현 횟수", fontsize=16, pad=20)
        plt.xlabel('연도', fontsize=14)
        plt.ylabel('논문 수', fontsize=14)
        plt.grid(True, alpha=0.3)
        
        # 막대 위에 숫자 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # 파일 저장
        safe_keyword = "".join(c for c in keyword if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_keyword = safe_keyword.replace(' ', '_')
        graph_path = os.path.join(GRAPH_FOLDER, f"{safe_keyword}_yearly_trend.png")
        plt.savefig(graph_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 통계 정보 계산
        peak_year = yearly_counts.idxmax()
        peak_count = yearly_counts.max()
        total_papers = len(filtered_data)
        year_range = f"{yearly_counts.index.min()}-{yearly_counts.index.max()}"
        
        return {
            "keyword": keyword,
            "analysis_type": "연도별 출현 빈도",
            "total_papers": total_papers,
            "year_range": year_range,
            "peak_year": int(peak_year),
            "peak_count": int(peak_count),
            "yearly_data": {int(year): int(count) for year, count in yearly_counts.items()},
            "graph_saved_to": graph_path,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": f"연도별 분석 중 오류: {str(e)}"}

@mcp.tool()
def category_research_analysis(params):
    """키워드를 WoS Categories별로 분석하여 어떤 분야에서 연구가 활발한지 시각화합니다."""
    keyword = params.get("keyword", "").strip()
    if not keyword:
        return {"error": "키워드를 입력해주세요."}
    
    try:
        df = load_csv_data()
        
        # 필수 컬럼 확인
        required_columns = ['Author Keywords', 'WoS Categories']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return {"error": f"필요한 컬럼이 없습니다: {missing_columns}"}
        
        # 키워드 필터링
        mask = df['Author Keywords'].astype(str).str.lower().str.contains(keyword.lower(), na=False)
        filtered_data = df[mask]
        
        if filtered_data.empty:
            return {
                "keyword": keyword,
                "message": f"'{keyword}' 키워드를 포함한 논문이 없습니다.",
                "total_papers": 0
            }
        
        # WoS Categories 분석 (세미콜론으로 분리된 카테고리들 처리)
        all_categories = []
        for categories_str in filtered_data['WoS Categories'].dropna():
            if pd.notna(categories_str):
                categories = [cat.strip() for cat in str(categories_str).split(';') if cat.strip()]
                all_categories.extend(categories)
        
        if not all_categories:
            return {"error": "WoS Categories 데이터가 없습니다."}
        
        # 카테고리별 빈도 계산
        category_counter = Counter(all_categories)
        top_15_categories = dict(category_counter.most_common(15))
        
        # 그래프 생성
        plt.figure(figsize=(16, 10))
        categories = list(top_15_categories.keys())
        counts = list(top_15_categories.values())
        
        # 긴 카테고리 이름 줄바꿈 처리
        wrapped_categories = []
        for cat in categories:
            if len(cat) > 25:
                words = cat.split()
                if len(words) > 3:
                    mid = len(words) // 2
                    wrapped = ' '.join(words[:mid]) + '\n' + ' '.join(words[mid:])
                else:
                    wrapped = cat
            else:
                wrapped = cat
            wrapped_categories.append(wrapped)
        
        bars = plt.bar(range(len(categories)), counts, 
                      color='lightcoral', edgecolor='black', alpha=0.8)
        
        plt.title(f"'{keyword}' 키워드 관련 연구 분야 분포 (WoS Categories 상위 15개)", 
                 fontsize=16, pad=20)
        plt.xlabel('연구 분야 (WoS Categories)', fontsize=14)
        plt.ylabel('논문 수', fontsize=14)
        plt.xticks(range(len(categories)), wrapped_categories, rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        # 막대 위에 숫자 표시
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(count), ha='center', va='bottom', fontsize=11, weight='bold')
        
        plt.tight_layout()
        
        # 파일 저장
        safe_keyword = "".join(c for c in keyword if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_keyword = safe_keyword.replace(' ', '_')
        graph_path = os.path.join(GRAPH_FOLDER, f"{safe_keyword}_categories.png")
        plt.savefig(graph_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 가장 활발한 연구 분야
        most_active_field = max(top_15_categories.keys(), key=lambda k: top_15_categories[k])
        most_active_count = top_15_categories[most_active_field]
        
        return {
            "keyword": keyword,
            "analysis_type": "연구 분야별 분포",
            "total_papers": len(filtered_data),
            "total_unique_categories": len(category_counter),
            "most_active_field": most_active_field,
            "most_active_count": most_active_count,
            "top_15_categories": top_15_categories,
            "all_categories_count": dict(category_counter),
            "graph_saved_to": graph_path,
            "status": "success"
        }
        
    except Exception as e:
        return {"error": f"카테고리 분석 중 오류: {str(e)}"}

@mcp.tool()
def comprehensive_research_analysis(params):
    """키워드에 대한 연도별 + 카테고리별 종합 분석을 수행합니다."""
    keyword = params.get("keyword", "").strip()
    if not keyword:
        return {"error": "키워드를 입력해주세요."}
    
    try:
        # 연도별 분석
        yearly_result = yearly_keyword_analysis({"keyword": keyword})
        
        # 카테고리별 분석  
        category_result = category_research_analysis({"keyword": keyword})
        
        # 에러가 있으면 해당 에러 반환
        if "error" in yearly_result:
            return yearly_result
        if "error" in category_result:
            return category_result
        
        # 종합 결과
        comprehensive_summary = {
            "keyword": keyword,
            "analysis_type": "종합 분석 (연도별 + 분야별)",
            "overview": {
                "total_papers": yearly_result.get("total_papers", 0),
                "research_period": yearly_result.get("year_range", ""),
                "peak_research_year": yearly_result.get("peak_year", ""),
                "peak_year_papers": yearly_result.get("peak_count", 0),
                "most_active_research_field": category_result.get("most_active_field", ""),
                "most_active_field_papers": category_result.get("most_active_count", 0),
                "total_research_fields": category_result.get("total_unique_categories", 0)
            },
            "detailed_results": {
                "yearly_analysis": yearly_result,
                "category_analysis": category_result
            },
            "status": "success"
        }
        
        return comprehensive_summary
        
    except Exception as e:
        return {"error": f"종합 분석 중 오류: {str(e)}"}

@mcp.tool()
def get_research_dataset_info(params):
    """연구 데이터셋의 기본 정보를 제공합니다."""
    try:
        df = load_csv_data()
        
        # 기본 통계
        info = {
            "dataset_info": {
                "total_papers": len(df),
                "total_columns": len(df.columns),
                "columns_list": list(df.columns)
            },
            "year_info": {},
            "keyword_info": {},
            "category_info": {},
            "file_paths": {
                "csv_file": CSV_PATH,
                "graphs_folder": GRAPH_FOLDER
            }
        }
        
        # 연도 정보
        if 'Publication Year' in df.columns:
            years = df['Publication Year'].dropna()
            info["year_info"] = {
                "year_range": f"{int(years.min())}-{int(years.max())}",
                "total_years": len(years.unique()),
                "most_productive_year": int(years.mode().iloc[0]) if not years.empty else None
            }
        
        # 키워드 정보
        if 'Author Keywords' in df.columns:
            keywords = df['Author Keywords'].dropna()
            info["keyword_info"] = {
                "papers_with_keywords": len(keywords),
                "sample_keywords": keywords.head(5).tolist()
            }
        
        # 카테고리 정보
        if 'WoS Categories' in df.columns:
            categories = df['WoS Categories'].dropna()
            all_cats = []
            for cat_str in categories:
                if pd.notna(cat_str):
                    all_cats.extend([c.strip() for c in str(cat_str).split(';') if c.strip()])
            
            if all_cats:
                cat_counter = Counter(all_cats)
                info["category_info"] = {
                    "total_unique_categories": len(cat_counter),
                    "most_common_categories": dict(cat_counter.most_common(5))
                }
        
        return info
        
    except Exception as e:
        return {"error": f"데이터셋 정보 조회 실패: {str(e)}"}

@mcp.tool()
def server_health_check(params):
    """서버 상태와 기능을 확인합니다."""
    try:
        # 파일 존재 여부 확인
        csv_exists = os.path.exists(CSV_PATH)
        folder_exists = os.path.exists(GRAPH_FOLDER)
        
        status_info = {
            "server_status": "healthy",
            "server_name": "Research_Trend_Analyzer", 
            "file_status": {
                "csv_file_exists": csv_exists,
                "csv_file_path": CSV_PATH,
                "graphs_folder_exists": folder_exists,
                "graphs_folder_path": GRAPH_FOLDER
            },
            "available_tools": [
                "yearly_keyword_analysis - 키워드 연도별 분석",
                "category_research_analysis - 키워드 분야별 분석", 
                "comprehensive_research_analysis - 종합 분석",
                "get_research_dataset_info - 데이터셋 정보",
                "server_health_check - 서버 상태 확인"
            ]
        }
        
        # CSV 파일이 있으면 데이터 로드 테스트
        if csv_exists:
            try:
                df = load_csv_data()
                status_info["data_status"] = {
                    "data_loaded": True,
                    "total_records": len(df),
                    "sample_loaded": True
                }
            except Exception as e:
                status_info["data_status"] = {
                    "data_loaded": False,
                    "error": str(e)
                }
        else:
            status_info["data_status"] = {
                "data_loaded": False,
                "error": "CSV 파일이 존재하지 않습니다"
            }
        
        return status_info
        
    except Exception as e:
        return {
            "server_status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    print("연구 동향 분석 MCP 서버를 시작합니다...", file=sys.stderr)
    print("서버명: Research_Trend_Analyzer", file=sys.stderr)
    print("사용 가능한 도구들:", file=sys.stderr)
    print("1. yearly_keyword_analysis - 키워드 연도별 출현 분석", file=sys.stderr)
    print("2. category_research_analysis - 키워드 분야별 연구 분석", file=sys.stderr) 
    print("3. comprehensive_research_analysis - 종합 분석", file=sys.stderr)
    print("4. get_research_dataset_info - 데이터셋 정보", file=sys.stderr)
    print("5. server_health_check - 서버 상태 확인", file=sys.stderr)
    print("", file=sys.stderr)
    
    mcp.run(transport="stdio")