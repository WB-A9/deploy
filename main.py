import streamlit as st
import pandas as pd
from st_aggrid import AgGrid,GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import altair as alt
import plotly.express as px
import plotly.io as pio
from modules.stats import Summary
from modules.text import show_glossary, translate, date_format
from modules.design import business_colormap
import plotly.graph_objects as go


pio.templates.default = "simple_white"

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

    options.configure_selection("None")
    
    selection = AgGrid(
        df, enable_enterprise_modules=True, gridOptions=options.build(), theme="streamlit", fit_columns_on_grid_load = True, update_mode=GridUpdateMode.MODEL_CHANGED, allow_unsafe_jscode=True)

    return selection
@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

def update_business():
        st.session_state.view_index = 0
        st.session_state.business_to_compare.clear()

def on_click():
    del st.session_state.date_range

def click_business(all_business, selected_name):
    del st.session_state.business_to_compare
    if st.session_state.all_business:
        st.session_state.business_to_compare = list(set(all_business) - set([selected_name]))
        del st.session_state.all_business 
    elif st.session_state.wba9:
        st.session_state.business_to_compare = list(set(['winebook_official', 'after9']) - set([selected_name]))
        del st.session_state.wba9

def main():
    
    daily_summary = pd.read_csv('data/df_daily_summary.csv')
    media = pd.read_csv('data/updated_media.csv')
    
    df_daily_summary = daily_summary.copy()
    df_daily_summary['date'] = pd.to_datetime(df_daily_summary['date'])
    summarizer = Summary(df_daily_summary.sort_values('date'))
    n_business = df_daily_summary['name'].nunique()
    all_business = df_daily_summary['name'].unique()
    # business_colormap = dict(zip(all_business, ['#f7b32b', '#08605f', '#8e4162', '#b3cdd1', '#c7f0bd', '#bbe5ed', '#9f4a54', '#fff07c', '#ff7f11', '#ff1b1c', '#edc9ff', '#f2b79f', '#0c6291', '#231123']))
    all_date = pd.to_datetime(df_daily_summary['date'].unique())
    up_to_date = all_date.max()
    tab1, tab2, tab3 = st.tabs(['현황', '기간 내 추이', '용어 사전'])
    
    period_range = range(1,  df_daily_summary["date"].nunique())
    with st.sidebar:
        
        selected_name = st.selectbox('보고 싶은 계정', all_business, index=3, on_change = update_business)
        period =  st.selectbox('증감 대비 기준', options = period_range, format_func= lambda x: str(x)+'일 전')

    df_daily_summary = summarizer.get_summaries(summary_func=['diff', 'pct_change'], periods = [period])
    df_latest = df_daily_summary.loc[df_daily_summary['date'] == up_to_date].reset_index(drop = True)    
    df_latest.columns = translate(df_latest.columns)
    up_to_date = date_format(up_to_date)
    
    with tab1:
        st.subheader('🍷와인 Instagram 현황🥂')
        st.write(f'{up_to_date} 기준')
        col_to_show = ['순위', '이름', '팔로워 수', '팔로우 수', '게시물 수', '좋아요 수', '댓글 수', '게시물 당 좋아요', '게시물 당 댓글', '참여도']
        df_latest_toshow = df_latest.reindex(columns = col_to_show).sort_values('순위')
        
        col1, _, col3, col4, col5 = st.columns([0.15, 0.05, 0.25, 0.1, 0.1])
        
        with col1:
            with st.container():
                selected = df_latest.loc[df_latest['이름'] == selected_name].to_dict('records')[0]
                
                url = selected['profile picture url']
                st.image(url)
                

        with col3:
            with st.container():
                st.subheader(f"{selected_name}")
                bio = selected['biography']
                website = selected['website']
                
                if isinstance(bio, str):
                    st.write('Biography')
                    st.caption(bio)
                if isinstance(website, str):
                    st.write('Website')
                    st.caption(website)
        with col4:
            with st.container():         
                st.metric(f'🏅 순위', value = f"{selected['순위']}위", delta= f"{selected['순위 증감(수)']:.0f}위", help = f'전체 {n_business}개 계정의 팔로워 수 기준')
                st.metric(f"👥 팔로워 수", value = f"{selected['팔로워 수']}명", delta = f"{selected['팔로워 증감(수)']:.0f}명({selected['팔로워 증감(%)']:.2f}%)", help = '해당 계정을 팔로우 하는 계정 수')
                st.metric(f"🤝 팔로우 수", value = f"{selected['팔로우 수']}명", delta = f"{selected['팔로우 증감(수)']:.0f}명({selected['팔로우 증감(%)']:.2f}%)", help = '해당 계정이 팔로우 하는 계정 수')
                st.metric(f"📷 게시물 수", value = f"{selected['게시물 수']}개", delta = f"{selected['게시물 증감(수)']:.0f}개({selected['게시물 증감(%)']:.2f}%)", help = '전체 게시물 수')
        with col5:
            with st.container():
                st.metric(f"❤️ 좋아요 수", value = f"{selected['좋아요 수']}개", delta = f"{selected['좋아요 증감(수)']:.0f}개({selected['좋아요 증감(%)']:.2f}%)", help = '전체 게시물에 달린 좋아요 수 합계')
                st.metric(f"💬 댓글 수", value = f"{selected['댓글 수']}개", delta = f"{selected['댓글 증감(수)']:.0f}개({selected['댓글 증감(%)']:.2f}%)", help = '전체 게시물에 달린 댓글 수 합계')
                st.metric(f"💡 참여도", value = f"{selected['참여도']:.2f}%", delta = f"{selected['참여도 증감(수)']:.0f}pp({selected['참여도 증감(%)']:.2f}%)", help = '참여도 = 100 x (좋아요 수 + 댓글 수) / 팔로워 수')
                    

        with st.expander(label = 'raw data 보기'):
            st.write(f'{up_to_date} 기준')
            aggrid_interactive_table(df=df_latest_toshow)
            csv = convert_df(df_latest_toshow)
            st.download_button(
            label="csv로 저장하기",
            data=csv,
            file_name=f"IG_data_{all_date.max().strftime('%Y%m%d')}.csv",
            mime='text/csv',
            )    
    
        with st.expander(label = '게시물 보기'):
            df_media = media.copy()
            for c in ['timestamp', 'date']:
                df_media[c] = pd.to_datetime(df_media[c])
           
            st.subheader(f'[{selected_name}] 게시물')
            media_option = st.radio(label = '옵션', options = ['전체(최신순)', '좋아요 많은 순', '댓글 많은 순'], horizontal= True, label_visibility= 'collapsed')

            
            col1, col2, col3, col4, col5 = st.columns([0.1, 0.1, 0.5, 0.1, 0.1])
            with col1:
                n_view = st.selectbox("보기 수", options = range(2, 7), index = 1)
                selected_media = df_media.loc[df_media['name'] == selected_name].sort_values({'전체(최신순)': 'date', '좋아요 많은 순': 'like_count', '댓글 많은 순': 'comments_count'}[media_option], ascending= False).reset_index(drop = True).T.to_dict()
                n_selected_media = len(selected_media.keys())
                st.caption(f'{n_selected_media}개')
                max_page = n_selected_media - n_view - 1
                
            # with col2:

            with col4:
                with st.container():
                    if st.button('처음으로'):
                        st.session_state.view_index = 0
                    if st.button('이전') and st.session_state.view_index > 0:
                        st.session_state.view_index -= 1

            with col5:
                with st.container():
                    if st.button('끝으로'):
                        st.session_state.view_index = max_page
                    if st.button('다음') and st.session_state.view_index < max_page:
                        st.session_state.view_index += 1

            with col3:
                view_index = st.slider('슬라이드로 넘기기', min_value= 0, max_value = max_page, key = 'view_index')

            cols = st.columns(n_view)
            for c in range(n_view):
                
                with cols[c]:
                    with st.container():
                        media_time = date_format(selected_media[view_index + c]['timestamp'])
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
        st.subheader(f'📈[{selected_name}] 기간 내 추이')
        
        
        source = df_daily_summary.copy()
        source.columns = translate(source)
        col1, col2, col3, col4 = st.columns(4)
   
        all_features =  source.select_dtypes('number').drop(columns = 'id').columns
        
        source = summarizer.get_summaries(summary_func = ['diff', 'pct_change'], periods = [period], fillna = False)
        source.columns = translate(source.columns)

        with col1:
            if ("business_to_compare" not in st.session_state):        
                    default_business = []
            else:
                default_business = st.session_state.business_to_compare
            business_to_compare = st.multiselect('비교 계정 선택', set(all_business) - set([selected_name]), default_business, key = 'business_to_compare') 
            selected_business = [selected_name] + business_to_compare           
            st.button('전체', key = 'all_business', on_click = click_business, args = (all_business, selected_name))
            st.button('Winebook & After9', key = 'wba9', on_click = click_business, args = (all_business, selected_name))

        with col2:
            target_features = st.multiselect('보고 싶은 수치',all_features,['팔로워 수', '참여도'])        
        
        with col3:
            plot_type = st.multiselect('차트 종류', options = ['라인', '바'], default = '라인')

        with col4:
            if 'date_range' not in st.session_state:
                default_range = (all_date.min(), all_date.max())

            else:
                default_range = st.session_state.date_range
            try:
                date_start, date_end = st.date_input(label = '기간', value = default_range, min_value = all_date.min(), max_value = all_date.max(), help= '범위 선택', key= 'date_range')
                
            except:
                date_start, date_end = (all_date.min(), all_date.max())
            
        
            st.button('전체 기간', on_click = on_click)
                
                
        source = source[(source['이름'].isin(selected_business)) & (source['날짜'].between(pd.to_datetime(date_start), pd.to_datetime(date_end)))]
        if date_start and date_end:
            for target_feature in target_features:
                fig = go.Figure()
                chart = []
                plot_title = f'{target_feature}'
                if '증감' in target_feature:
                    source_to_plot = source.copy().dropna(subset = target_features)
                    plot_title += f'({period}일 전 대비)'     
                else:
                    source_to_plot = source.copy()
                if source_to_plot[target_feature].dtype == int:
                    text_auto = True
                else:
                    text_auto = '.2f'
                
                if '라인' in plot_type:
                    chart.extend(px.line(data_frame = source_to_plot, x = '날짜', y = target_feature, line_group = '이름', markers = True, color = '이름', title = plot_title, hover_data = ['이름','날짜',target_feature], color_discrete_map = business_colormap).data
                    )
                if '바' in plot_type:
                    chart.extend(px.bar(data_frame = source_to_plot, x = '날짜', y = target_feature, barmode = 'group', text_auto= text_auto, color = '이름', title = plot_title, hover_data = ['이름','날짜',target_feature], opacity=0.5, color_discrete_map = business_colormap).data
                )
            
                for data in chart:
                    fig.add_trace(data)
                    # chart.update_xaxes(rangeslider_visible=True)
                    # st.plotly_chart(chart,use_container_width= True)
                fig.update_layout(title = plot_title, xaxis_title= "날짜", yaxis_title= target_feature,)
                fig.update_xaxes(rangeslider_visible=True)    
                st.plotly_chart(fig,use_container_width= True)

    with tab3:
        show_glossary()
    
st.set_page_config(
    page_title='WB-A9 인스타그램 현황', layout='wide')

main()






