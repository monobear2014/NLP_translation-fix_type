import streamlit as st
import langcodes #đổi mã ngôn ngữ sang tên, e.g: "en" -> English,"fr"->French 
from deep_translator import GoogleTranslator #deep_translator : dịch văn bản
from langdetect import DetectorFactory, LangDetectExpextion, detect #langdetect : nhân diện ngôn ngữ
from nltk.tokenize import TreebankWordTokenizer, wordpunct_tokenize #nltk :Tách từ/ xử lí văn bản
from spellchecker import SpellChecker #kiểm tra chính tả
 
 #Đoạn văn bản ngắn dễ trả về kết qua khác nhau qua các lần chạy nên ta cần dùng
DetectorFactory.seed = 0 #để cố định random seed.(Giúp kết quả nhất quán)
#nếu ko nhất quán thì sao? vì DetectorFactory là thử viện nhận diện ngôn ngữ(en , vn, fr...)
#ví dụ print("hi") trả về là en(English) nhưng có thể khi reRun lại trả về vn(Việt nam).
MIN_INPUT_LENGTH = 3#biến dev tự đặt. Chỉ xử lí chuỗi nhập vào ít nhất 3 kí tự
#do các mô hình thường kém với câu ít kí tự

SPELL_LANGS = {
    "en","es","fr","pt","de",
    "ru","ar","eu","lv","nl"
}#tập hợp 1 vài mã ngôn ngữ được Python hỗ trợ 

TARGET_LANGS = { 
 "Vietnamese": "vi",
 "English": "en",
 "French": "fr",
 "Japanese": "ja",
 "Chinese": "zh-CN",
 "Korean": "ko",
 "Spanish": "es",
 "German": "de"
}# chỉ càn nhìn ta cũng thấy được rằng đây là 1 dictionary

EXAMPLES_T = [ #các câu mẫu cho cho chức năng dịch
 "Every morning, I drink a cup of coffee.",
 "Bonjour, comment allez-vous?",
 "Xin chao, hom nay troi dep qua.",
]

EXAMPLES_S = [ #cũng là các câu mẫu nhưng sai chính tả =))
 "Yesturday, I recieveed a mesage from my freind.",
 "Definately a great oppurtunity.",
 "Je voudraiis allerr au marchee"
]
# lí do tại sao chỉ dùng vài câu mẫu mà mô hình vẫn hiểu đc câu khác
#ngoài cẫu mẫu trên vì:
#1. Đó không phải là  dữ liệu để mô hình train/test/validation
#2. Chỉ là câu mẫu để ng dùng bấm thử trong giao diện streamlit
#3. Mô hình thật sự học ở thư viện langdetect


### xây dựng hàm nhận hỗ trợ dịch văn bản

@st.cache_resource(show_spinner=False)
# dấu "@" : gắn thêm chức năng(phía sau dấu @) cho hàm
# dùng cache vì mỗi lần reRun thì sẽ k phải load lại toàn bộ dữ liẹu
# mà chỉ load lại dữ liệu mới được thêm/nhập vào
def get_spellchecker(code):
    return SpellChecker(language = code)

def language_name(code):
    try:
        return langcodes.Language.get(code).display_name()
    except:
        return code or "Unknown"
#hàm chuyển mã ngôn ngữ. eg: gọi hàm language_name("en") -> Ouput: English
def detect_language(raw):
    try:
        return detect(raw)
    except LangDetectException:
        return None
#hàm nhận diện ngôn ngữ


### xây dựng hàm sửa lỗi chính tả

def fix_type(text,code):
    spell = get_spellchecker(code)
    tokens = wordpunct_tokenize(text)#tách câu thành các từ(token)
    fixed = []#tạo danh sách chứa két quả sửa

    #dùng for để duyệt từng token sau khi tách
    #isalpha() : kiếm tra phải chữ cái không
    for token in tokens:
        if token.isalpha() and len(token) >1:
            suggestion = spell.correction(token.lower()) or token#tìm từ đúng
            suggestion = suggestion.title() if token.istitle() else suggestion
            suggestion = suggestion.upper() if token.isupper() else suggestion
            #2 lệnh trên dùng giữ nguyên chữ hoa chữ thường
            fixed.append(suggestion)#dùng .append() để thêm vào list đã tạo ban đầu 
        else:#nếu ko phải từ thì giữ nguyên rồi thêm vào list
            fixed.append(token)
    return TreebankWordDetokenizer().detokenize(fixed), fixed != tokens
    #return để trả về câu đã sửa

### Pipeline dịch văn bản

def run_translation(text, target_code):
    raw = text.strip()#strip để loại bỏ các kí là khoảng trắng, tab, xuống dòng
    if len(raw) < MIN_INPUT_LENGTH  : #MIN_INPUT_LENGTH = 3 đã tạo ở trên
        return {"ok": False, "error": f"Nhập tối thiểu {MIN_INPUT_LENGTH} ký tự."}
    
    #tạo biến source để nhận xác định ngôn ngữ gốc của văn bản đc nhập vào
    #hay còn gọi là ngôn ngữ cần dịch
    source = detect_language(raw)
    if source is None :
        return {"ok":False, "error": "Không nhận diện được ngôn ngữ."}
    
    if source == target_code:#nếu ngôn ngữ cần dịch == ngôn ngữ dịch
        return {
            "ok" :True,
            "source": language_name(source),
            "target": language_name(target_code),
            "translated": raw,
            "note" :"Câu đã ở ngôn ngữ dịch, khônc cần dịch"
        }
    
    try:
        translated = GoogleTranslator(
            source = source,
            target = target_code
        ).translate(raw)
        # ví dụ source = "vn" , target = "en" --> dịch từ việt sang english
    except Exception as e:
        return {"ok":False,"error":f"Lỗi dịch {e}"}
#try-except ở đây là nếu bình thường thì sẽ dịch ngược lại sai sẽ chuyển
#qua except trả về thông báo lỗi








