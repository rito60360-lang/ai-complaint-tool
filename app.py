import streamlit as st
import re
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="ECクレーム対応AI Pro", layout="centered")
st.title("🛡️ ECクレーム対応AI（プロ版）")

# 危険ワード
DANGEROUS_WORDS = ["全額返金", "保証します", "責任を負います", "必ず対応"]

# 感情検知（簡易）
def detect_emotion(text):
    if "最悪" in text or "ふざけるな" in text or "怒" in text:
        return "🔴 強い怒り"
    elif "困って" in text or "不満" in text:
        return "🟡 不満"
    else:
        return "🟢 通常"

# 個人情報マスク
def mask_info(text):
    text = re.sub(r'\d{2,4}-\d{2,4}-\d{3,4}', '***-****-****', text)
    text = re.sub(r'\S+@\S+', '***@***.com', text)
    return text

# 入力
shop = st.text_input("ショップ名")
customer = st.text_input("顧客名")
rule = st.text_area("社内ルール（例：返金は7日以内のみ）")

issue = st.selectbox(
    "クレーム内容",
    ["配送遅延", "商品不良", "返品・返金", "注文ミス"]
)

detail = st.text_area("クレーム内容")

# 感情分析
if detail:
    emotion = detect_emotion(detail)
    st.info(f"顧客感情：{emotion}")

# NGチェック
if detail:
    found = [w for w in DANGEROUS_WORDS if w in detail]
    if found:
        st.error(f"⚠️ 危険表現：{', '.join(found)}")

# 生成
if st.button("返信生成"):

    if not shop or not customer or not detail:
        st.warning("入力不足")
    else:
        safe_text = mask_info(detail)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=f"""
あなたはECのカスタマーサポートです。

条件：
・丁寧
・絶対に「全額返金」などの約束は禁止
・会社ルールを守る

ショップ名：{shop}
顧客名：{customer}
ルール：{rule}
クレーム内容：{safe_text}

上記をもとに返信文を作成してください。
"""
        )

        st.success("返信文")
        st.write(response.output[0].content[0].text)
