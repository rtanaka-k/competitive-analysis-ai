# -*- coding: utf-8 -*-
import streamlit as st
from openai import OpenAI
import anthropic
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import json
import hmac
import os
import csv

# ============================================
# ページ設定（最初に実行）
# ============================================
st.set_page_config(
    page_title="競合分析AI v2.1 (Dual API)",
    page_icon="📊",
    layout="wide"
)

# ============================================
# セキュリティ機能: アクセスログ記録
# ============================================

def ensure_log_directory():
    """ログディレクトリの作成"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

def log_access(username, action, details=""):
    """アクセスログの記録"""
    try:
        log_dir = ensure_log_directory()
        log_file = os.path.join(log_dir, "access_log.csv")
        
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "display_name": st.session_state.get("user_display_name", username),
            "action": action,
            "details": details
        }
        
        file_exists = os.path.isfile(log_file)
        
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "username", "display_name", "action", "details"])
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)
            
    except Exception as e:
        print(f"ログ記録エラー: {e}")

def get_access_logs():
    """アクセスログの取得"""
    log_file = os.path.join("logs", "access_log.csv")
    
    if os.path.exists(log_file):
        try:
            df = pd.read_csv(log_file)
            return df
        except Exception as e:
            st.error(f"ログファイルの読み込みに失敗しました: {e}")
            return None
    else:
        return None

# ============================================
# セキュリティ機能: ベーシック認証
# ============================================

def check_password():
    """ユーザー名とパスワードによる認証"""
    
    def login_form():
        """ログインフォームの表示"""
        st.title("競合分析AI v2.1 (Dual API)")
        st.info("KRAFTON Japan 社内ツールです。ユーザー名とパスワードを入力してください。")
        
        with st.form("login_form"):
            username = st.text_input("ユーザー名", key="username_input")
            password = st.text_input("パスワード", type="password", key="password_input")
            submit = st.form_submit_button("ログイン", type="primary", use_container_width=True)
            
            if submit:
                if "users" in st.secrets:
                    users = st.secrets["users"]
                    
                    if username in users:
                        correct_password = users[username]["password"]
                        
                        if hmac.compare_digest(password, correct_password):
                            st.session_state["password_correct"] = True
                            st.session_state["username"] = username
                            st.session_state["user_display_name"] = users[username].get("display_name", username)
                            
                            log_access(username, "login", "ログイン成功")
                            
                            st.rerun()
                        else:
                            st.error("パスワードが間違っています")
                            log_access(username, "login_failed", "パスワード不一致")
                    else:
                        st.error("ユーザー名が見つかりません")
                        log_access(username, "login_failed", "ユーザー名不明")
                else:
                    st.warning("ユーザー設定が見つかりません。デフォルト認証を使用します。")
                    if username == "admin" and password == "krafton2024":
                        st.session_state["password_correct"] = True
                        st.session_state["username"] = username
                        st.session_state["user_display_name"] = "管理者"
                        
                        log_access(username, "login", "ログイン成功（デフォルト認証）")
                        
                        st.rerun()
                    else:
                        st.error("ユーザー名またはパスワードが間違っています")
        
        with st.expander("テスト用アカウント情報"):
            st.caption("Secretsが未設定の場合、以下でログインできます：")
            st.code("ユーザー名: admin\nパスワード: krafton2024")
    
    if "password_correct" not in st.session_state:
        login_form()
        return False
    elif not st.session_state["password_correct"]:
        login_form()
        return False
    else:
        return True

# パスワード認証をチェック
if not check_password():
    st.stop()

# ============================================
# ログイン後のメインアプリケーション
# ============================================

# カスタムCSS
st.markdown("""
<style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .stMarkdown table {
        border-collapse: collapse;
        width: 100%;
        margin: 20px 0;
        border: 2px solid #4a90e2;
    }
    .stMarkdown th {
        background-color: #1e3a5f;
        color: white;
        padding: 12px 15px;
        text-align: left;
        border: 1px solid #4a90e2;
        font-weight: bold;
    }
    .stMarkdown td {
        padding: 10px 15px;
        border: 1px solid #555;
        color: #e0e0e0;
    }
    .stMarkdown tbody tr:nth-child(even) {
        background-color: #2d2d2d;
    }
    .stMarkdown tbody tr:nth-child(odd) {
        background-color: #1a1a1a;
    }
    .stMarkdown tbody tr:hover {
        background-color: #3a3a3a;
    }
