import streamlit as st
import pandas as pd
from st_aggrid import AgGrid,GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import altair as alt
import plotly.express as px
import plotly.io as pio
from modules.stats import Summary

pio.templates.default = "simple_white"

def get_chart(data,target_col,target_name,title):
    hover = alt.selection_single(
        fields=["날짜"], nearest=True, on="mouseover", empty="none",    )

    lines = (
        alt.Chart(data,title= title)
        .mark_line()
        .encode(
            x="date(이름)",     y= target_col,     color="이름")
    )

    # Draw points on the line,and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="date(날짜)",     y= target_col,     opacity=alt.condition(hover,alt.value(0.3),alt.value(0)),     tooltip=[
                alt.Tooltip("이름",title="이름"),         alt.Tooltip("날짜",title="날짜"),         alt.Tooltip(target_col,title=target_name),     ], )
        .add_selection(hover)
    )

    return (lines + points + tooltips).interactive()

def translate(columns):
    trans_dict = {'rank': '순위', 'name': '이름', 'followers' : '팔로워', 'follows': '팔로우', 'media': '게시물', 'like': '좋아요', 'comments': '댓글', 'diff': '증감(수)', 'pct_change': '증감(%)', 'count': '수', 'ratio': '당', 'date': '날짜'}
    trans_cols = []
    for name in columns:
        trans_words = ''
        if 'pct_change' in name:
            splitted = name.split('_pct_change')[0].split('_') + ['pct_change']
        else:
            splitted = name.split('_')
        if 'ratio' in splitted:
            splitted.insert(2, splitted.pop(0))
        for word in splitted:
            if trans_dict.get(word):
                word = trans_dict[word]
            trans_words += word + ' '
        trans_cols.append(trans_words.strip())
    return trans_cols

def set_date_range(start = '2021-11-20',end = '2021-12-25'):    
    return pd.date_range(start=start,end=end,freq='D')

def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df,enableRowGroup=True,enableValue=True,enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    
    selection = AgGrid(
        df, enable_enterprise_modules=True, gridOptions=options.build(), theme="streamlit", update_mode=GridUpdateMode.MODEL_CHANGED, allow_unsafe_jscode=True)

    return selection

