# 와인 관련 Instagram 분석

### 목적

- 와인 관련 인스타그램 계정 데이터 분석 및 대시보드 작성

### 배포

[<h3 style="text-decoration:none;" target="_blank">바로가기</h3>](https://wba9-insta.streamlitapp.com/)

- 스크린샷
    
    [<img src= "img/1.png?raw=true"  width = "800">]()
    
    [<img src= "img/2.png?raw=true" width = "800">]()
    
    [<img src= "img/3.png?raw=true" width = "800">]()
    
    [<img src= "img/4.png?raw=true" width = "800">]()
    

### 데이터 수집 및 자동화

- Instagram Graph API 활용 - business 계정 정보 및 media 정보 수집
    - 파이썬 코드 참조
        
        [https://github.com/imakashsahu/Instagram-Graph-API-Python](https://github.com/imakashsahu/Instagram-Graph-API-Python)
        
- 자동화 - Github Actions
    - 매일 아침 9시 API로 데이터를 불러와 db에 저장하는 코드 실행
        
        ```yaml
        name: fetchInstagramData
        
        on:
          schedule:
            - cron: '00 00 * * *'
        
        jobs:
          build:
            runs-on: ubuntu-latest
            steps:
            - uses: actions/checkout@v2
              with:
                # 개인 토큰을 사용할 것인지 말 것인지
                persist-credentials: false 
            - name: 1. pip 업그래이드
              run: python -m pip install --upgrade pip
            - name: 2. 환경 설정
              run: pip install -r requirements.txt
            - name: 3. 데이터 불러오기 실행
              env: 
                ACCESS_KEY: ${{ secrets.ACCESS_KEY }}
                CLIENT_ID: ${{ secrets.CLIENT_ID }}
                CLIENT_SECRET: ${{ secrets.CLIENT_SECRET }}
                PAGE_ID: ${{ secrets.PAGE_ID }}
                INSTAGRAM_ACCOUNT_ID: ${{ secrets.INSTAGRAM_ACCOUNT_ID }}
                USER: ${{ secrets.USER }}
                PW: ${{ secrets.PW }}
                HOST: ${{ secrets.HOST }}
                DB_NAME: ${{ secrets.DB_NAME }}
        
              run:  
                python backend/fetch_data/business_discovery.py
                python backend/fetch_data/media_discovery.py
                python backend/get_summary.py
        ```
        

### DB 구축

- Google Cloud Platform 상에 MySQL 서버 구축
    
    [<img src= "img/8.png?raw=true" width = "800">]()
    

### 데이터 분석

- 지표 설정
    1. 기본 수치
       
        1) 순위 rank
        집계하는 전체 계정의 일간 팔로워 수 내림차순
        2) 팔로워 followers count
        해당 계정을 팔로우 하는 계정 수
        3) 팔로우 follows count
        해당 계정이 팔로우 하는 계정 수
        4) 게시물 수 media count
        해당 계정의 게시물 수
         8) 좋아요 수 like count
        게시물에 달린 좋아요 수 합계
        6) 댓글 수 comments count
        게시물에 달린 댓글 수 합계
        7) 참여 engagement
        좋아요 수와 댓글 수의 합계
        
    2. 복합 수치
        
        1) 증감(수) change in count
        기준일 대비 수치 변화량
        2) 증감(%) change in percentage
        기준일 대비 수치 변화량의 백분율(800 * 증감(수) / 기준일 수치)
        3) 참여도 engagement rate
        팔로워 수 대비 참여 백분율(800 * 참여 / 팔로워 수)
        4) 게시물 당 OO OO-media count ratio
        게시물 하나 당 OO 수(OO 수 / 게시물 수)
        
- 수치 계산을 위한 객체 생성
    
    ```python
    class Summary():
        def __init__(self, df):
            self.df = df
            self.df['rank'] = self.df.groupby(['date'])['followers_count'].rank(ascending = False).astype(int)
            self.df_summary = {'diff' : dict(), 'pct_change' : dict()}
            self._calc_engage_rate()
            for a, b in [('like', 'media'), ('comments', 'media')]:
                self.df = Summary.calc_ab_ratio(self.df, a, b)
                
    
        def get_summaries(self, summary_func:iter = ['diff'], periods:iter = [1], fillna = False):
            df_summaries = self.df.copy()
            for s in summary_func:
                for p in periods:
                    self._summarize(summary_func = s, periods = p)
                    df_summaries = df_summaries.join(self.df_summary[s][p])
            return df_summaries    
    
        def _summarize(self, summary_func = 'diff', periods=1, fillna = False):
            if periods in self.df_summary[summary_func].keys():
                return    
            if summary_func == 'diff':
                defined_func = lambda x: x.diff(periods)
            elif summary_func == 'pct_change':
                defined_func = lambda x: x.pct_change(periods) * 800
            df_summary = self.df.groupby('name')[[c for c in self.df.columns if ('count' in c) or ('ratio' in c) or (c == 'rank') or ('rate' in c)]].transform(defined_func)
            df_summary.columns = [c.split('_count')[0] + f'_{summary_func}' for c in df_summary.columns]
            if 'rank_diff' in df_summary.columns:
                df_summary.loc[df_summary['rank_diff'] != 0, 'rank_diff'] *= -1
            if fillna:
                df_summary = df_summary.fillna(0)
            self.df_summary[summary_func][periods] = df_summary
        
        def _calc_engage_rate(self):
            self.df['engagementrate'] = 800 * (self.df['like_count'] + self.df['comments_count']) / self.df['followers_count']
        
        @staticmethod
        def calc_ab_ratio(df, a, b):
            df[f'{a}_{b}_ratio'] = df[f'{a}_count'] / df[f'{b}_count']
            return df
    ```
    

### 시각화

- streamlit 자체 함수를 활용한 수치 표현
    
    [<img src= "img/6.png?raw=true" width = "800">]()
    
- plotly를 활용한 그래프 시각화
    
    [<img src= "img/7.png?raw=true" width = "800">]()
        
    [<img src= "img/8.png?raw=true" width = "800">]()