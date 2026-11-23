"""ARIRANG — Streamlit-based Korean traditional music creation web prototype."""
import os
import streamlit as st
from engine import INSTRUMENTS, MOODS, VOCAL_GENDERS, VOCAL_DELIVERIES, build_prompt
from ace_client import AceClient, AceStepError
from storage import register, authenticate, save_track, list_tracks, get_track, delete_track

st.set_page_config(page_title='ARIRANG | 판소리 AI', page_icon='🎵', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=Noto+Serif+KR:wght@500;700&display=swap');
:root {--jade:#1f7265;--jade-light:#eaf5f1;--ink:#1c2b26;--muted:#758780;--border:#e6ece8;}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"] {background:#fff!important;color:var(--ink)!important;font-family:'Noto Sans KR',sans-serif!important;}
[data-testid="stHeader"] {background:rgba(255,255,255,.93)!important;}
[data-testid="stDecoration"] {display:none!important;}
[data-testid="stSidebar"] {background:#fff!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebarUserContent"] {padding:1rem .9rem 2rem!important;}
.block-container {max-width:1460px!important;padding:1.7rem 2.5rem 3rem!important;}
[data-testid="stVerticalBlockBorderWrapper"]>div {border-radius:16px!important;border-color:var(--border)!important;box-shadow:0 1px 10px rgba(12,49,36,.025)!important;}
[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input,[data-baseweb="select"]>div {border-color:#dce7e1!important;background:#fff!important;border-radius:10px!important;color:#23382e!important;}
.stButton>button,.stDownloadButton>button {border-radius:10px!important;min-height:2.7rem!important;font-weight:600!important;}
.stButton>button[kind="primary"] {background:var(--jade)!important;color:white!important;border:1px solid var(--jade)!important;}
.stButton>button:not([kind="primary"]) {border:1px solid #e0e9e4!important;color:#37564b!important;background:#fff!important;}
[data-testid="stSidebar"] .stButton>button {border:0!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;padding-left:16px!important;}
[data-testid="stSidebar"] .stButton>button[kind="primary"] {background:#e8f4ef!important;color:#1b6c5e!important;}
.hero {padding:17px 0 20px}.tag{font-size:11px;letter-spacing:.14em;color:var(--jade);font-weight:800}.hero h1{font-family:'Noto Serif KR',serif;font-size:30px;margin:4px 0 4px}.hero p{color:var(--muted);font-size:13px;margin:0}
.panel-title {font-size:18px;font-weight:800;margin-bottom:12px}.tiny {font-size:12px;color:var(--muted);line-height:1.7}
.welcome {padding:25px 0 15px}.welcome h2{font-family:'Noto Serif KR',serif;font-size:29px;color:var(--ink)}.welcome p{color:var(--muted);font-size:14px;line-height:1.85}
.stat {padding:17px 20px;border:1px solid var(--border);border-radius:14px;background:#fcfefd;font-size:14px;color:#435c50;min-height:90px}.stat b{font-size:24px;color:#1f7265;display:block}
.mountain-wrap svg{width:100%;height:auto;max-height:210px}.empty-state {text-align:center;padding:34px 10px 18px}.empty-state h3{font-family:'Noto Serif KR',serif;margin:8px 0}.empty-state p{font-size:12px;color:#8a9890}
.footer {padding-top:26px;color:#9eaca4;font-size:11px}
@media(max-width:850px){.block-container{padding:1rem!important}.hero h1{font-size:24px}}

/* ARIRANG light theme: Streamlit's dark theme must not make labels white. */
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"],
[data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] p,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] li,
[data-testid="stAppViewContainer"] [data-testid="stRadio"] label,
[data-testid="stAppViewContainer"] [data-testid="stRadio"] p,
[data-testid="stAppViewContainer"] [data-testid="stCheckbox"] label,
[data-testid="stAppViewContainer"] [data-testid="stCheckbox"] p,
[data-testid="stAppViewContainer"] [data-testid="stToggle"] label,
[data-testid="stAppViewContainer"] [data-testid="stSelectbox"] label,
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary,
[data-testid="stAppViewContainer"] [data-testid="stExpander"] summary p,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color:#23352e !important;
}
[data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] p,
[data-testid="stAppViewContainer"] [data-testid="stTextArea"] small,
[data-testid="stAppViewContainer"] [data-testid="stTextInput"] small {
    color:#65756e !important;
}
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea,
[data-baseweb="select"] input,
[data-baseweb="select"] [role="combobox"],
[data-testid="stSelectbox"] span,
[data-testid="stNumberInput"] input {
    color:#1c2b26 !important;
    background-color:#fff !important;
    -webkit-text-fill-color:#1c2b26 !important;
}
[data-testid="stTextArea"] textarea::placeholder,
[data-testid="stTextInput"] input::placeholder,
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder {
    color:#78867f !important;
    opacity:1 !important;
    -webkit-text-fill-color:#78867f !important;
}
[data-testid="stExpander"] details,
[data-testid="stExpander"] summary,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background-color:#fff !important;
}
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"] h3 {
    color:#172b23 !important;
}
/* Preserve readable white text on the green primary button. */
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span,
.stDownloadButton > button[kind="primary"] p {
    color:#fff !important;
}
</style>''', unsafe_allow_html=True)

# Original illustrated landscape motif, not a screenshot of another product.
MOUNTAINS = '''<div class="mountain-wrap"><svg viewBox="0 0 600 230" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="한국의 산과 정자 풍경">
<defs><linearGradient id="ridge1" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#b9d0c9"/><stop offset="1" stop-color="#f9fdfb"/></linearGradient><linearGradient id="ridge2" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#d9e6df"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>
<circle cx="300" cy="67" r="34" fill="#eed9a5" opacity=".82"/>
<path d="M0 182 Q49 144 91 155 Q118 159 163 114 Q193 80 224 119 Q253 148 290 115 Q327 65 369 113 Q411 156 458 124 Q503 96 542 136 Q575 154 600 143 L600 230 L0 230Z" fill="url(#ridge1)"/>
<path d="M0 201 Q80 167 130 182 Q175 193 238 152 Q288 126 333 169 Q389 192 432 163 Q485 141 527 171 Q560 186 600 172 L600 230 L0 230Z" fill="url(#ridge2)"/>
<g stroke="#466e61" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M400 153 Q419 150 436 136 Q452 151 471 153 L400 153"/><path d="M412 159 L412 183 M461 159 L461 183 M426 160 L426 181 M447 160 L447 181 M406 160 L465 160 M406 184 L465 184"/></g>
<path d="M16 105 Q60 86 97 104 M502 81 Q544 61 579 85" stroke="#e0be76" stroke-width="2" fill="none" stroke-linecap="round" opacity=".7"/>
</svg></div>'''

for key, default in {'page':'홈','user_id':None,'username':None,'task_id':None,'audio':None,'submitted_prompt':None,'submitted_lyrics':'','saved_audio_signature':None}.items():
    if key not in st.session_state: st.session_state[key]=default


def nav(page):
    st.session_state.page=page
    st.rerun()


def login_panel():
    st.markdown('<div class="panel-title">ARIRANG 계정</div><div class="tiny">로그인하면 생성한 음악을 내 라이브러리에 저장할 수 있어요.</div>', unsafe_allow_html=True)
    tab1,tab2=st.tabs(['로그인','회원가입'])
    with tab1:
        with st.form('login_form'):
            u=st.text_input('아이디',key='signin_name')
            p=st.text_input('비밀번호',type='password',key='signin_pw')
            submit=st.form_submit_button('로그인',type='primary',use_container_width=True)
        if submit:
            uid=authenticate(u,p)
            if uid is None: st.error('아이디 또는 비밀번호를 확인해 주세요.')
            else:
                st.session_state.user_id=uid
                st.session_state.username=u.strip().lower()
                st.success('로그인되었습니다.')
                st.rerun()
    with tab2:
        with st.form('signup_form'):
            u=st.text_input('새 아이디 (영문 소문자·숫자·_ 3~24자)')
            p=st.text_input('새 비밀번호 (8자 이상)',type='password')
            p2=st.text_input('비밀번호 확인',type='password')
            submit=st.form_submit_button('회원가입',use_container_width=True)
        if submit:
            if p!=p2: st.error('비밀번호가 일치하지 않습니다.')
            else:
                ok,msg=register(u,p)
                (st.success if ok else st.error)(msg)
    st.caption('이 로그인은 학교 시연용 로컬 계정입니다. 이메일 인증·비밀번호 재설정·온라인 서버용 보안 기능은 포함되지 않습니다.')

with st.sidebar:
    st.image('arirang_logo.png',width=195)
    st.markdown('<div class="tiny" style="text-align:center;margin-top:-12px;margin-bottom:17px">우리의 소리를 새롭게</div>',unsafe_allow_html=True)
    if st.session_state.user_id is None:
        if st.button('♙  로그인 / 회원가입',use_container_width=True,type='primary' if st.session_state.page=='로그인' else 'secondary'):
            nav('로그인')
    else:
        st.caption('● '+st.session_state.username+' 님')
        if st.button('로그아웃',use_container_width=True):
            st.session_state.user_id=None
            st.session_state.username=None
            nav('홈')
    st.divider()
    for page,label in [('홈','⌂   홈'),('음악 만들기','♫   새로운 노래 만들기'),('라이브러리','▤   라이브러리')]:
        if st.button(label,key='nav_'+page,use_container_width=True,type='primary' if st.session_state.page==page else 'secondary'):
            nav(page)
    st.markdown('<div style="height:25px"></div>',unsafe_allow_html=True)
    st.markdown(MOUNTAINS,unsafe_allow_html=True)
    st.caption('ARIRANG · Pansori music research prototype')

page=st.session_state.page
if page=='홈':
    st.markdown('<div class="welcome"><div class="tag">ARIRANG · KOREAN MUSIC AI</div><h2>우리의 소리, 새로운 가능성.</h2><p>판소리의 고유한 표현을 바탕으로 가사와 음악 스타일을 조합해 보세요.<br>ACE-Step 기반 판소리 특화 음악 생성 실험 공간입니다.</p></div>',unsafe_allow_html=True)
    st.markdown(MOUNTAINS,unsafe_allow_html=True)
    a,b,c=st.columns(3)
    with a: st.markdown('<div class="stat"><b>01</b>가사 직접 작성</div>',unsafe_allow_html=True)
    with b: st.markdown('<div class="stat"><b>02</b>국악기·창법 선택</div>',unsafe_allow_html=True)
    with c: st.markdown('<div class="stat"><b>03</b>생성 및 보관</div>',unsafe_allow_html=True)
    st.write('')
    if st.button('♫  음악 만들러 가기',type='primary',use_container_width=True): nav('음악 만들기')
    st.info('음악 생성은 별도 ACE-Step 실행 서버를 연결했을 때만 작동합니다. 서버 없이도 화면·프롬프트·회원가입 기능을 시연할 수 있습니다.')
elif page=='로그인':
    st.markdown('<div class="hero"><div class="tag">ACCOUNT</div><h1>ARIRANG에 오신 것을 환영합니다.</h1></div>',unsafe_allow_html=True)
    login_panel()
elif page=='라이브러리':
    st.markdown('<div class="hero"><div class="tag">MY MUSIC</div><h1>나의 라이브러리</h1><p>저장된 음악을 다시 듣거나 다운로드하세요.</p></div>',unsafe_allow_html=True)
    if st.session_state.user_id is None:
        st.info('라이브러리를 사용하려면 로그인이 필요해요.')
        if st.button('로그인하러 가기',type='primary'): nav('로그인')
    else:
        items=list_tracks(st.session_state.user_id)
        if not items:
            st.markdown(MOUNTAINS,unsafe_allow_html=True)
            st.markdown('<div class="empty-state"><h3>아직 저장한 음악이 없어요.</h3><p>음악 만들기에서 생성한 곡을 저장해 보세요.</p></div>',unsafe_allow_html=True)
            if st.button('새 노래 만들기',type='primary'): nav('음악 만들기')
        for tid,title,created,size in items:
            with st.container(border=True):
                st.markdown(f'**🎵 {title}**')
                st.caption('저장: '+created[:16].replace('T',' ')+' UTC · '+str(round(size/1024))+' KB')
                if st.button('열기 / 닫기',key=f'open_{tid}'):
                    k=f'show_{tid}';st.session_state[k]=not st.session_state.get(k,False)
                if st.session_state.get(f'show_{tid}',False):
                    record=get_track(st.session_state.user_id,tid)
                    if record:
                        st.audio(record[4],format='audio/mpeg')
                        st.download_button('MP3 다운로드',data=record[4],file_name=f'ARIRANG_{tid}.mp3',mime='audio/mpeg',key=f'dl_{tid}')
                        with st.expander('생성 프롬프트 / 가사'):
                            st.code(record[2],language='text')
                            st.text(record[3])
                        if st.button('이 음악 삭제',key=f'delete_{tid}'):
                            delete_track(st.session_state.user_id,tid)
                            st.rerun()
elif page=='음악 만들기':
    st.markdown('<div class="hero"><div class="tag">CREATE STUDIO</div><h1>새로운 노래 만들기</h1><p>가사, 분위기, 창법, 국악기를 선택해서 나만의 판소리를 만들어 보세요.</p></div>',unsafe_allow_html=True)
    left,right=st.columns([1.05,.95],gap='large')
    with left:
        with st.container(border=True):
            st.markdown('**가사**')
            lyrics=st.text_area('가사 입력',value='달아 달아 밝은 달아\n내 마음을 비추어라\n떠나간 임의 발자취\n어디에서 찾으리오',height=150,max_chars=2500,label_visibility='collapsed',placeholder='가사를 입력해 주세요')
            mode=st.radio('생성 유형',['판소리 창 (보컬 포함)','국악 기악 (보컬 없음)'],horizontal=True)
            vocal=mode.startswith('판소리')
        with st.container(border=True):
            st.markdown('**음악 스타일**')
            custom_style=st.text_area('자유 스타일 입력',height=100,max_chars=1200,placeholder='예: 여성 보컬, 애절한 계면조, 느린 진양조, 대금의 서정적인 선율')
            mood=st.selectbox('기본 분위기',['직접 설정']+list(MOODS.keys()))
        with st.container(border=True):
            st.markdown('**보컬 선택**')
            vocal_gender=st.radio('보컬 성별',list(VOCAL_GENDERS.keys()),horizontal=True,disabled=not vocal)
            vocal_delivery=st.selectbox('보컬 표현 방식',list(VOCAL_DELIVERIES.keys()),disabled=not vocal)
        with st.expander('⚙ 고급 옵션 · 악기 및 장단'):
            traditional=st.toggle('정통 판소리 · 북만 사용',value=False)
            st.markdown('**반주 악기**')
            ins=[];cols=st.columns(2)
            for idx,name in enumerate(INSTRUMENTS):
                with cols[idx%2]:
                    picked=st.checkbox(name,value=name in ['북','장구'],disabled=traditional,key=f'inst_{name}')
                    if picked: ins.append(name)
            if traditional: ins=['북']
            duration=st.slider('곡 길이 (초)',10,90,30,5)
            extra=st.text_input('추가 요청 (선택)')
        with st.expander('🔌 ACE-Step 서버 연결'):
            try:
                cfg=st.secrets.get('ACESTEP_API_URL',os.getenv('ACESTEP_API_URL',''))
                token=st.secrets.get('ACESTEP_API_KEY',os.getenv('ACESTEP_API_KEY',''))
            except Exception:
                cfg=os.getenv('ACESTEP_API_URL','');token=os.getenv('ACESTEP_API_KEY','')
            url=st.text_input('ACE-Step API 주소',value=cfg,placeholder='http://localhost:8001')
            demo=st.toggle('시연 모드',value=not bool(url))
            if demo: st.caption('시연 모드에서는 음악이 생성되지 않아요. GPU 서버 연결이 필요합니다.')
        if not ins: st.warning('악기를 하나 이상 선택해 주세요.')
        prompt=build_prompt(mood,ins or ['북'],vocal=vocal,extra=extra,custom_style=custom_style,vocal_gender=vocal_gender,vocal_delivery=vocal_delivery)
        with st.expander('ARIRANG 판소리 프롬프트 미리보기'):
            st.code(prompt,language='text')
        generate=st.button('♫  음악 만들기',type='primary',use_container_width=True,disabled=not ins or (vocal and not lyrics.strip()))
    with right:
        st.markdown('<div class="panel-title">내 작업 공간</div>',unsafe_allow_html=True)
        if generate:
            st.session_state.audio=None
            st.session_state.task_id=None
            st.session_state.submitted_prompt=prompt
            st.session_state.submitted_lyrics=lyrics.strip()
            st.session_state.saved_audio_signature=None
            if demo: st.info('시연용 프롬프트 생성 완료! 실제 음원 생성에는 ACE-Step 서버가 필요해요.')
            elif not url.strip(): st.error('ACE-Step 서버 주소가 없어요.')
            else:
                try:
                    with st.spinner('음악 생성 요청 중…'):
                        st.session_state.task_id=AceClient(url,token).generate(prompt,lyrics.strip(),duration,vocal)
                    st.success('생성 요청이 접수됐어요.')
                except AceStepError as exc: st.error(str(exc))
        if st.session_state.task_id and not st.session_state.audio and not demo:
            st.info('생성 중입니다. 상태 확인을 눌러 주세요.')
            if st.button('↻ 생성 상태 확인',use_container_width=True):
                try:
                    client=AceClient(url,token)
                    result=client.query(st.session_state.task_id)
                    if result['status']==0: st.info('아직 생성 중입니다.')
                    elif result['status']==2: st.error('생성 실패: '+str(result.get('error') or '서버 로그 확인'))
                    else:
                        for item in result.get('files',[]):
                            if item.get('file'):
                                st.session_state.audio=client.fetch_audio(item['file']);break
                        if st.session_state.audio: st.success('음악 생성 완료!')
                        else: st.error('오디오 파일을 찾지 못했습니다.')
                except AceStepError as exc: st.error(str(exc))
        if st.session_state.audio:
            st.markdown('**🎵 생성된 음악**')
            st.audio(st.session_state.audio,format='audio/mpeg')
            st.download_button('MP3 다운로드',data=st.session_state.audio,file_name='ARIRANG_pansori.mp3',mime='audio/mpeg',use_container_width=True)
            if st.session_state.user_id is None:
                st.caption('로그인하면 음악을 라이브러리에 보관할 수 있습니다.')
                if st.button('로그인해서 저장하기'): nav('로그인')
            else:
                title=st.text_input('음악 제목',value='나의 판소리',key='save_title')
                sig=(st.session_state.task_id,hash(st.session_state.audio))
                if st.session_state.saved_audio_signature==sig: st.success('라이브러리에 저장했어요.')
                elif st.button('라이브러리에 저장',type='primary'):
                    try:
                        save_track(st.session_state.user_id,title,st.session_state.submitted_prompt or '',st.session_state.submitted_lyrics,st.session_state.audio)
                        st.session_state.saved_audio_signature=sig
                        st.success('저장 완료! 왼쪽 라이브러리에서 확인해 보세요.')
                    except ValueError as exc: st.error(str(exc))
        elif not st.session_state.task_id:
            st.markdown(MOUNTAINS,unsafe_allow_html=True)
            st.markdown('<div class="empty-state"><h3>아직 생성한 음악이 없어요.</h3><p>가사와 스타일을 입력하고 새로운 음악을 만들어 보세요.</p></div>',unsafe_allow_html=True)
        st.caption('실제 악기 음색·보컬 성별은 프롬프트에 기반한 요청이며 정확한 구현을 보장하지 않습니다.')

st.markdown('<div class="footer">ARIRANG · 판소리 AI 연구 시제품 · Streamlit + ACE-Step · 2026</div>',unsafe_allow_html=True)
