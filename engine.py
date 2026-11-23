"""ARIRANG: rule-based Korean traditional music prompt builder."""
MOODS = {
    '애절함 · 그리움': ('solemn longing and restrained sorrow', 'Gyemyeonjo-inspired expression', 'slow, expansive Jinyangjo-inspired pulse'),
    '장엄함 · 결의': ('majestic determination and dramatic resolve', 'Ujo-inspired strong vocal delivery', 'measured Jungmori-inspired pulse'),
    '흥겨움 · 기쁨': ('playful joy and lively theatrical storytelling', 'bright Pyeongjo-inspired phrases', 'energetic Jajinmori-inspired pulse'),
    '차분함 · 서정': ('serene contemplation and tenderness', 'calm Pyeongjo-inspired expression', 'gentle Jungmori-inspired pulse'),
}
VOCAL_GENDERS = {
    '자동 (AI 선택)': 'A solo Korean pansori singer, voice gender unspecified.',
    '여성 보컬': 'A solo female Korean pansori singer with a natural female vocal timbre.',
    '남성 보컬': 'A solo male Korean pansori singer with a natural male vocal timbre.',
}
VOCAL_DELIVERIES = {
    '기본 판소리': 'Traditional pansori vocal delivery, with well-controlled seongeum and sigimsae.',
    '힘 있고 웅장하게': 'Resonant, powerful traditional pansori projection, never modern pop belting.',
    '절제되고 담담하게': 'Restrained and intimate traditional pansori storytelling, avoiding exaggerated ornaments.',
    '섬세하고 애절하게': 'Tender, emotionally nuanced pansori phrasing with subtle traditional ornaments.',
}
INSTRUMENTS = {
    '북': 'Korean pansori buk barrel drum, responding to the singer like a gosu',
    '장구': 'Korean janggu hourglass drum, supporting the jangdan',
    '징': 'Korean jing large gong, sparse resonant accents',
    '꽹과리': 'Korean kkwaenggwari small gong, restrained bright punctuation',
    '대금': 'Korean daegeum large bamboo transverse flute',
    '소금': 'Korean sogeum small bamboo flute',
    '가야금': 'Korean gayageum plucked zither',
    '거문고': 'Korean geomungo plucked six-string zither',
}

def build_prompt(mood, instruments, vocal=True, extra='', custom_style='', vocal_gender='자동 (AI 선택)', vocal_delivery='기본 판소리'):
    if mood != '직접 설정' and mood not in MOODS:
        raise ValueError('Unknown mood')
    if vocal and vocal_gender not in VOCAL_GENDERS:
        raise ValueError('Unknown vocal gender')
    if vocal and vocal_delivery not in VOCAL_DELIVERIES:
        raise ValueError('Unknown vocal delivery')
    if not instruments or any(i not in INSTRUMENTS for i in instruments):
        raise ValueError('Choose at least one valid instrument')
    parts = ['Authentic Korean traditional pansori-inspired acoustic performance; specifically Korean, not generic East Asian music.']
    if mood in MOODS:
        feeling, jo, rhythm = MOODS[mood]
        parts.append(f'Mood: {feeling}. Musical expression: {jo}. Rhythm: {rhythm}.')
    if custom_style.strip():
        parts.append('User-selected musical style and direction (prioritize this when it conflicts with the mood preset): ' + custom_style.strip()[:1200])
    if vocal:
        parts += [VOCAL_GENDERS[vocal_gender], VOCAL_DELIVERIES[vocal_delivery], 'Expressive seongeum, controlled traditional sigimsae, clear Korean diction, story-driven phrasing, aniri and chang expression. Natural vocal projection without pop belting or exaggerated ornamentation.']
    else:
        parts += ['Instrumental only, no voice, no chanting, no lyrics.']
    parts += [
        'ONLY these Korean acoustic instruments: ' + '; '.join(INSTRUMENTS[i] for i in instruments) + '.',
        'Allow open space around the voice; avoid over-arrangement. No Chinese or Japanese instruments, Western drum kits, pop, EDM, synths, cinematic strings, or artificial vocal effects.',
    ]
    if extra.strip():
        parts += ['Additional direction: ' + extra.strip()[:450]]
    return '\n'.join(parts)
