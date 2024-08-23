import os

# Define punctuation symbols and special symbols
PUNCTUATION = ["!", "?", "…", ",", ".", "-"]
PU_SYMBOLS = PUNCTUATION + ["SP", "SP2", "SP3", "UNK"]
PAD = "_"

PUNCTUATION_REP_MAP = {
    "：": ",",
    "；": ",",
    "，": ",",
    "。": ".",
    "！": "!",
    "？": "?",
    "\n": ".",
    "·": ",",
    "、": ",",
    "...": "…",
    "$": ".",
    "/": ",",
    "—": "-",
    "~": "…",
    "～":"…",
}

# Define consonants, vowels (with and without tones)
C_SYMBOLS = [
    "AA", "EE", "OO", "b", "c", "ch", "d", "f", "g", "h", "j", "k", "l", "m", 
    "n", "p", "q", "r", "s", "sh", "t", "w", "x", "y", "z", "zh"
]

V_SYMBOLS = [
    f"{vowel}{tone}" 
    for vowel in ["E", "En", "a", "ai", "an", "ang", "ao", "e", "ei", "en", 
                  "eng", "er", "i", "i0", "ia", "ian", "iang", "iao", "ie", 
                  "in", "ing", "iong", "ir", "iu", "o", "ong", "ou", "u", 
                  "ua", "uai", "uan", "uang", "ui", "un", "uo", "v", "van", 
                  "ve", "vn"]
    for tone in range(1, 6)
]

V_SYMBOLS_WITHOUT_TONE = [
    "E", "En", "a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "er", 
    "i", "i0", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iong", "ir", 
    "iu", "o", "ong", "ou", "u", "ua", "uai", "uan", "uang", "ui", "un", 
    "uo", "v", "van", "ve", "vn"
]

# Define Japanese symbols
JA_SYMBOLS = [
    "I", "N", "U", "a", "b", "by", "ch", "cl", "d", "dy", "e", "f", "g", "gy", 
    "h", "hy", "i", "j", "k", "ky", "m", "my", "n", "ny", "o", "p", "py", "r", 
    "ry", "s", "sh", "t", "ts", "u", "v", "w", "y", "z"
]

# Define ARPAbet symbols
ARPA_SYMBOLS = {
    "AH0", "S", "AH1", "EY2", "AE2", "EH0", "OW2", "UH0", "NG", "B", "G", 
    "AY0", "M", "AA0", "F", "AO0", "ER2", "UH1", "IY1", "AH2", "DH", "IY0", 
    "EY1", "IH0", "K", "N", "W", "IY2", "T", "AA1", "ER1", "EH2", "OY0", 
    "UH2", "UW1", "Z", "AW2", "AW1", "V", "UW2", "AA2", "ER", "AW0", "UW0", 
    "R", "OW1", "EH1", "ZH", "AE0", "IH2", "IH", "Y", "JH", "P", "AY1", 
    "EY0", "OY2", "TH", "HH", "D", "ER0", "CH", "AO1", "AE1", "AO2", "OY1", 
    "AY2", "IH1", "OW0", "L", "SH"
}

# Define Korean symbols
KO_SYMBOLS = 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㄲㄸㅃㅆㅉㅏㅓㅗㅜㅡㅣㅐㅔ空停'

# Define Yue (Cantonese) symbols
YUE_SYMBOLS = {
    'Yeot3', 'Yip1', 'Yyu3', 'Yeng4', 'Yut5', 'Yaan5', 'Ym5', 'Yaan6', 
    #... other symbols omitted for brevity
    'Yap5', 'Yik5', 'Yun6', 'Yaam5', 'Yun5', 'Yik3', 'Ya2', 'Yyut6', 
    'Yon4', 'Yk1', 'Yit4', 'Yak6', 'Yaan2', 'Yuk1', 'Yai2', 'Yik2', 
    'Yaat2', 'Yo3', 'Ykw', 'Yn5', 'Yaa', 'Ye5', 'Yu4', 'Yei1', 'Yai3', 
    'Yyun5', 'Yip2', 'Yaau2', 'Yiu5', 'Ym4', 'Yeoi6', 'Yk', 'Ym6', 
    'Yoe1', 'Yeoi3', 'Yon', 'Yuk4', 'Yaai3', 'Yaa4', 'Yot6', 'Yaang1', 
    'Yei4', 'Yek1', 'Yo', 'Yp', 'Yo6', 'Yp4', 'Yan3', 'Yoi', 'Yap3', 
    'Yek3', 'Yim3', 'Yz', 'Yot2', 'Yoi6', 'Yit2', 'Yu5', 'Yaan3', 
    'Yan1', 'Yon5', 'Yp1', 'Yong5', 'Ygw', 'Yak', 'Yat6', 'Ying4', 
    'Yu2', 'Yf', 'Ya4', 'Yon1', 'You4', 'Yik6', 'Yui1', 'Yaat1', 
    'Yeot4', 'Yi2', 'Yaai1', 'Yek5', 'Ym3', 'Yong6', 'You5', 'Yyun1', 
    'Yn1', 'Yo2', 'Yip6', 'Yui3', 'Yaak5', 'Yyun2'
}

