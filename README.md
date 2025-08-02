연구 동향을 분석하는 MCP(Model Context Protocol) 서버입니다.

*주요 기능*

연도별 키워드 트렌드 분석: 1999-2025년간 키워드별 연구 동향 시각화
연구 분야별 분포 분석: Web of Science 카테고리별 연구 현황 파악
종합 트렌드 분석: 연도별 + 분야별 통합 인사이트 제공
자동 그래프 생성: PNG 형태의 시각화 차트 자동 생성
실시간 데이터 처리: 1000편의 연구논문 데이터 실시간 분석

**설치 및 설정**
필요 조건
1. Python 3.12 이상 (최근 버전)
2. Claude Desktop 또는 MCP와 호환되는 클라이언트
3. CSV 파일

설치하기
1. 레포지터리 클론
git clone https://github.com/yeobaek-blank/LAB1_WOS_Trend_Mini.git
cd LAB1_WOS_Trend_Mini
2. 의존성 설치
pip install -r requirements.txt
3. 데이터파일 준비
cp your_research_data.csv ./통합문서1.csv

Claude Desktop 설정 
claude_desktop_config.json 파일을 찾아서 수정합니다. 이전에 등록된 서버가 있다면 같이 실행될 수 있도록 수정합니다.
{
  "mcpServers": {
    "research-trend-analyzer": {
      "command": "python",
      "args": ["path/to/LAB1_WOS_Trend_Mini/server.py"],
      "env": {}
    }
  }
}

**사용법**
1. 연도별 키워드 분석
ex) "Korea" 키워드의 연도별 연구 동향을 분석해줘
출력 예시:
총 논문 수: 1000편
연구 기간: 1999-2025
최고 연구년도: 2021년 (72편)
그래프 파일: Korea_yearly_trend.png

2. 연구 분야별 분석
ex) "North Korea" 키워드의 연구 분야별 분포를 보여줘
출력 예시:
상위 분야: International Relations (207편)
총 연구 분야: 108개
그래프 파일: North_Korea_categories.png

3. 종합 분석
ex) "Korean" 키워드에 대한 종합적인 분석을 해줘
출력 예시:
연도별 + 분야별 통합 분석
상세 통계 및 인사이트
2개의 그래프 파일 생성

4. 데이터셋 정보 확인
ex)연구 데이터셋의 기본 정보를 알려줘

6. 서버 상태 확인
ex) 서버 상태를 확인해줘

사용 가능한 함수 목록
1. yearly_keyword_analysis   : 키워드의 연도별 출현 빈도를 분석합니다.
2. category_research_analysis   : 키워드를 WoW Categories 컬럼에서 분야별로 분석 해 줍니다.
3. comprehensive_research_analysis   : 연도 + 분야별 종합 분석을 실행합니다. 
4. get_research_dataset_info   : 연구 데이터셋의 기본 정보를 제공합니다.
5. server_health_check  : 서버의 상태와 기능을 확인합니다.

**문서 구조**
LAB1_WOS_Trend_Mini/  
├── README.md                    # 프로젝트 문서  
├── server.py                    # MCP 서버 메인 파일  
├── requirements.txt             # Python 의존성  
├── 통합문서1.csv               # 연구 데이터 (1000편)  
├── research_graphs/             # 생성된 그래프 저장 폴더  
│   ├── Korea_yearly_trend.png  
│   ├── Korea_categories.png  
│   └── ...  
├── src/                        # 소스 코드 폴더  
│   ├── analysis/               # 분석 모듈  
│   ├── visualization/          # 시각화 모듈  
│   └── utils/                  # 유틸리티 함수  
└── docs/                       # 추가 문서  

**CSV파일 데이터셋 정보**
총 논문 수: 1,000편  
연구 기간: 1999-2025년 (26년간)  
데이터 출처: Web of Science  
주요 분야: 국제관계, 지역연구, 아시아연구  
언어: 주로 영어 논문  
지역: 한국 관련 연구 중심  

**CSV 파일 컬럼 정보**
Publication Type, Authors, Article Title
Source Title, Publication Year, Abstract
WoS Categories, Research Areas
Keywords Plus, Author Keywords
Times Cited, DOI 등 총 72개 필드 (결측치, 공백 있음)
