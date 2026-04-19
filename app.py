import streamlit as st
import re

st.set_page_config(page_title="ECクレーム対応AI Pro", layout="centered")

st.title("🛡️ ECクレーム対応AI（プロ版）")

# ------------------------
# 危険ワード
# ------------------------
DANGEROUS_WORDS = ["全額返金", "保証します", "責任を負います", "必ず対応"]

# ------------------------
# 感情検知（簡易）
# ------------------------
def detect_emotion(text):
    if "最悪" in text or "ふざけるな" in text or "怒" in text:
        return "🔴 強い怒り"
    elif "困って" in text or "不満" in text:
        return "🟡 不満"
    else:
        return "🟢 通常"

# ------------------------
# 個人情報マスク
# ------------------------
def mask_info(text):
    text = re.sub(r'\d{2,4}-\d{2,4}-\d{3,4}', '***-****-****', text)
    text = re.sub(r'\S+@\S+', '***@***.com', text)
    return text

# ------------------------
# セッション
# ------------------------
if "mail" not in st.session_state:
    st.session_state.mail = ""

# ------------------------
# 入力
# ------------------------
shop = st.text_input("ショップ名")
customer = st.text_input("顧客名")

rule = st.text_area("社内ルール（例：返金は7日以内のみ）")

issue = st.selectbox(
    "クレーム内容",
    ["配送遅延", "商品不良", "返品・返金", "注文ミス"]
)

detail = st.text_area("クレーム内容")

# ------------------------
# 感情分析
# ------------------------
if detail:
    emotion = detect_emotion(detail)
    st.info(f"顧客感情：{emotion}")

# ------------------------
# NGチェック
# ------------------------
if detail:
    found = [w for w in DANGEROUS_WORDS if w in detail]
    if found:
        st.error(f"⚠️ 危険表現: {', '.join(found)}")

# ------------------------
# 生成
# ------------------------
if st.button("返信生成"):

    if not shop or not customer or not detail:
        st.warning("入力不足")
    else:

        safe_text = mask_info(detail)

        # クレーム別
        if issue == "配送遅延":
            base = "商品の配送遅延につきまして深くお詫び申し上げます。"
        elif issue == "商品不良":
            base = "商品不良につきまして深くお詫び申し上げます。"
        elif issue == "返品・返金":
            base = "返品・返金の件につきましてご迷惑をおかけしております。"
        else:
            base = "ご注文に関する不備についてお詫び申し上げます。"

        # 感情によって謝罪強化
        if "🔴" in detect_emotion(detail):
            apology = "この度は多大なるご不快な思いをおかけし、心より深くお詫び申し上げます。"
        else:
            apology = "この度はご迷惑をおかけし申し訳ございません。"

        mail = f"""
件名：お詫びとご対応について

{customer}

{shop}でございます。

{apology}

{base}

{safe_text}

【対応について】
{rule if rule else "社内確認の上、対応いたします。"}

本件は担当者が責任を持って対応いたします。

何卒よろしくお願い申し上げます。
"""

        st.session_state.mail = mail

# ------------------------
# 表示
# ------------------------
if st.session_state.mail:
    st.subheader("📨 下書き（AI生成）")
    st.text_area("", st.session_state.mail, height=300)

    st.warning("⚠️ AIの下書きです。必ず人が確認してください")

    # リスク表示
    if any(word in st.session_state.mail for word in DANGEROUS_WORDS):
        st.error("⚠️ 法的リスクあり（要修正）")
    else:
        st.success("🟢 リスク低")

    # 承認フロー
    if st.button("✅ 人間確認OK"):
        st.success("送信可能です")

    if st.button("🧑‍💼 上司確認へ"):
        st.info("上司確認を行ってください")
