import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

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

def translate(column_or_index):
    trans_dict = {'rank': '순위', 'name': '이름', 'followers' : '팔로워', 'follows': '팔로우', 'media': '게시물', 'like': '좋아요', 'comments': '댓글', 'diff': '증감(수)', 'pct_change': '증감(%)', 'count': '수', 'ratio': '당', 'date': '날짜', 'engagementrate': '참여도',
    'carousel': '캐러셀', 'album': '앨범', 'image': '이미지', 'video': '영상', 'engagement': '참여 수', 'type': '종류', 'timestamp': '업로드 시간', 'permalink': '게시물 주소', 'caption': '캡션'}
    trans_names = []
    for name in column_or_index:
        name = name.lower()
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
        trans_names.append(trans_words.strip())
    return trans_names

def date_format(datetime, format = 'kor'):
    if format == 'kor':
        strf = '%Y년 %m월 %d일'
    else:
        strf = f"%Y{format}%m{format}%d"

    if isinstance(datetime, pd.Series) or isinstance(datetime, pd.DataFrame):
        return datetime.dt.strftime(strf)
    else:
        return datetime.strftime(strf)

def get_week_num(date, ref_weekday = 0):

    target_day = pd.to_datetime(date)
    year = target_day.year
    month = target_day.month
    first_day = pd.to_datetime(datetime(year, month, 1, tzinfo = timezone(timedelta(hours = 9))))
    n = 0
    for day in pd.date_range(start = first_day, end = target_day):
        if day.day_of_week == ref_weekday:
            n += 1
    return f'{year}년 {month}월 {n}주차'

def show_glossary():
    content = '''
    ##### 1. 기본 수치
    ###### 1) 순위 rank
    집계하는 전체 계정의 일간 팔로워 수 내림차순
    ###### 2) 팔로워 followers count
    해당 계정을 팔로우 하는 계정 수
    ###### 3) 팔로우 follows count
    해당 계정이 팔로우 하는 계정 수
    ###### 4) 게시물 수 media count
    해당 계정의 게시물 수
    ###### 5) 좋아요 수 like count
    게시물에 달린 좋아요 수 합계
    ###### 6) 댓글 수 comments count
    게시물에 달린 댓글 수 합계
    ###### 7) 참여 engagement
    좋아요 수와 댓글 수의 합계
    
    ##### 2. 복합 수치
    ###### 1) 증감(수) change in count
    기준일 대비 수치 변화량
    ###### 2) 증감(%) change in percentage
    기준일 대비 수치 변화량의 백분율(100 * 증감(수) / 기준일 수치)
    ###### 3) 참여도 engagement rate
    팔로워 수 대비 참여 백분율(100 * 참여 / 팔로워 수)
    ###### 4) 게시물 당 OO OO-media count ratio
    게시물 하나 당 OO 수(OO 수 / 게시물 수)
    '''
    st.markdown(content)
    
        