</style>
""", unsafe_allow_html=True)

# タイトル
col_title, col_user = st.columns([4, 1])
with col_title:
    st.title("競合分析AI v2.1 (Dual API)")
    st.markdown("**市場データに基づく競合タイトル分析ツール**")
with col_user:
    st.markdown(f"**ログイン中:** {st.session_state.get('user_display_name', 'ゲスト')}")
    if st.button("ログアウト"):
        log_access(st.session_state.get("username", "unknown"), "logout", "ログアウト")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("---")

# ============================================
# AI Provider選択
# ============================================
st.subheader("■ AI Provider選択")
provider = st.radio(
    "使用するAI",
    ["Claude (Anthropic)", "OpenAI (GPT)"],
    horizontal=True,
    help="ClaudeまたはOpenAIのAPIを選択してください"
)

# API Key確認
if provider == "Claude (Anthropic)":
    if "ANTHROPIC_API_KEY" in st.secrets:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        st.success("✓ Claude API Key設定済み")
    else:
        st.error("⚠️ ANTHROPIC_API_KEY が設定されていません")
        st.stop()
else:  # OpenAI
    if "OPENAI_API_KEY" in st.secrets:
        api_key = st.secrets["OPENAI_API_KEY"]
        st.success("✓ OpenAI API Key設定済み")
        
        # Vector Store ID確認（オプション）
        if "OPENAI_VECTOR_STORE_ID" in st.secrets:
            vector_store_id = st.secrets["OPENAI_VECTOR_STORE_ID"]
            st.info(f"📚 Vector Store設定済み: {vector_store_id[:20]}...")
        else:
            vector_store_id = None
            st.warning("ℹ️ Vector Store IDが未設定です。組み込みデータのみ使用します。")
    else:
        st.error("⚠️ OPENAI_API_KEY が設定されていません")
        st.stop()

st.markdown("---")

# 組み込み市場データ
MARKET_DATA = """
【2024年度 国内ゲーム市場データ】
■ 総市場規模
- モバイルゲーム: 約1.3兆円
- 家庭用ゲーム: 約0.4兆円
- PCゲーム: 約0.2兆円

■ ジャンル別シェア（モバイル）
- RPG: 28%
- パズル: 15%
- アクション: 12%
- カードゲーム: 10%
- その他: 35%

■ 主要タイトル推定年間売上（2024年）
1. モンスターストライク: 約500億円
2. パズル&ドラゴンズ: 約300億円
3. Fate/Grand Order: 約400億円
4. プロジェクトセカイ: 約250億円
5. ウマ娘 プリティーダービー: 約600億円

■ プラットフォーム比率
- iOS: 55%
- Android: 45%

■ ユーザー獲得単価（CPI）
- RPG: 800-1,500円
- パズル: 300-600円
- アクション: 500-1,000円
"""

# 簡易入力フォーム
st.subheader("■ 分析内容入力")
user_prompt = st.text_area(
    "分析したい内容や質問を入力してください",
    height=200,
    placeholder=f"""例:
競合タイトル: モンスターストライク
自社タイトル: [新作RPG]

以下の観点で競合分析してください:
- 市場規模・シェア
- 収益モデル
- ユーザー獲得戦略

既知情報:
- モンストの年間売上: 約500億円
- 主要ターゲット: 20-30代男性

以下の市場データも参考にしてください:
{MARKET_DATA[:200]}..."""
)

# 分析実行ボタン
st.markdown("---")
if st.button("▶ 競合分析を実行", type="primary", use_container_width=True):
    if not user_prompt:
        st.error("● 分析内容を入力してください")
    else:
        # アクセスログ記録
        log_access(
            st.session_state.get("username", "unknown"),
            "analysis_executed",
            f"Provider:{provider}"
        )
        
        # プロンプトに市場データを追加
        full_prompt = f"""
以下の市場データを参考に分析してください:

{MARKET_DATA}

---

{user_prompt}

---

【出力形式】
必ず以下の形式で出力してください:

## エグゼクティブサマリー
[3-5行の要約]

## 主要な発見事項
[重要ポイントを3-5個、箇条書きで]