def main():
    st.set_page_config(
    page_title='WB-A9 인스타그램 현황', layout='wide')
    
    df_daily_summary = pd.read_csv('data/df_daily_summary.csv')
    df_daily_summary['date'] = pd.to_datetime(df_daily_summary['date'])
    summarizer = Summary(df_daily_summary.sort_values('date'))

    tab1, tab2 = st.tabs(['현황', '기간 내 추이'])

    df_daily_summary = summarizer.get_summaries(summary_func=['diff'], periods = [1])
    n_business = df_daily_summary['name'].nunique()
    all_business = df_daily_summary['name'].unique()

    up_to_date = max(df_daily_summary['date'])

    df_latest = df_daily_summary.loc[df_daily_summary['date'] == up_to_date].reset_index(drop = True)
    df_latest['rank'] = df_latest['followers_count'].rank(ascending = False)
    
    df_latest.columns = translate(df_latest.columns)
    up_to_date = up_to_date.strftime('%Y년 %m월 %d일')

    with tab1:
        st.subheader('🍷와인 인플루언서 Instagram 현황🥂')
        st.write(f'{up_to_date} 기준')
        col_to_show = ['순위', '이름', '팔로워 수', '팔로우 수', '게시물 수', '좋아요 수', '댓글 수']
        df_latest_toshow = df_latest.reindex(columns = col_to_show).sort_values('순위')

        
        col1, col2, col3, col4 = st.columns([0.5, 0.2, 0.1, 0.1])
        with col1:
            selection = aggrid_interactive_table(df=df_latest_toshow)
            st.write('선택시 자세히 보기')
        with col2:
            with st.container():
                if selection['selected_rows']:
                    selected = selection["selected_rows"][0]
                    selected_name = selected['이름']
                    selected_df = df_latest.loc[df_latest['이름'] == selected_name]
                    selected_df[selected_df.select_dtypes('number').columns] = selected_df.select_dtypes('number').astype(int)
                    url = selected_df['profile picture url'].values[0]
                    bio = selected_df['biography'].values[0]
                    st.image(url)
                    st.subheader(f"{selected_name}")
                    if isinstance(bio, str):
                        st.write('Biography')
                        st.caption(bio)
                    with col3:
                        with st.container():
                            
                            st.metric('🏅 순위', value = f"{selected['순위']} 위", delta= None , delta_color="normal", help=None)
                            st.metric(f"👥 팔로워 수", value = f"{selected['팔로워 수']}명", delta = f"{selected_df['팔로워 증감(수)'].values[0]}명")
                            st.metric(f"🤝 팔로우 수", value = f"{selected['팔로우 수']}명", delta = f"{selected_df['팔로우 증감(수)'].values[0]}명")
                    with col4:
                        with st.container():
                            st.metric(f"📷 게시물 수", value = f"{selected['게시물 수']}개", delta = f"{selected_df['게시물 증감(수)'].values[0]}개")
                            st.metric(f"❤️ 좋아요 수", value = f"{selected['좋아요 수']}개", delta = f"{selected_df['좋아요 증감(수)'].values[0]}개")
                            st.metric(f"💬 댓글 수", value = f"{selected['댓글 수']}개", delta = f"{selected_df['댓글 증감(수)'].values[0]}개")
                        

            

        st.markdown('---')
        if selection['selected_rows']:
            
            media = pd.read_csv('data/updated_media.csv')
            for c in ['timestamp', 'date']:
                media[c] = pd.to_datetime(media[c])

            
            selected_media = media.loc[media['name'] == selected_name].reset_index(drop = True).T.to_dict()
            n_selected_media = len(selected_media.keys())
            st.subheader(f'[{selected_name}] 게시물')
            st.markdown(f'#### {n_selected_media}개')
            col1, col2 = st.columns(2)
            with col1:
                n_view = st.selectbox("보기 수", options = range(4, 7))
            with col2:
                view_index = st.slider('슬라이드로 넘기기', min_value= 0, max_value = n_selected_media - n_view - 1)
            cols = st.columns(n_view)
            for c in range(n_view):
                with cols[c]:
                    with st.container():
                        media_time = selected_media[view_index + c]['timestamp'].strftime("%Y년 %m월 %d일")
                        st.caption(media_time)
                        media_url = selected_media[view_index + c]['media_url']
                        if pd.isnull(media_url):
                            media_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png'
                        if selected_media[view_index + c]['media_type'] == 'VIDEO':
                            st.video(media_url)
                        else:
                            st.image(media_url)
                        st.markdown(f'''
                        ❤️ {selected_media[view_index + c]['like_count']}
                        💬 {selected_media[view_index + c]['comments_count']}
                        ''')
                        st.caption(selected_media[view_index + c]['caption'])
                        
                    st.markdown(f'''
                    
                    [🔗 게시물로]({selected_media[view_index + c]['permalink']})
                    
                    ''')
                    
                    
                


    with tab2:
        st.subheader(f'📈기간 내 추이')
        
        
        source = df_daily_summary.copy()
        source.columns = translate(source)
        col1, col2, col3, col4 = st.columns(4)
        

        
        all_features =  source.select_dtypes('number').drop(columns = 'id').columns
        buttons = [st.button('전체'),st.button('Winebook & After9')]
        with col1:
            
            if buttons[1] or ("selected_business" not in st.session_state):        
                    default_business = ['winebook_official','after9']
            elif buttons[0]:
                    default_business = all_business.copy()
            else:
                default_business = st.session_state.selected_business
            selected_business = st.multiselect('보고 싶은 업체 선택', all_business, default_business, key = 'selected_business')            

        with col2:
            target_features = st.multiselect('보고 싶은 수치',all_features,'팔로워 수')
            
        with col3:
            
            period =  st.selectbox('증감 비교 일수', options = range(1,  source["날짜"].nunique()), disabled = all('증감' not in f for f in target_features))
            source = summarizer.get_summaries(summary_func = ['diff', 'pct_change'], periods = [period], fillna = False)
            source.columns = translate(source.columns)
        with col4:
            plot_type = st.radio('차트 종류', options = ['라인', '바'], index = 0)
        
        source = source[source['이름'].isin(selected_business)]
        for target_feature in target_features:
            plot_title = f'{target_feature}'
            if '증감' in target_feature:
                source_to_plot = source.copy().dropna(subset = target_features)
                plot_title += f'({period}일 전 대비)'
            else:
                source_to_plot = source.copy()
            if plot_type == '라인':
                chart = px.line(data_frame = source_to_plot, x = '날짜', y = target_feature, line_group = '이름', markers = True, color = '이름', title = plot_title, hover_data = ['이름','날짜',target_feature]
                )
            elif plot_type == '바':
                chart = px.bar(data_frame = source_to_plot, x = '날짜', y = target_feature, barmode = 'group', text_auto='.2s', color = '이름', title = plot_title, hover_data = ['이름','날짜',target_feature]
            )
            chart.update_xaxes(rangeslider_visible=True)
            st.plotly_chart(chart,use_container_width= True)
            

main()






