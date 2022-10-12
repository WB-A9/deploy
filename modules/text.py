import streamlit as st
import pandas as pd

def st_header(text:str, num = 1):
    return st.markdown(f"{'#' * num} {text}")

def inc_dec(number):
    if number > 0:
        text =  '증가하였습니다.'
    elif number < 0:
        text = '감소하였습니다.'
    else:
        text = '로 변동이 없었습니다.'
    return text

def translate(columns):
    trans_dict = {'rank': '순위', 'name': '이름', 'followers' : '팔로워', 'follows': '팔로우', 'media': '게시물', 'like': '좋아요', 'comments': '댓글', 'diff': '증감(수)', 'pct_change': '증감(%)', 'count': '수', 'ratio': '당', 'date': '날짜', 'engagementrate': '참여도'}
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

def date_format(datetime, format = 'kor'):
    if format == 'kor':
        strf = '%Y년 %m월 %d일'
    else:
        strf = f"%Y{format}%m{format}%d"

    if isinstance(datetime, pd.Series) or isinstance(datetime, pd.DataFrame):
        return datetime.dt.strftime(strf)
    else:
        return datetime.strftime(strf)