import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

colors = ["#fd7f6f", "#7eb0d5", "#b2e061", "#bd7ebe", "#ffb55a", "#ffee65", "#beb9db", "#fdcce5", "#8bd3c7"] + ["#ea5545", "#f46a9b", "#ef9b20", "#edbf33", "#ede15b", "#bdcf32", "#87bc45", "#27aeef", "#b33dc6"]
 # Spring Pastel + Retro Metro

all_business = ['WSA와인아카데미', 'Wine Folly', 'after9', 'winebook_official', '나라셀라 • NARA CELLAR', '와인21 @wine21.com', '와인비전 Winevision', '주류학개론', '퍼플독ㅣPurpleDog', '달리 Dali 주류 스마트오더', '루얼 잠실새내 와인샵&테이스팅룸', '와인소셜', '와프너 | wapener', '테이스팅 와인샵 와인도어', '와인인_WINEIN.(Wine inspiration)']

business_colormap = dict(zip(all_business, colors[:len(all_business)-1]))
    

def Bar(df:pd.DataFrame, x:str, y:str, group:str, text = None, title:str = '', colormap = None, range_slider:bool = False, barmode = 'relative', facet_col = None):
    texttemplate = "%{text}"
    if text:
        if df[text].dtype == float:
            texttemplate = "%{text:.2f}"
        if '수' in text:
            texttemplate = "%{text:.0f}"

    fig = px.bar(data_frame = df, barmode = barmode, text = text, x = x, y = y , color = group , title = title, hover_data = [group, y, x], color_discrete_map = colormap, width = 1500,  height = 500, opacity =0.7, facet_col = facet_col)
    # fig = px.bar(data_frame = df, text = group, text_auto = text_auto, x = x, y = y , color = group , title = title, hover_data = [group, y, x], color_discrete_map = colormap,  width = 1000, opacity =0.7)
    fig.update_traces(texttemplate=texttemplate, textangle = 90, textposition = 'auto')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')


    fig.update_layout(
        xaxis=dict(
            title = x,
            showline=True,
            showgrid=False,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=2,
            ticks='outside',
            tickfont=dict(
                family='Arial',
                size=12,
                color='rgb(82, 82, 82)',
            ),
            rangeslider_visible= range_slider
        ),
        yaxis=dict(
            title = y,
            showgrid=False,
            zeroline=False,
            showline=False,
            showticklabels=True,
        ),
        autosize=True,
        margin=dict(
            autoexpand=True,
            l=100,
            r=20,
            t=110,
        ),
        
        showlegend=False,
        plot_bgcolor='white'
    )
    
    fig.update_layout(legend=dict(x = 0, y= max(- (1 +  1.5 * range_slider), -2), traceorder='reversed', font_size=12, orientation = 'h'))
    
    
    return fig
