import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from modules.stats import Summary
from modules.text import show_glossary, st_header, translate, date_format, get_week_num
from datetime import datetime, timedelta, timezone
import os
from modules.authentification import check_password, signout
from modules.design import Bar, business_colormap

pio.templates.default = "simple_white"

def main():
    
    report_init = pd.to_datetime(datetime(2022, 10, 3, 12, 0, tzinfo = timezone(timedelta(hours = 9))))
    
    current_time = pd.to_datetime(datetime.now(tz = timezone(timedelta(hours=9))))

    report_period = pd.date_range(start = report_init, end = current_time - timedelta(days = 7), freq = '7D')
    
    with st.sidebar:
        target_business = st.selectbox('분석 계정', options = ['winebook_official', 'after9'])
        report_start = st.selectbox(label = '주차', options = report_period[::-1], format_func = get_week_num)
        report_end = pd.to_datetime(report_start + timedelta(days = 7))
        report_date = report_end
        # report_date = pd.to_datetime(report_end + timedelta(days = 0))
        
        
    
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
        weekly_media = media.copy().loc[media['timestamp'].between(date_format(report_start, format = '-'), date_format(report_end, format = '-'))]
        weekly_media['engagement'] = weekly_media['like_count'] + weekly_media['like_count']
        weekly_media.to_csv(os.path.join(REPORT_DATA_BASE, w_media_data_path), index = False)
    
    
    df_plot_weekly = df_weekly_summary[(df_weekly_summary['날짜'].dt.dayofweek == report_date.dayofweek)]
    
    # df_plot_weekly = df_weekly_summary[df_weekly_summary['날짜'].dt.dayofweek == report_date.dayofweek]
    df_plot_weekly['날짜'] = date_format(df_plot_weekly['날짜'])
    all_business = sorted(df_weekly_summary['이름'].unique().tolist())
    # # business_colormap = dict(zip(all_business, px.colors.qualitative.Alphabet[:len(all_business)+1]))
    # business_colormap = dict(zip(all_business, ['#f7b32b', '#08605f', '#8e4162', '#b3cdd1', '#c7f0bd', '#bbe5ed', '#9f4a54', '#fff07c', '#ff7f11', '#ff1b1c', '#edc9ff', '#f2b79f', '#0c6291', '#231123']))
    tab1, tab2 = st.tabs(['보고서', '용어 사전'])
    with tab1:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st_header(target_business, num = 2)
            st_header(f'{get_week_num(report_start)} 주간 보고서', num = 3)
            st.caption(f'분석 기간: {date_format(report_start)} ~ {date_format(report_end)}')
            st.caption(f'작성일: {date_format(report_date)} 월요일' )
            

        with col2:
            
            # url = df_weekly_summary.sort_values('날짜', ascending = False).loc[df_weekly_summary['이름'] == target_business, 'profile picture url'].unique()[0]
            image_path = f"img/{target_business}.jpeg"
            st.image(image_path)

        st_header('', num = 1)        
        with st.container():
            st_header('1. 팔로워 수', num = 4)
        
            largest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nlargest(1, '팔로워 증감(수)')['이름'].values[0]
            smallest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nsmallest(1, '팔로워 증감(수)')['이름'].values[0]
            
            business_to_report = [target_business, largest_inc, smallest_inc]
            metric_header = ['본 계정', 'Weekly Best', 'Weekly Worst']
            cols = st.columns([0.5, 0.25, 0.25])
            for b_idx in range(len(business_to_report)):
                business = business_to_report[b_idx]
                report_data = df_weekly_summary.loc[(date_format(df_weekly_summary['날짜']) == date_format(report_date)) & (df_weekly_summary['이름'] == business)].to_dict('records')[0]
                with cols[b_idx]:
                    st_header(metric_header[b_idx], num = 5)
                    st.metric(f'{business}', value = f"{report_data['팔로워 수']}명", delta = f"{report_data['팔로워 증감(수)']:.0f}명({report_data['팔로워 증감(%)']:.2f}%)")
                # st.markdown(f'''<**{report_data['이름']}**>의 {'팔로워 수'}({report_data['팔로워 수']:.0f}명)는 전주 대비 **{abs(report_data['followers_diff']):.0f}명({abs(report_data['followers_pct_change']):.2f}%)** {inc_dec(report_data['followers_diff'])}''')
            
            for feature in ["팔로워 수", "팔로워 증감(수)"]:
                fig = Bar(df = df_plot_weekly.loc[(df_plot_weekly['날짜'] == date_format(report_date)) | (df_plot_weekly['날짜'] == date_format(report_start))].sort_values(['날짜', feature]),  y = feature, x = '이름', group = '이름', text_auto = True, colormap = business_colormap , title = feature, range_slider = False, barmode = 'relative', facet_col = '날짜')
                fig.update_traces(visible = 'legendonly', selector = ({'name': 'Wine Folly'}))
                st.plotly_chart(fig, use_container_width=True)

        
        with st.container():
            st_header('2. 참여도', num = 4)
        
            largest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nlargest(1, '참여도 증감(%)')['이름'].values[0]
            smallest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nsmallest(1, '참여도 증감(%)')['이름'].values[0]
            
            business_to_report = [target_business, largest_inc, smallest_inc]
            cols = st.columns([0.5, 0.25, 0.25])
            for b_idx in range(len(business_to_report)):
                business = business_to_report[b_idx]
                report_data = df_weekly_summary.loc[(date_format(df_weekly_summary['날짜']) == date_format(report_date)) & (df_weekly_summary['이름'] == business)].to_dict('records')[0]
                with cols[b_idx]:
                    st_header(metric_header[b_idx], num = 5)
                    st.metric(f'{business}', value = f"{report_data['참여도']:.2f}%", delta = f"{report_data['참여도 증감(수)']:.2f}pp({report_data['참여도 증감(%)']:.2f}%)")
            
            for feature in ["참여도", "참여도 증감(%)"]:
                fig = Bar(df = df_plot_weekly.loc[(df_plot_weekly['날짜'] == date_format(report_date)) | (df_plot_weekly['날짜'] == date_format(report_start))].sort_values(['날짜', feature]),  y = feature, x = '이름', group = '이름', text_auto = True, colormap = business_colormap , title = feature, range_slider = False, barmode = 'relative', facet_col = '날짜')
                # fig.update_traces(visible = 'legendonly', selector = ({'name': 'Wine Folly'}))
                st.plotly_chart(fig, use_container_width=True)

        with st.container():
            st_header('3. 게시물', num = 4)
        
            largest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nlargest(1, '게시물 증감(수)')['이름'].values[0]
            smallest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nsmallest(1, '게시물 증감(수)')['이름'].values[0]
            
            business_to_report = [target_business, largest_inc, smallest_inc]
            metric_header = ['본 계정', 'Weekly Best', 'Weekly Worst']
            cols = st.columns([0.5, 0.25, 0.25])
            for b_idx in range(len(business_to_report)):
                business = business_to_report[b_idx]
                report_data = df_weekly_summary.loc[(date_format(df_weekly_summary['날짜']) == date_format(report_date)) & (df_weekly_summary['이름'] == business)].to_dict('records')[0]
                with cols[b_idx]:
                    st_header(metric_header[b_idx], num = 5)
                    st.metric(f'{business}', value = f"{report_data['게시물 수']}개", delta = f"{report_data['게시물 증감(수)']:.0f}개({report_data['게시물 증감(%)']:.2f}%)")
                
            
            for feature in ["게시물 수", "게시물 증감(수)"]:
                fig = Bar(df = df_plot_weekly.loc[(df_plot_weekly['날짜'] == date_format(report_date)) | (df_plot_weekly['날짜'] == date_format(report_start))].sort_values(['날짜', feature]),  y = feature, x = '이름', group = '이름', text_auto = True, colormap = business_colormap , title = feature, range_slider = False, barmode = 'relative', facet_col = '날짜')
                # fig.update_traces(visible = 'legendonly', selector = ({'name': 'Wine Folly'}))
                st.plotly_chart(fig, use_container_width=True)

        with st.container():
            st_header('주간 Top3 게시물(참여도 기준)', num = 6)
            

            for business in [(all_business, '전체'), ([target_business], target_business)]:
                er_top3 = weekly_media.loc[(weekly_media['name'].isin(business[0]))].nlargest(3, 'engagement')
                
                if not weekly_media.empty:
                    with st.expander(f'{business[1]}'):

                        for c in ['timestamp', 'date']:
                            er_top3[c] = pd.to_datetime(er_top3[c])
                        
                        er_top3 = er_top3.reset_index(drop = True).T.to_dict()

                        cols = st.columns(3)
                        for c in range(len(er_top3)):
                            
                            with cols[c]:
                                with st.container():
                                    st_header(f'{c+1}위', num = 6)
                                    media_time = date_format(er_top3[c]['timestamp'])
                                    st.caption(er_top3[c]['name'])
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
                else:
                    st.write('지난 주 게시물이 없었습니다.')
            
            st.markdown('---')
#             signout()
    with tab2:
        show_glossary()
                    




st.set_page_config(layout='wide')

# if check_password():
main()
    