## 推奨アクション
[具体的な推奨事項を3-5個、箇条書きで]

## リスクと機会
[主要なリスクと機会を各3個ずつ]
"""
        
        # ===== Claude を使うパターン =====
        if provider == "Claude (Anthropic)":
            with st.spinner("Claude (Sonnet 4) で分析中... (30-60秒)"):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    message = client.messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4000,
                        messages=[{"role": "user", "content": full_prompt}]
                    )
                    
                    result = message.content[0].text
                    st.success("■ 分析完了 (Claude)")
                    
                except Exception as e:
                    st.error(f"× Claude APIエラー: {str(e)}")
                    log_access(st.session_state.get("username", "unknown"), "analysis_error", f"Claude Error: {str(e)}")
                    st.stop()
        
        # ===== OpenAI を使うパターン =====
        else:
            with st.spinner("OpenAI (GPT-4o) で分析中... (30-60秒)"):
                try:
                    client = OpenAI(api_key=api_key)
                    
                    # Chat Completions API（正しい方法）
                    response = client.chat.completions.create(
                        model="gpt-4o",  # 最新モデル
                        messages=[
                            {"role": "system", "content": "あなたはゲーム業界の競合分析専門家です。"},
                            {"role": "user", "content": full_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=4000
                    )
                    
                    result = response.choices[0].message.content
                    st.success("■ 分析完了 (OpenAI GPT-4o)")
                    
                except Exception as e:
                    st.error(f"× OpenAI APIエラー: {str(e)}")
                    st.info(f"ヒント: モデル名を確認してください。現在: gpt-4o")
                    log_access(st.session_state.get("username", "unknown"), "analysis_error", f"OpenAI Error: {str(e)}")
                    st.stop()
        
        # ===== 結果の表示 =====
        st.markdown("---")
        st.markdown("## ■ 分析結果")
        
        # エグゼクティブサマリー抽出
        if "エグゼクティブサマリー" in result or "EXECUTIVE_SUMMARY" in result:
            try:
                summary_start = result.find("エグゼクティブサマリー") if "エグゼクティブサマリー" in result else result.find("EXECUTIVE_SUMMARY")
                summary_end = result.find("##", summary_start + 1)
                if summary_end == -1:
                    summary_end = len(result)
                
                summary_text = result[summary_start:summary_end].replace("エグゼクティブサマリー", "").replace("EXECUTIVE_SUMMARY", "").strip()
                summary_text = summary_text.replace("##", "").strip()
                
                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; background-color: #1e3a5f; margin: 20px 0; border: 2px solid #4a90e2; color: white;">
                    <h3 style="color: #4a90e2; margin-top: 0;">■ エグゼクティブサマリー</h3>
                    <p style="color: white; line-height: 1.6;">{summary_text}</p>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass
        
        # 詳細結果をタブで表示
        st.markdown("---")
        tab1, tab2 = st.tabs(["■ 詳細分析", "■ エクスポート"])
        
        with tab1:
            st.markdown(result)
        
        with tab2:
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                st.download_button(
                    label="▶ テキスト形式",
                    data=result,
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            with col_exp2:
                md_content = f"""# 競合分析レポート

**分析日**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}
**AI Provider**: {provider}
**ユーザー**: {st.session_state.get('user_display_name', 'ゲスト')}

---

{result}
"""
                st.download_button(
                    label="▶ Markdown形式",
                    data=md_content,
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

# 管理者用: アクセスログ表示
if st.session_state.get("username") == "admin":
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔐 管理者機能")
        if st.button("アクセスログを表示"):
            st.session_state["show_logs"] = True

if st.session_state.get("show_logs", False):
    st.markdown("---")
    st.subheader("🔐 アクセスログ")
    
    logs_df = get_access_logs()
    if logs_df is not None and not logs_df.empty:
        st.dataframe(logs_df.sort_values('timestamp', ascending=False), use_container_width=True)
    else:
        st.info("アクセスログがありません")
    
    if st.button("ログを閉じる"):
        st.session_state["show_logs"] = False
        st.rerun()

# フッター
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.markdown("**競合分析AI v2.1 (Dual API)**")
with col_f2:
    st.markdown(f"*Powered by {provider}*")
with col_f3:
    st.markdown(f"*{datetime.now().strftime('%Y/%m/%d')}*")
