import streamlit as st
from openai import OpenAI
import anthropic

st.set_page_config(page_title="AI Competitive Analysis (Switch)", layout="wide")

st.title("AI Competitive Analysis - Provider Switch Demo")

# プロバイダの選択
provider = st.radio(
    "どのプロバイダを使いますか？",
    ["Claude (Anthropic)", "OpenAI"],
    horizontal=True,
)

st.caption("※ secrets.toml に ANTHROPIC_API_KEY / OPENAI_API_KEY を設定しておいてください。")

user_prompt = st.text_area("分析したい内容や質問を入力してください", height=150)

if st.button("分析を実行する", type="primary", use_container_width=True):

    if not user_prompt:
        st.error("入力が空です。内容を入力してください。")
        st.stop()

    # ===== Claude を使うパターン =====
    if provider == "Claude (Anthropic)":
        if "ANTHROPIC_API_KEY" not in st.secrets:
            st.error("ANTHROPIC_API_KEY が secrets.toml に設定されていません。")
            st.stop()

        claude_api_key = st.secrets["ANTHROPIC_API_KEY"]
        client = anthropic.Anthropic(api_key=claude_api_key)

        with st.spinner("Claude (Sonnet) で分析中..."):
            message = client.messages.create(
                model="claude-sonnet-4.1",
                max_tokens=2000,
                messages=[{"role": "user", "content": user_prompt}],
            )
            answer = message.content[0].text

        st.success("Claude からの回答")
        st.write(answer)

    # ===== OpenAI を使うパターン =====
    else:
        if "OPENAI_API_KEY" not in st.secrets:
            st.error("OPENAI_API_KEY が secrets.toml に設定されていません。")
            st.stop()

        openai_api_key = st.secrets["OPENAI_API_KEY"]
        client = OpenAI(api_key=openai_api_key)

        with st.spinner("OpenAI (gpt-4.1-mini) で分析中..."):
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=user_prompt,
            )
            answer = response.output[0].content[0].text

        st.success("OpenAI からの回答")
        st.write(answer)
