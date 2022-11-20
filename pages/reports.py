import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from modules.stats import Summary
from modules.text import show_glossary, st_header, translate, date_format, get_week_num
from datetime import datetime, timedelta, timezone
from modules.db import load_data, get_by_query, insert_data
from modules.tools import aggrid_interactive_table, convert_df
from modules.design import Bar, business_colormap
from modules.auth import check_password, signout
import os

pio.templates.default = "simple_white"

def main():
    
    report_init = pd.to_datetime(datetime(2022, 10, 3, 12, 0, tzinfo = timezone(timedelta(hours = 9))))
    
    current_time = pd.to_datetime(datetime.now(tz = timezone(timedelta(hours=9))))

    report_period = pd.date_range(start = report_init, end = current_time, freq = '7D')
    
    with st.sidebar:
        target_business = st.selectbox('분석 계정', options = ['winebook_official', 'after9'])
        report_end = st.selectbox(label = '주차', options = report_period[::-1], format_func = get_week_num)
        report_start = pd.to_datetime(report_end - timedelta(days = 7))
        report_date = report_end
        
    df_weekly_summary = load_data('weekly_summary')
    weekly_media = get_by_query(f"SELECT * FROM test_weekly_media WHERE date > '{date_format(report_start, '-')}'")
    
    if not date_format(report_date) in date_format(df_weekly_summary['날짜']).tolist():
        with st.spinner(text="Updating data for weekly reports"):
            df_daily_summary = load_data('daily_summary')
            df_daily_summary['date'] = pd.to_datetime(df_daily_summary['date'])
            summarizer = Summary(df_daily_summary.sort_values('date'))
            df_weekly_summary = summarizer.get_summaries(summary_func=['diff', 'pct_change'], periods = [7])
            df_weekly_summary.columns = translate(df_weekly_summary.columns)
            df_weekly_summary = df_weekly_summary.loc[df_weekly_summary['날짜'].dt.dayofweek == 0]
            
            insert_data(df_weekly_summary.loc[df_weekly_summary['날짜'] == df_weekly_summary['날짜'].max()], 'weekly_summary')   
    
    if weekly_media.empty:
          with st.spinner(text="Updating data for weekly reports"):
            media = load_data('latest_media')
            weekly_media = media.loc[media['timestamp'].between(date_format(report_start, format = '-'), date_format(report_end, format = '-'))]
            weekly_media['engagement'] = weekly_media['like_count'] + weekly_media['comments_count']
            insert_data(weekly_media, 'weekly_media')      
       
    df_plot_weekly = df_weekly_summary[(df_weekly_summary['날짜'].dt.dayofweek == report_date.dayofweek)]
    
    df_plot_weekly['날짜'] = date_format(df_plot_weekly['날짜'])
    all_business = sorted(df_weekly_summary['이름'].unique().tolist())
    
    with st.sidebar:
        with st.expander('그래프에 포함'):
            selected_business = []
            all_select = st.button('전체 선택')
            all_rm = st.button('전체 제거')

            for business in all_business:
                tmp_key = 'plot_'+business
                if all_select:
                    st.session_state[tmp_key] = True
                if all_rm:
                    st.session_state[tmp_key] = False
                tmp_check = st.checkbox(business, key = tmp_key, value = business != 'Wine Folly')
                if tmp_check:
                    selected_business.append(business)
        if check_password():
            if signout():
                return None
                    
            
    
    tab1, tab2, tab3 = st.tabs(['보고서', '데이터 보기', '용어 사전'])
    with tab1:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            st_header(target_business, num = 2)
            st_header(f'{get_week_num(report_end)} 주간 보고서', num = 3)
            st.caption(f'분석 기간: {date_format(report_start)} ~ {date_format(report_end)}')
            st.caption(f'작성일: {date_format(report_date)} 월요일' )
            

        with col2:
            image_path = f"img/{target_business}.jpeg"
            st.image(image_path)

        st_header('', num = 1)        
        with st.container():
            st_header('1. 팔로워 수', num = 4)
        
            largest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nlargest(1, '팔로워 증감(%)')['이름'].values[0]
            smallest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nsmallest(1, '팔로워 증감(%)')['이름'].values[0]
            
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
            
            df_to_plot = df_plot_weekly.loc[((df_plot_weekly['날짜'] == date_format(report_date)) | (df_plot_weekly['날짜'] == date_format(report_start))) & (df_plot_weekly["이름"].isin(selected_business))]
            if selected_business:
                for feature in ["팔로워 수", "팔로워 증감(수)"]:
                    fig = Bar(df = df_to_plot.sort_values(['날짜', feature]), text = feature, y = feature, x = '이름', group = '이름', colormap = business_colormap , title = feature, range_slider = False, barmode = 'relative', facet_col = '날짜')
                    #fig.update_traces(visible = 'legendonly', selector = ({'name': 'Wine Folly'}))
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
            
            if selected_business:
                for feature in ["참여도", "참여도 증감(%)"]:
                    fig = Bar(df = df_to_plot.sort_values(['날짜', feature]), text = feature, y = feature, x = '이름', group = '이름', colormap = business_colormap , title = feature, range_slider = False, barmode = 'relative', facet_col = '날짜')
                    ## fig.update_traces(visible = 'legendonly', selector = ({'name': 'Wine Folly'}))
                    st.plotly_chart(fig, use_container_width=True)

        with st.container():
            st_header('3. 게시물', num = 4)
        
            largest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nlargest(1, '게시물 증감(%)')['이름'].values[0]
            smallest_inc = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date)].nsmallest(1, '게시물 증감(%)')['이름'].values[0]
            
            business_to_report = [target_business, largest_inc, smallest_inc]
            metric_header = ['본 계정', 'Weekly Best', 'Weekly Worst']
            cols = st.columns([0.5, 0.25, 0.25])
            for b_idx in range(len(business_to_report)):
                business = business_to_report[b_idx]
                report_data = df_weekly_summary.loc[(date_format(df_weekly_summary['날짜']) == date_format(report_date)) & (df_weekly_summary['이름'] == business)].to_dict('records')[0]
                with cols[b_idx]:
                    st_header(metric_header[b_idx], num = 5)
                    st.metric(f'{business}', value = f"{report_data['게시물 수']}개", delta = f"{report_data['게시물 증감(수)']:.0f}개({report_data['게시물 증감(%)']:.2f}%)")
                
            if selected_business:
                for feature in ["게시물 수", "게시물 증감(수)"]:
                    fig = Bar(df = df_to_plot.sort_values(['날짜', feature]), text = feature, y = feature, x = '이름', group = '이름', colormap = business_colormap , title = feature, range_slider = False, barmode = 'relative', facet_col = '날짜')
                    ## fig.update_traces(visible = 'legendonly', selector = ({'name': 'Wine Folly'}))
                    st.plotly_chart(fig, use_container_width=True)
            
        with st.container():
            st_header('주간 Top3 게시물(참여도 기준)', num = 6)
            df_weekly_follower_cnt = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date), ['이름', '팔로워 수']]

            df_er = pd.merge(weekly_media, df_weekly_follower_cnt, how = 'inner', left_on = 'name', right_on = '이름')
            df_er['engagementRate'] = 100 * df_er['engagement'] / df_er['팔로워 수']

            for business in [(all_business, '전체'), ([target_business], target_business)]:
                
                
                er_top3 = df_er.loc[(df_er['name'].isin(business[0]))].nlargest(3, 'engagementRate')
                
                if not df_er.empty:
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
                                    (참여도 {er_top3[c]['engagementRate']: .2f}%)
                                    ''')
                                    st.caption(er_top3[c]['caption'])
                                    
                                st.markdown(f'''
                                
                                [🔗 게시물로]({er_top3[c]['permalink']})
                                
                                ''')
                else:
                    st.write('지난 주 게시물이 없었습니다.')
            
            st.markdown('---')
            
    with tab2:
        
        summary_to_save = df_weekly_summary.loc[date_format(df_weekly_summary['날짜']) == date_format(report_date),
        ['순위', '이름', '날짜', '팔로우 수', '팔로워 수', '게시물 수', 
       '좋아요 수', '댓글 수', '참여도', '게시물 당 좋아요', '게시물 당 댓글', '팔로우 증감(수)', '팔로워 증감(수)', '게시물 증감(수)',
       '좋아요 증감(수)', '댓글 증감(수)', '순위 증감(수)', '참여도 증감(수)', '게시물 당 좋아요 증감(수)',
       '게시물 당 댓글 증감(수)', '팔로우 증감(%)', '팔로워 증감(%)', '게시물 증감(%)', '좋아요 증감(%)',
       '댓글 증감(%)', '순위 증감(%)', '참여도 증감(%)', '게시물 당 좋아요 증감(%)',
       '게시물 당 댓글 증감(%)']].sort_values('순위').reset_index(drop = True)
        
        weekly_media.columns = translate(weekly_media.columns)
        media_to_save = weekly_media[['이름', '게시물 주소', '게시물 종류', '좋아요 수', '댓글 수', '참여 수', '업로드 시간', '캡션']]
        
        st_header('주간 데이터', num = 3)

        with st.expander('요약 데이터'):
            st.dataframe(summary_to_save)
            st.download_button(
                label="저장",
                data= convert_df(summary_to_save),
                file_name=f"IG 요약 데이터 {get_week_num(report_end)}.csv",
                mime='text/csv',
                )
            

        with st.expander('미디어 데이터'):
            st.dataframe(media_to_save)
            st.download_button(
                label="저장",
                data= convert_df(media_to_save),
                file_name=f"IG 미디어 데이터 {get_week_num(report_end)}.csv",
                mime='text/csv',
                )
            
     
    with tab3:
        show_glossary()
                    




st.set_page_config(layout='wide')

if check_password():
    main()
    
with st.sidebar:
    st.info('''문의 및 요청  
    *[jihong2jihong@gmail.com](mailto:jihong2jihong@gmail.com)*
        ''', icon = "❓")