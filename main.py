import streamlit as st
import pandas as pd
import os
from st_aggrid import AgGrid,GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import altair as alt
from datetime import datetime
import plotly.express as px
import plotly.io as pio

pio.templates.default = "simple_white"
# pio.templates.

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

    # options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df, enable_enterprise_modules=True, gridOptions=options.build(), theme="alpine", update_mode=GridUpdateMode.MODEL_CHANGED, allow_unsafe_jscode=True,    )

    return selection

feature_dict = {'rank': '순위', 'name': '이름', 'followers_count': '팔로워 수', 'follows_count': '팔로우 수', 'media_count': '게시물 수', 'like_count': '좋아요 수', 'comments_count': '댓글 수', 'followers_diff': '팔로워 증감(수)', 'follows_diff': '팔로우 증감(수)', 'media_diff': '게시물 증감(수)', 'like_diff': '좋아요 증감(수)', 'comments_diff': '댓글 증감(수)', 'followers_pct_change': '팔로워 증감(%)', 'follows_pct_change': '팔로우 증감(%)', 'media_pct_change': '게시물 증감(%)', 'like_pct_change': '좋아요 증감(%)', 'comments_pct_change': '댓글 증감(%)'}

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
    page_title='인스타그램 현황',    layout='wide')
    
    
    df_daily_summary = pd.read_csv('data/df_daily_summary.csv')
    df_daily_summary['date'] = pd.to_datetime(df_daily_summary['date'])

    n_business = df_daily_summary['name'].nunique()

    up_to_date = max(df_daily_summary['date'])

    df_latest = df_daily_summary.loc[df_daily_summary['date'] == up_to_date].reset_index(drop = True)
    df_latest['rank'] = df_latest['followers_count'].rank(ascending = False)
    df_latest = df_latest.rename(columns = feature_dict)
    up_to_date = up_to_date.strftime('%Y년 %m월 %d일')
    st.subheader(f'업체 별 Instagram 현황: {up_to_date} 기준')
    # added_feature = st.multiselect('보고 싶은 특성 : ',list(feature_dict.values()),['순위','이름','팔로워 수','팔로워 증감(수)'])
    df_latest_toshow = df_latest.reindex(columns = list(feature_dict.values())).sort_values('순위')


    col1,col2 = st.columns(2)
    with col1:
        selection = aggrid_interactive_table(df=df_latest_toshow)
    with col2:
        st.write('업체 클릭 후 자세히 보기')
        if selection['selected_rows']:
            selected = selection["selected_rows"][0]
            url = df_latest.loc[df_latest['이름'] == selected['이름'],'profile_picture_url'].values[0]
            st.image(url,width = 120)
            st.subheader(f"{selected['이름']}")
            st.write(f"순위: {selected['순위']} / {n_business} 위")
            st.write(f"팔로워 수: {selected['팔로워 수']} 명( {tag_sign(selected['팔로워 증감(수)'])} )")
            st.write(f"팔로우 수: {selected['팔로우 수']} 명( {tag_sign(selected['팔로우 증감(수)'])} ) ")
            st.write(f"게시물 수: {selected['게시물 수']} 개( {tag_sign(selected['게시물 증감(수)'])} )")
            st.write(f"좋아요 수: {selected['좋아요 수']} 개( {tag_sign(selected['좋아요 증감(수)'])} )")
            st.write(f"댓글 수: {selected['댓글 수']} 개( {tag_sign(selected['댓글 증감(수)'])} )")
    
    source = df_daily_summary.copy().sort_values('date')
    feature_dict.update({'date' : '날짜'})
    source = source.rename(columns = feature_dict)
    all_business = source['이름'].unique()
    all_features =  ['팔로워 수', '팔로우 수', '게시물 수', '좋아요 수', '댓글 수', '팔로워 증감(수)', '팔로우 증감(수)', '게시물 증감(수)', '좋아요 증감(수)', '댓글 증감(수)', '팔로워 증감(%)', '팔로우 증감(%)', '게시물 증감(%)', '좋아요 증감(%)', '댓글 증감(%)']
    

    st.markdown('---')
    st.subheader(f'기간 내 추이')
    
    col1,col2 = st.columns(2)
    buttons = [st.button('전체'),st.button('Winebook & After9')]
    with col1:
        
        if buttons[1] or ("selected_business" not in st.session_state):        
                default_business = ['winebook_official','after9']
        elif buttons[0]:
                default_business = all_business
        else:
            default_business = st.session_state.selected_business

        selected_business = st.multiselect('보고 싶은 업체 선택',all_business, default_business,key = 'selected_business')        
        source = source[source['이름'].isin(selected_business)]
        
    with col2:
        target_features = st.multiselect('보고 싶은 수치',all_features,'팔로워 수')

    for target_feature in target_features:
        chart = px.line(data_frame = source, x = '날짜', y = target_feature, line_group = '이름', markers = True, color = '이름', title = f'{target_feature} 추이', hover_data = ['이름','날짜',target_feature]

        )
        chart.update_xaxes(rangeslider_visible=True)
        
        st.plotly_chart(chart,use_container_width= True)
        
    


main()






