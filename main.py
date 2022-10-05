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

def tag_sign(number):
    if number > 0:
        sign = '🔼 '
    elif number < 0:
        sign = '🔽 '
    else:
        sign = ''        
    return sign + str(abs(number))

def main():
    st.set_page_config(
    page_title='WB-A9 인스타그램 현황', layout='wide')
    
    
    df_daily_summary = pd.read_csv('data/df_daily_summary.csv')
    df_daily_summary['date'] = pd.to_datetime(df_daily_summary['date'])
    summarizer = Summary(df_daily_summary.sort_values('date'))

    df_daily_summary = summarizer.get_summaries(summary_func=['diff'], periods = [1])
    n_business = df_daily_summary['name'].nunique()
    all_business = df_daily_summary['name'].unique()

    up_to_date = max(df_daily_summary['date'])

    df_latest = df_daily_summary.loc[df_daily_summary['date'] == up_to_date].reset_index(drop = True)
    df_latest['rank'] = df_latest['followers_count'].rank(ascending = False)
    
    df_latest.columns = translate(df_latest.columns)
    up_to_date = up_to_date.strftime('%Y년 %m월 %d일')
    st.subheader('🍷와인 인플루언서 Instagram 현황🥂')
    st.write(f'{up_to_date} 기준')
    col_to_show = ['순위', '이름', '팔로워 수', '팔로우 수', '게시물 수', '좋아요 수', '댓글 수']
    df_latest_toshow = df_latest.reindex(columns = col_to_show).sort_values('순위')

    
    col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
    with col1:
        selection = aggrid_interactive_table(df=df_latest_toshow)
        st.write('선택시 자세히 보기')
    with col2:
        if selection['selected_rows']:
            selected = selection["selected_rows"][0]
            selected_df = df_latest.loc[df_latest['이름'] == selected['이름']]
            
            url = selected_df['profile picture url'].values[0]
            bio = selected_df['biography'].values[0]
            st.image(url)
            st.subheader(f"{selected['이름']}")
            if isinstance(bio, str):
                st.write('Biography')
                st.write(bio)
            with col3:
                    st.write(f"순위: {selected['순위']} / {n_business} 위")
                    st.write(f"팔로워 수: {selected['팔로워 수']} 명(전일대비 {tag_sign(selected_df['팔로워 증감(수)'].values[0])} )")
                    st.write(f"팔로우 수: {selected['팔로우 수']} 명(전일대비 {tag_sign(selected_df['팔로우 증감(수)'].values[0])} ) ")
                    st.write(f"게시물 수: {selected['게시물 수']} 개(전일대비 {tag_sign(selected_df['게시물 증감(수)'].values[0])} )")
                    st.write(f"좋아요 수: {selected['좋아요 수']} 개(전일대비 {tag_sign(selected_df['좋아요 증감(수)'].values[0])} )")
                    st.write(f"댓글 수: {selected['댓글 수']} 개(전일대비 {tag_sign(selected_df['댓글 증감(수)'].values[0])} )")
    

    st.markdown('---')
    st.subheader(f'📈기간 내 추이')
    
    
    source = df_daily_summary.copy()
    source.columns = translate(source)
    col1,col2, col3 = st.columns(3)
    

    
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
    
    
    source = source[source['이름'].isin(selected_business)]
    for target_feature in target_features:
        if '증감' in target_feature:
            source_to_plot = source.copy().dropna(subset = target_features)
        else:
            source_to_plot = source.copy()
        chart = px.line(data_frame = source_to_plot, x = '날짜', y = target_feature, line_group = '이름', markers = True, color = '이름', title = f'{target_feature} 추이', hover_data = ['이름','날짜',target_feature]

        )
        chart.update_xaxes(rangeslider_visible=True)
        
        st.plotly_chart(chart,use_container_width= True)

main()






