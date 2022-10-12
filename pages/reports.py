import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from modules.stats import Summary
from modules.text import st_header, translate, date_format
from datetime import datetime, timedelta
import os

pio.templates.default = "simple_white"

# 그니까
# 1. 팔로워 수 / 참여도 증가가 가장 큰 업체
# 2. -> 어떤 게시물이 터졌는지(참여도 증감) -> 행사/이벤트, 특정 게시물 타입?
# 3. 게시물 내용 분석(게시물 카테고리 분류 / 미디어 타입 / 해시태그)
# https://blog.hootsuite.com/calculate-engagement-rate/
# 4. 업체 동향 (게시물 게시 속도, 늘고 있는지? / 활동 없는지)


def main():
    st.set_page_config(layout='centered')
    our_business = 'winebook_official'
    report_start = pd.to_datetime('2022-10-10 12:00')
    current_time = pd.to_datetime(datetime.now())

    report_period = pd.date_range(start = report_start, end = current_time, freq = '7D')

    report_date = st.selectbox(label = '기준일', options = report_period[::-1], format_func = date_format)
    
    REPORT_DATA_BASE = 'data/report'
    w_summary_data_path = f"weekly_summary_{date_format(report_date, format = '')}.csv"
    w_media_data_path = f"weekly_media_{date_format(report_date, format = '')}.csv"
    
    if os.path.exists(os.path.join(REPORT_DATA_BASE, w_summary_data_path)):
        df_weekly_summary = pd.read_csv(os.path.join(REPORT_DATA_BASE, w_summary_data_path))
        df_weekly_summary['날짜'] = pd.to_datetime(df_weekly_summary['날짜'])    
    else: 
        df_daily_summary = pd.read_csv('data/df_daily_summary.csv')
        df_daily_summary['date'] = pd.to_datetime(df_daily_summary['date'])
        summarizer = Summary(df_daily_summary.sort_values('date'))
        df_weekly_summary = summarizer.get_summaries(summary_func=['diff', 'pct_change'], periods = [7])
        df_weekly_summary.columns = translate(df_weekly_summary.columns)
        df_weekly_summary.to_csv(os.path.join(REPORT_DATA_BASE, w_summary_data_path), index = False)
    if os.path.exists(os.path.join(REPORT_DATA_BASE, w_media_data_path)):
        weekly_media = pd.read_csv(os.path.join(REPORT_DATA_BASE, w_media_data_path))
        weekly_media['timestamp'] = pd.to_datetime(weekly_media['timestamp']) 
        weekly_media['date'] = pd.to_datetime(weekly_media['date']) 
    else:
        media = pd.read_csv("data/updated_media.csv")
        last_report_date = pd.to_datetime(report_date - timedelta(days = 7))
        weekly_media = media.copy().loc[media['timestamp'].between(date_format(last_report_date, format = '-'), date_format(report_date, format = '-')) & (media['name'] == 'winebook_official')]
        weekly_media['engagement'] = weekly_media['like_count'] + weekly_media['like_count']
        weekly_media.to_csv(os.path.join(REPORT_DATA_BASE, w_media_data_path), index = False)
    
    
    df_plot_weekly = df_weekly_summary[df_weekly_summary['날짜'].dt.dayofweek == report_date.dayofweek]
    df_plot_weekly['날짜'] = date_format(df_plot_weekly['날짜'])

    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st_header(our_business, num = 2)
        st_header(f'{date_format(report_date)}자 주간 보고서', num = 3)

    with col2:
        
        url = df_weekly_summary.sort_values('날짜', ascending = False).loc[df_weekly_summary['이름'] == our_business, 'profile picture url'].unique()[0]
        st.image(url)
        
    with st.container():
        st_header('1. 팔로워 수', num = 5)
    
        largest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nlargest(1, '팔로워 증감(수)')['이름'].values[0]
        smallest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nsmallest(1, '팔로워 증감(수)')['이름'].values[0]
        
        business_to_report = [our_business, largest_inc, smallest_inc]
        metric_header = ['본 계정', 'Weekly Best', 'Weekly Worst']
        cols = st.columns([0.5, 0.25, 0.25])
        for b_idx in range(len(business_to_report)):
            business = business_to_report[b_idx]
            report_data = df_weekly_summary.loc[(date_format(df_weekly_summary['날짜']) == date_format(report_date)) & (df_weekly_summary['이름'] == business)].to_dict('records')[0]
            with cols[b_idx]:
                st_header(metric_header[b_idx], num = 6)
                st.metric(f'{business}', value = f"{report_data['팔로워 수']}명", delta = f"{report_data['팔로워 증감(수)']:.0f}명({report_data['팔로워 증감(%)']:.2f}%)")
            # st.markdown(f'''<**{report_data['이름']}**>의 {'팔로워 수'}({report_data['팔로워 수']:.0f}명)는 전주 대비 **{abs(report_data['followers_diff']):.0f}명({abs(report_data['followers_pct_change']):.2f}%)** {inc_dec(report_data['followers_diff'])}''')
        
        st.plotly_chart(px.line(data_frame = df_plot_weekly.loc[df_plot_weekly['이름'].isin(business_to_report)], x = '날짜', y = '팔로워 수', line_group = '이름', markers = True, color = '이름', title = '팔로워 수', hover_data = ['이름','날짜','팔로워 수']),
        use_container_width=True)

    
    with st.container():
        st_header('2. 참여도', num = 5)
    
        largest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nlargest(1, '참여도 증감(수)')['이름'].values[0]
        smallest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nsmallest(1, '참여도 증감(수)')['이름'].values[0]
        
        business_to_report = [our_business, largest_inc, smallest_inc]
        cols = st.columns([0.5, 0.25, 0.25])
        for b_idx in range(len(business_to_report)):
            business = business_to_report[b_idx]
            report_data = df_weekly_summary.loc[(date_format(df_weekly_summary['날짜']) == date_format(report_date)) & (df_weekly_summary['이름'] == business)].to_dict('records')[0]
            with cols[b_idx]:
                st_header(metric_header[b_idx], num = 6)
                st.metric(f'{business}', value = f"{report_data['참여도']:.2f}%", delta = f"{report_data['참여도 증감(수)']:.2f}pp({report_data['참여도 증감(%)']:.2f}%)")
            
        
        st.plotly_chart(px.line(data_frame = df_plot_weekly.loc[df_plot_weekly['이름'].isin(business_to_report)], x = '날짜', y = '참여도', line_group = '이름', markers = True, color = '이름', title = '팔로워 수', hover_data = ['이름','날짜','참여도']),
        use_container_width=True)

    er_top3 = weekly_media.nlargest(3, 'engagement')
    with st.expander('주간 Top3 게시물'):

        for c in ['timestamp', 'date']:
            er_top3[c] = pd.to_datetime(er_top3[c])
        
        er_top3 = er_top3.reset_index(drop = True).T.to_dict()

        cols = st.columns(3)
        for c in range(3):
            
            with cols[c]:
                with st.container():
                    st_header(f'{c+1}위', num = 6)
                    media_time = date_format(er_top3[c]['timestamp'])
                    st.caption(media_time)
                    media_url = er_top3[c]['media_url']
                    if pd.isnull(media_url):
                        media_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png'
                    if er_top3[c]['media_type'] == 'VIDEO':
                        st.video(media_url)
                    else:
                        st.image(media_url)
                    st.markdown(f'''
                    ❤️ {er_top3[c]['like_count']}
                    💬 {er_top3[c]['comments_count']}
                    ''')
                    st.caption(er_top3[c]['caption'])
                    
                st.markdown(f'''
                
                [🔗 게시물로]({er_top3[c]['permalink']})
                
                ''')
            

main()


