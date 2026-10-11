import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
import re

st.set_page_config(page_title="楽天口コミ要約ツール", layout="wide")
st.title("🛍️ 楽天口コミ要約ツール（無料版）")

# APIキー設定
API_KEY = "AQ.Ab8RN6Kwe5YP8FsohywP6TdgORKvd14Uh6uhZfx8oxNSmYFaOA"

url = st.text_input("楽天レビューページのURLを入力してください（例: https://review.rakuten.co.jp/item/...）")

if st.button("要約を実行"):
    if not url:
        st.warning("URLを入力してください。")
    else:
        with st.spinner("レビューを取得中..."):
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            try:
                res = requests.get(url, headers=headers, timeout=30)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, "html.parser")
                
                review_elements = soup.find_all(["span", "div"], class_=re.compile(r"revRvwUserItemDescr|revRvwUserEntryComment|review-body"))
                reviews = [e.get_text(strip=True) for e in review_elements if e.get_text(strip=True)]
                
                if not reviews:
                    st.error("レビュー本文が見つかりませんでした。商品ページ（item.rakuten.co.jp）ではなく、「みんなのレビュー」を押した後のレビュー一覧ページ（review.rakuten.co.jp）のURLを入力してみてください。")
                else:
                    st.info(f"{len(reviews)} 件の口コミを取得しました。Geminiで分析中...")
                    
                    client = genai.Client(api_key=API_KEY)
                    prompt = f"""
以下の楽天市場の商品レビューから、アフィリエイト記事作成のリサーチ用に要約・分析してください。

【出力フォーマット】
■ 総合的な評価傾向（1〜2行）
■ メリット（良い点・高評価の理由）
■ デメリット（悪い点・気になる点）
■ おすすめできる人・できない人

【レビュー本文】
{"\n---\n".join(reviews[:30])}
"""
                    response = client.models.generate_content(
                        model='gemini-3.5-flash',
                        contents=prompt,
                    )
                    
                    st.markdown("### 📊 口コミ要約結果")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
