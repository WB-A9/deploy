import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

all_business = ['WSA와인아카데미', 'Wine Folly', 'after9', 'winebook_official', '나라셀라 • NARA CELLAR', '와인21 @wine21.com', '와인비전 Winevision', '주류학개론', '퍼플독ㅣPurpleDog', '달리 Dali 주류 스마트오더', '루얼 잠실새내 와인샵&테이스팅룸', '와인소셜', '와프너 | wapener', '테이스팅 와인샵 와인도어']

business_colormap = dict(zip(all_business,
 ['#f7b32b', '#08605f', '#8e4162', '#b3cdd1', '#c7f0bd', '#bbe5ed', '#9f4a54', '#fff07c', '#ff7f11', '#ff1b1c', '#edc9ff', '#f2b79f', '#0c6291', '#231123']))

def Bar(df:pd.DataFrame, x:str, y:str, group:str, title:str = '', text_auto = False, colormap = None, range_slider:bool = False):
    
    fig = px.bar(data_frame = df, barmode = 'group', text = group, text_auto = text_auto, x = x, y = y , color = group , title = title, hover_data = [group, y, x], color_discrete_map = colormap,  width = 800, opacity =0.7)
    fig.update_traces(texttemplate="%{text}", textangle = 90, textposition = 'inside')
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
        showlegend=True,
        plot_bgcolor='white'
    )
    
    fig.update_layout(legend=dict(x = 0, y= - (0.5 +  1.5 * range_slider), traceorder='reversed', font_size=10, orientation = 'h'))
    
    
    return fig
