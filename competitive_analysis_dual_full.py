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

# ページ設定
st.set_page_config(
    page_title="競合分析AI v2.7 (Dual Mode)",
    page_icon="■",
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
        st.title("競合分析AI v2.7 (Dual Mode)")
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
    .highlight-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    .summary-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #e8f4f8;
        margin: 20px 0;
        border: 2px solid #1f77b4;
    }
    
    /* 表のスタイリング（ダークモード対応） */
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
    
    /* ゼブラストライプ（交互に背景色） */
    .stMarkdown tbody tr:nth-child(even) {
        background-color: #2d2d2d;
    }
    
    .stMarkdown tbody tr:nth-child(odd) {
        background-color: #1a1a1a;
    }
    
    /* ホバー効果 */
    .stMarkdown tbody tr:hover {
        background-color: #3a3a3a;
    }
</style>
""", unsafe_allow_html=True)

# タイトル（ユーザー名表示付き）
col_title, col_user = st.columns([4, 1])
with col_title:
    st.title("競合分析AI v2.7 (Dual Mode)")
    st.markdown("**市場データに基づく競合タイトル分析ツール**")
with col_user:
    st.markdown(f"**ログイン中:** {st.session_state.get('user_display_name', 'ゲスト')}")
    if st.button("ログアウト"):
        log_access(st.session_state.get("username", "unknown"), "logout", "ログアウト")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

st.markdown("---")

# サイドバー
with st.sidebar:
    st.header("■ 設定")
    
    # API Provider選択
    api_provider = st.radio(
        "AI Provider",
        ["Claude (Anthropic)", "OpenAI (GPT)"],
        help="使用するAIモデルを選択してください"
    )
    
    # Claude専用: モデル選択
    claude_model_mode = "sonnet"  # デフォルト
    if api_provider == "Claude (Anthropic)":
        st.markdown("---")
        claude_model_mode = st.radio(
            "🤖 Claudeモデル選択",
            ["標準モード (Sonnet 4)", "高精度モード (Opus 4)"],
            index=0,
            help="""
            **標準モード**: 高速・低コスト・安定動作（v2.1ベース）
            **高精度モード**: より正確な分析（コスト5倍、v2.6最適化版）
            """
        )
        
        if "高精度" in claude_model_mode:
            st.warning("💎 **Opus 4**: 最高精度の分析（コスト5倍）")
        else:
            st.info("⚡ **Sonnet 4**: 標準的な分析を高速で提供")
    
    # API Key取得（Secretsから自動取得）
    if api_provider == "Claude (Anthropic)":
        if "ANTHROPIC_API_KEY" in st.secrets:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
            st.success("✓ Claude API Key設定済み")
        else:
            st.error("⚠️ Claude API Keyが設定されていません")
            st.info("管理者にStreamlit SecretsでANTHROPIC_API_KEYを設定するよう連絡してください")
            api_key = None
    else:  # OpenAI
        if "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            st.success("✓ OpenAI API Key設定済み")
            
            # Vector Store ID確認（オプション）
            if "OPENAI_VECTOR_STORE_ID" in st.secrets:
                vector_store_id = st.secrets["OPENAI_VECTOR_STORE_ID"]
                st.info(f"📚 Vector Store設定済み")
            else:
                vector_store_id = None
        else:
            st.error("⚠️ OpenAI API Keyが設定されていません")
            st.info("管理者にStreamlit SecretsでOPENAI_API_KEYを設定するよう連絡してください")
            api_key = None
            vector_store_id = None
    
    st.markdown("---")
    st.header("■ データソース")
    
    uploaded_file = st.file_uploader(
        "市場データPDFをアップロード（任意）",
        type=['pdf'],
        help="ファミ通白書などのPDFファイル"
    )
    
    st.markdown("### ▶ 組み込みデータ")
    st.markdown("""
    - 国内モバイルゲーム市場: 約1.3兆円
    - RPGジャンルシェア: 25-30%
    - 主要タイトルTOP10データ
    """)
    
    st.markdown("---")
    st.markdown("### ▶ 使い方")
    st.markdown("""
    1. 競合情報を入力
    2. 分析実行
    3. インタラクティブなグラフで確認
    """)
    
    # 管理者用: アクセスログ表示
    if st.session_state.get("username") == "admin":
        st.markdown("---")
        st.markdown("### 🔐 管理者機能")
        if st.button("アクセスログを表示"):
            st.session_state["show_logs"] = True

# メイン入力フォーム
st.subheader("■ 基本情報入力")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### ▶ 競合タイトル情報")
    competitor_name = st.text_input(
        "競合タイトル名 *",
        placeholder="例: モンスターストライク",
    )
    
    competitor_genre = st.selectbox(
        "ジャンル",
        ["RPG", "アクション", "パズル", "シミュレーション", "スポーツ", 
         "レーシング", "アドベンチャー", "カードゲーム", "その他"]
    )
    
    competitor_platform = st.multiselect(
        "プラットフォーム",
        ["iOS", "Android", "PlayStation", "Nintendo Switch", "Xbox", "Steam/PC"],
        default=["iOS", "Android"]
    )

with col2:
    st.markdown("#### ▶ 自社タイトル情報")
    our_product = st.text_input(
        "自社タイトル名 *",
        placeholder="例: [プロジェクト名]",
    )
    
    our_genre = st.selectbox(
        "自社ジャンル",
        ["RPG", "アクション", "パズル", "シミュレーション", "スポーツ", 
         "レーシング", "アドベンチャー", "カードゲーム", "その他"],
        key="our_genre"
    )
    
    our_platform = st.multiselect(
        "自社プラットフォーム",
        ["iOS", "Android", "PlayStation", "Nintendo Switch", "Xbox", "Steam/PC"],
        default=["iOS", "Android"],
        key="our_platform"
    )

st.markdown("---")
st.subheader("■ 分析設定")

col3, col4 = st.columns(2)

with col3:
    analysis_type = st.radio(
        "分析タイプ",
        ["包括的分析", "マーケティング特化", "マネタイゼーション特化"],
    )

with col4:
    comparison_focus = st.multiselect(
        "比較観点",
        ["市場規模・シェア", "収益モデル", "ユーザー獲得戦略", 
         "ゲーム設計・機能", "運営手法", "IP・コラボ戦略"],
        default=["市場規模・シェア", "収益モデル"]
    )

# 詳細情報
st.markdown("---")
st.subheader("■ 詳細情報")

col_add1, col_add2 = st.columns(2)

with col_add1:
    st.markdown("#### ▶ 競合タイトルの既知情報")
    competitor_revenue = st.text_input(
        "既知の年間売上（任意）",
        placeholder="例: 200億円",
        help="既知の売上データがあれば入力してください"
    )
    competitor_dau = st.text_input(
        "既知のDAU/MAU（任意）",
        placeholder="例: 50万人/200万人"
    )

with col_add2:
    st.markdown("#### ▶ 自社タイトルの目標数値")
    our_revenue_target = st.text_input(
        "売上目標（任意）",
        placeholder="例: 100億円"
    )
    our_dau_target = st.text_input(
        "DAU/MAU目標（任意）",
        placeholder="例: 30万人/100万人"
    )

additional_context = st.text_area(
    "特記事項・既知の情報",
    height=100,
    placeholder="例: 競合の月間売上50億円、主要ターゲット20-30代男性 など"
)

# 参照データの処理
reference_data = ""
if uploaded_file is not None:
    st.info("▶ アップロードされたPDFを参照データとして使用します")
    reference_data = "\n【アップロードされた市場データ】\n市場レポートの内容を参照中..."

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

# 分析実行ボタン
st.markdown("---")
if st.button("▶ 競合分析を実行", type="primary", use_container_width=True):
    if not api_key:
        st.error("● API Keyが設定されていません。管理者にStreamlit SecretsでANTHROPIC_API_KEYを設定するよう連絡してください。")
    elif not competitor_name or not our_product:
        st.error("● 競合タイトル名と自社タイトル名を入力してください")
    else:
        # アクセスログ記録
        log_access(
            st.session_state.get("username", "unknown"),
            "analysis_executed",
            f"競合:{competitor_name} vs 自社:{our_product}"
        )
        
        with st.spinner(f"{api_provider}で分析中... (60-90秒)"):
            try:
                # モデルモード判定
                use_opus = "高精度" in claude_model_mode if api_provider == "Claude (Anthropic)" else False
                
                # プロンプト構築
                prompt_intro = ""
                if use_opus:
                    # Opus 4用: Few-Shot Examples追加
                    prompt_intro = """
**【出力形式の重要な注意】**
すべてのセクションは必ずMarkdown表形式で出力してください。

【正しい出力例】
| 項目 | FGO | モンスターストライク |
|------|-----|-------------------|
| 推定年間売上 | 950億円 | 800億円（目標） |
| 市場ランキング | TOP 3 | TOP 10（目標） |

【誤った出力例（禁止）】
FGOの推定年間売上は950億円です。
モンスターストライクの目標は800億円です。

→ このようなテキスト形式は絶対禁止です！

---

"""
                
                prompt = f"""
あなたはゲーム業界の競合分析専門家です。以下の市場データと情報を基に詳細な分析を実施してください。

{prompt_intro}
{MARKET_DATA}

{reference_data}

【分析対象】
■ 競合タイトル
- タイトル名: {competitor_name}
- ジャンル: {competitor_genre}
- プラットフォーム: {', '.join(competitor_platform)}
{f"- 既知の年間売上: {competitor_revenue}" if competitor_revenue else ""}
{f"- 既知のDAU/MAU: {competitor_dau}" if competitor_dau else ""}

■ 自社タイトル
- タイトル名: {our_product}
- ジャンル: {our_genre}
- プラットフォーム: {', '.join(our_platform)}
{f"- 売上目標: {our_revenue_target}" if our_revenue_target else ""}
{f"- DAU/MAU目標: {our_dau_target}" if our_dau_target else ""}

【分析タイプ】: {analysis_type}
【比較観点】: {', '.join(comparison_focus)}

【特記事項】
{additional_context if additional_context else "特になし"}

**【重要】既知の情報がある場合は、必ずその数値を優先して使用してください。推測が必要な場合は『推測』と明記してください。**

---

**【重要指示】以下を必ず守ってください:**
1. COMPARISON_METRICSは必ずJSON形式（```json ... ```）で出力
2. 全てのセクションで必ず表形式（Markdownテーブル）を使用
3. 箇条書き（-や•）は使用禁止
4. セクション名（MARKET_ANALYSIS、COMPETITOR_ANALYSIS等）を単独行で出力しない（必ず## セクション名の形式）
5. **既知の数値情報がある場合は必ずその値を使用し、『（市場データ参照）』または『（既知情報）』と明記**
6. **推測値の場合は必ず『（推定）』と明記し、根拠を示す**
7. **データが不明な場合は『データなし』と記載し、無理に推測しない**
8. **すべての数値・評価に対して、可能な限り出典・根拠を併記する**
9. **買い切りゲームとライブサービスで指標を適切に使い分ける**
10. **楽観的すぎる予測を避け、現実的なリスクも明示する**

以下の形式で回答してください。**必ず数値データを引用**してください:

## EXECUTIVE_SUMMARY
*3-5行で結論と最重要ポイント簡潔に記載*

## COMPARISON_METRICS

**評価軸の定義**（100点満点）:
- **market_position（市場ポジション）**: 市場での認知度・ランキング順位・ブランド力
- **revenue_potential（収益性）**: 年間売上規模・ARPU・課金効率・収益安定性
  * ライブサービス: 継続課金・イベント収益・長期ARPU
  * 買い切り: 初回売上・DLC収益・周辺商品展開
- **user_base（ユーザー基盤）**: DAU/MAU・ユーザー定着率・コミュニティ活性度
- **brand_strength（ブランド力）**: IP価値・メディア露出・ファンロイヤリティ・二次展開力
- **technology（技術力）**: グラフィック品質・システム安定性・技術革新性・開発体制の強さ

**必ず以下の正確なJSON形式で出力**（評価の根拠は表の後に記載）:
```json
{{
  "competitor": {{
    "market_position": 85,
    "revenue_potential": 75,
    "user_base": 80,
    "brand_strength": 90,
    "technology": 70
  }},
  "our_product": {{
    "market_position": 40,
    "revenue_potential": 60,
    "user_base": 30,
    "brand_strength": 45,
    "technology": 75
  }}
}}
```

**各評価の根拠**（必ず具体的な要素を列挙）:

| 評価軸 | 競合スコア | 根拠となる具体的要素 | 自社スコア | 根拠となる具体的要素 |
|-------|----------|-------------------|----------|-------------------|
| 市場ポジション | XX点 | • [要素1: 例：国内売上TOP3]<br>• [要素2: 例：Google検索トレンド高位]<br>• [要素3: 例：SNS言及数多数] | XX点 | • [要素1]<br>• [要素2]<br>• [要素3] |
| 収益性 | XX点 | • [要素1: 例：年間売上600億円]<br>• [要素2: 例：ARPU 8,000円/月]<br>• [要素3: 例：課金ユーザー率15%] | XX点 | • [要素1]<br>• [要素2]<br>• [要素3] |
| ユーザー基盤 | XX点 | • [要素1: 例：DAU 200万人]<br>• [要素2: 例：継続率70%]<br>• [要素3: 例：コミュニティ活発] | XX点 | • [要素1]<br>• [要素2]<br>• [要素3] |
| ブランド力 | XX点 | • [要素1: 例：IP知名度90%]<br>• [要素2: 例：コラボ実績多数]<br>• [要素3: 例：メディア露出高] | XX点 | • [要素1]<br>• [要素2]<br>• [要素3] |
| 技術力 | XX点 | • [要素1: 例：グラフィック品質高]<br>• [要素2: 例：サーバー安定性99.9%]<br>• [要素3: 例：技術的革新性] | XX点 | • [要素1]<br>• [要素2]<br>• [要素3] |

**重要**: 各評価軸について、スコアを構成する具体的要素を最低3つ挙げること。抽象的な表現ではなく、数値・事実に基づく要素を記載。


## MARKET_ANALYSIS
### 市場規模とトレンド

**必ず以下の表形式で出力（箇条書き禁止）**:
**既知の売上データがある場合は必ずその値を使用し、『（既知情報）』と明記してください**

| 項目 | {competitor_name} | {our_product} |
|------|-------------------|---------------|
| 推定年間売上 | XXX億円（既知情報 or 市場データ参照 or 推定） | XXX億円（目標 or 推定） |
| 市場ランキング | TOP XX（[期間]・[範囲]） | TOP XX（[期間]・[範囲]・目標） |

*ランキング定義例: 「月間・国内モバイル全体」「年間・ジャンル内」「週間・iOS売上」など具体的に明記*

| DAU/MAU | XX万人/XX万人（既知 or 推定） | XX万人/XX万人（目標） |
| 主要ターゲット層 | XX代XX性 | XX代XX性 |
| 市場シェア | X.X%（既知 or 推定） | X.X%（目標） |

*既知の情報を最優先し、推測の場合は必ず根拠を付記*
**重要**: 買い切りゲームの場合、DAU/MAUは販売本数・アクティブプレイヤー数など適切な指標に置き換えること
（例: 「累計販売XX万本」「月間アクティブプレイヤーXX万人」など）

### ジャンル特性

**必ず以下の表形式で出力（箇条書き禁止）**:

| 特性項目 | {competitor_name} | {our_product} |
|----------|-------------------|---------------|
| ジャンル適合度 | 高/中/低 + 理由 | 高/中/低 + 理由 |
| 差別化ポイント | 具体的特徴 | 具体的特徴 |
| CPI（ユーザー獲得単価） | XXX円（[出典]） | XXX円（推定・目標） |
| 主要収益モデル | [ガチャ/サブスク等] | [想定モデル] |

*CPI出典例: 「業界平均」「類似タイトル実績」「マーケティングレポート」など具体的に明記*
*データがない場合は「推測・根拠不足」と明記すること*

## COMPETITOR_ANALYSIS

### ビジネスモデル比較

| 項目 | {competitor_name} | {our_product} |
|------|-------------------|---------------|
| 収益化手法 | [具体的手法] | [想定手法] |
| 課金設計 | [ガチャ/サブスク等] | [想定設計] |
| 平均課金単価 | [推定金額] | [目標金額] |
| 収益の柱 | [メイン収益源] | [想定収益源] |

### 強み・弱み比較

**必ず以下の表形式で出力（箇条書き禁止）**:

| 評価軸 | {competitor_name} | {our_product} |
|--------|-------------------|---------------|
| **強み1** | [具体的な強み] | [具体的な強み] |
| **強み2** | [具体的な強み] | [具体的な強み] |
| **強み3** | [具体的な強み] | [具体的な強み] |
| **弱み1** | [具体的な弱み] | [具体的な弱み] |
| **弱み2** | [具体的な弱み] | [具体的な弱み] |
| **弱み3** | [具体的な弱み] | [具体的な弱み] |

## GAP_ANALYSIS

### 主要ギャップ分析

| 評価項目 | 現状のギャップ | 重要度 | 対応優先度 |
|----------|---------------|--------|-----------|
| 市場認知度 | {competitor_name}が[X]点優位 | 高/中/低 | 高/中/低 |
| 収益性 | {competitor_name}が[X]点優位 | 高/中/低 | 高/中/低 |
| ユーザー基盤 | {competitor_name}が[X]点優位 | 高/中/低 | 高/中/低 |
| 技術力 | {our_product}が[X]点優位 | 高/中/低 | 高/中/低 |
| ブランド力 | {competitor_name}が[X]点優位 | 高/中/低 | 高/中/低 |

### 差別化戦略

**必ず以下の表形式で出力（{our_product}の差別化ポイントを{competitor_name}と比較）**:

| 差別化要素 | {competitor_name}のアプローチ | {our_product}の差別化ポイント | 実現可能性 |
|-----------|----------------------------|----------------------------|----------|
| [要素1] | [競合の現状] | [自社の差別化内容] | 高/中/低 |
| [要素2] | [競合の現状] | [自社の差別化内容] | 高/中/低 |
| [要素3] | [競合の現状] | [自社の差別化内容] | 高/中/低 |

## ACTION_PLAN ({our_product}向け)

**{our_product}の具体的アクションプラン**

### 短期施策（3ヶ月以内）

**対象タイトル: {our_product}**

**必ず以下の表形式で出力**:

| No | 施策 | 目的 | 実行内容 | 期待効果 | 優先度 |
|----|------|------|---------|---------|--------|
| 1 | [施策名] | [目的] | [具体的内容] | [効果・KPI] | 高/中/低 |
| 2 | [施策名] | [目的] | [具体的内容] | [効果・KPI] | 高/中/低 |
| 3 | [施策名] | [目的] | [具体的内容] | [効果・KPI] | 高/中/低 |

### 中期施策（6-12ヶ月）

**対象タイトル: {our_product}**

**必ず以下の表形式で出力**:

| No | 戦略 | 目標 | 実行計画 | マイルストーン | KPI |
|----|------|------|---------|--------------|-----|
| 1 | [戦略名] | [目標数値] | [計画概要] | [達成時期] | [測定指標] |
| 2 | [戦略名] | [目標数値] | [計画概要] | [達成時期] | [測定指標] |

## RISK_OPPORTUNITY ({our_product}向け)

**{our_product}のリスクと市場機会分析**

### リスク分析

**対象タイトル: {our_product}**

| リスク項目 | 内容 | 発生確率 | 影響度 | 対策 |
|-----------|------|---------|--------|------|
| [リスク1] | [具体的内容] | 高/中/低 | 高/中/低 | [対策] |
| [リスク2] | [具体的内容] | 高/中/低 | 高/中/低 | [対策] |
| [リスク3] | [具体的内容] | 高/中/低 | 高/中/低 | [対策] |

### 市場機会

**対象タイトル: {our_product}**

| 機会項目 | 内容 | 実現可能性 | 期待効果 | アプローチ |
|---------|------|-----------|---------|-----------|
| [機会1] | [具体的内容] | 高/中/低 | [効果] | [方法] |
| [機会2] | [具体的内容] | 高/中/低 | [効果] | [方法] |
| [機会3] | [具体的内容] | 高/中/低 | [効果] | [方法] |

**実現可能性の評価基準**:
- **高**: 自社の現有リソース・技術で即座に実行可能。競合優位性あり。成功事例多数。
- **中**: 追加投資・時間が必要だが実現可能。競合も狙える領域。リスクあり。
- **低**: 大規模投資・技術革新が必要。高リスク。他社も成功例少ない。

*楽観的すぎる評価は避け、現実的なリスク・障壁も併記すること*

## DATA_SOURCES

**必ず以下の形式で具体的な出典を明記**:

### 使用したデータソース

| データ項目 | 出典 | 詳細（ページ/URL） | 信頼性 |
|----------|------|------------------|--------|
| 市場規模 | [レポート名] | [ページ番号 or URL] | 高/中/低 |
| 売上推定 | [情報源] | [ページ番号 or URL] | 高/中/低 |
| DAU/MAU | [情報源] | [ページ番号 or URL] | 高/中/低 |
| CPI | [情報源] | [ページ番号 or URL] | 高/中/低 |

**記載例**:
- PDFデータの場合: 「ファミ通ゲーム白書2025 p.45-47」
- Webデータの場合: 「https://example.com/market-report」
- 組み込みデータの場合: 「2024年度国内ゲーム市場データ（提供データ）」
- 推測の場合: 「業界一般知識に基づく推測」

**データの信頼性について**:
- **高**: 公式発表、大手市場調査会社レポート、政府統計
- **中**: 業界推定、アナリストレポート、メディア報道
- **低**: 推測、一般的な業界知識、根拠不十分

**データが不足している項目**:
[該当する項目を明記し、推測であることを明示]

**重要**: すべてのデータについて、可能な限り具体的な出典を記載すること。ページ番号やURLがある場合は必ず含めること。
"""
                
                # ===== Claude を使うパターン =====
                if api_provider == "Claude (Anthropic)":
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    # モデルとtemperatureを選択
                    use_opus = "高精度" in claude_model_mode
                    selected_model = "claude-opus-4-20250514" if use_opus else "claude-sonnet-4-20250514"
                    selected_temperature = 0.1 if use_opus else 0.7
                    
                    # Opus 4使用時の通知
                    if use_opus:
                        st.info(f"🚀 {selected_model}（Opus 4）で分析を実行中...")
                    
                    # システムプロンプト（Opus 4使用時のみ）
                    system_prompt = None
                    if use_opus:
                        system_prompt = """あなたはゲーム業界の競合分析専門家です。

【絶対に守るべきルール】
1. すべての情報は必ずMarkdown表形式で出力すること
2. 表の形式: | 項目 | 値1 | 値2 | のように必ず縦棒(|)で区切ること
3. 箇条書き（-や•）は絶対に使用禁止
4. テキストのみの羅列は禁止
5. 自社タイトルのスコア・データも必ず記載すること（空欄禁止）
6. 新規タイトルの場合は「目標XX」「計画XX」という形で記載

このような表形式を必ず使用してください。テキストのみの出力は不可です。"""
                    
                    # API呼び出し
                    if system_prompt:
                        message = client.messages.create(
                            model=selected_model,
                            max_tokens=8000,
                            temperature=selected_temperature,
                            system=system_prompt,
                            messages=[{"role": "user", "content": prompt}]
                        )
                    else:
                        message = client.messages.create(
                            model=selected_model,
                            max_tokens=8000,
                            temperature=selected_temperature,
                            messages=[{"role": "user", "content": prompt}]
                        )
                    
                    result = message.content[0].text
                
                # ===== OpenAI を使うパターン =====
                else:
                    client = OpenAI(api_key=api_key)
                    
                    # Chat Completions API
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "あなたはゲーム業界の競合分析専門家です。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=8000
                    )
                    
                    result = response.choices[0].message.content
                
                st.success(f"■ 分析完了 ({api_provider})")
                st.markdown("---")
                
                # 結果を視覚化
                st.markdown("## ■ 分析結果")
                
                # エグゼクティブサマリー抽出（ダークモード対応）
                if "EXECUTIVE_SUMMARY" in result:
                    summary_start = result.find("EXECUTIVE_SUMMARY")
                    summary_end = result.find("##", summary_start + 1)
                    if summary_end == -1:
                        summary_end = len(result)
                    
                    summary_text = result[summary_start:summary_end].replace("EXECUTIVE_SUMMARY", "").strip()
                    
                    st.markdown(f"""
                    <div style="padding: 20px; border-radius: 10px; background-color: #1e3a5f; margin: 20px 0; border: 2px solid #4a90e2; color: white;">
                        <h3 style="color: #4a90e2; margin-top: 0;">■ エグゼクティブサマリー</h3>
                        <p style="color: white; line-height: 1.6;">{summary_text}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # JSONデータを抽出してレーダーチャート作成
                json_data_found = False
                if "```json" in result:
                    json_start = result.find("```json") + 7
                    json_end = result.find("```", json_start)
                    json_str = result[json_start:json_end].strip()
                    
                    try:
                        metrics_data = json.loads(json_str)
                        json_data_found = True
                        
                        # レーダーチャート作成
                        categories = ['市場ポジション', '収益性', 'ユーザー基盤', 'ブランド力', '技術力']
                        
                        fig = go.Figure()
                        
                        # 競合データ
                        fig.add_trace(go.Scatterpolar(
                            r=[
                                metrics_data['competitor']['market_position'],
                                metrics_data['competitor']['revenue_potential'],
                                metrics_data['competitor']['user_base'],
                                metrics_data['competitor']['brand_strength'],
                                metrics_data['competitor']['technology']
                            ],
                            theta=categories,
                            fill='toself',
                            name=competitor_name,
                            line=dict(color='#FF6B6B', width=2)
                        ))
                        
                        # 自社データ
                        fig.add_trace(go.Scatterpolar(
                            r=[
                                metrics_data['our_product']['market_position'],
                                metrics_data['our_product']['revenue_potential'],
                                metrics_data['our_product']['user_base'],
                                metrics_data['our_product']['brand_strength'],
                                metrics_data['our_product']['technology']
                            ],
                            theta=categories,
                            fill='toself',
                            name=our_product,
                            line=dict(color='#4ECDC4', width=2)
                        ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100],
                                    tickfont=dict(size=12)
                                )
                            ),
                            showlegend=True,
                            title={
                                'text': "■ 競合比較レーダーチャート（100点満点）",
                                'x': 0.5,
                                'xanchor': 'center'
                            },
                            height=500,
                            font=dict(size=14)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 比較テーブル
                        st.markdown("### ■ 詳細スコア比較")
                        
                        comparison_df = pd.DataFrame({
                            '評価項目': categories,
                            competitor_name: [
                                metrics_data['competitor']['market_position'],
                                metrics_data['competitor']['revenue_potential'],
                                metrics_data['competitor']['user_base'],
                                metrics_data['competitor']['brand_strength'],
                                metrics_data['competitor']['technology']
                            ],
                            our_product: [
                                metrics_data['our_product']['market_position'],
                                metrics_data['our_product']['revenue_potential'],
                                metrics_data['our_product']['user_base'],
                                metrics_data['our_product']['brand_strength'],
                                metrics_data['our_product']['technology']
                            ],
                            '差分': [
                                metrics_data['competitor']['market_position'] - metrics_data['our_product']['market_position'],
                                metrics_data['competitor']['revenue_potential'] - metrics_data['our_product']['revenue_potential'],
                                metrics_data['competitor']['user_base'] - metrics_data['our_product']['user_base'],
                                metrics_data['competitor']['brand_strength'] - metrics_data['our_product']['brand_strength'],
                                metrics_data['competitor']['technology'] - metrics_data['our_product']['technology']
                            ]
                        })
                        
                        # 差分に色をつける（ダークモード対応）
                        def highlight_diff(val):
                            if isinstance(val, (int, float)):
                                if val > 0:
                                    return 'background-color: #8B0000; color: white'
                                elif val < 0:
                                    return 'background-color: #006400; color: white'
                            return ''
                        
                        styled_df = comparison_df.style.applymap(highlight_diff, subset=['差分'])
                        st.dataframe(styled_df, use_container_width=True, height=250)
                        
                        # 各評価の根拠を表示
                        st.markdown("---")
                        st.markdown("### ■ 評価軸の定義")
                        
                        definition_text = """
| 評価軸 | 定義 |
|-------|------|
| **市場ポジション** | 市場での認知度・ランキング順位・ブランド力 |
| **収益性** | 年間売上規模・ARPU・課金効率・収益安定性<br>ライブサービス: 継続課金・イベント収益・長期ARPU<br>買い切り: 初回売上・DLC収益・周辺商品展開 |
| **ユーザー基盤** | DAU/MAU・ユーザー定着率・コミュニティ活性度 |
| **ブランド力** | IP価値・メディア露出・ファンロイヤリティ・二次展開力 |
| **技術力** | グラフィック品質・システム安定性・技術革新性・開発体制の強さ |
                        """
                        st.markdown(definition_text)
                        
                        st.markdown("---")
                        st.markdown("### ■ 各スコアの評価根拠")
                        st.info("各評価項目のスコアがどのような要素で構成されているかを確認できます")
                        
                        # 結果から根拠表を抽出
                        if "**各評価の根拠**" in result:
                            # 根拠表の開始位置を探す
                            rationale_start = result.find("**各評価の根拠**")
                            # 次のセクション（##）までを取得
                            rationale_end = result.find("##", rationale_start + 10)
                            if rationale_end == -1:
                                rationale_end = len(result)
                            
                            rationale_content = result[rationale_start:rationale_end].strip()
                            st.markdown(rationale_content)
                        else:
                            st.warning("● 評価根拠の詳細が見つかりませんでした")
                        
                    except (json.JSONDecodeError, KeyError) as e:
                        st.warning(f"● レーダーチャートの生成に失敗しました: {str(e)}")
                
                if not json_data_found:
                    st.warning("● レーダーチャート用のデータが見つかりませんでした")
                
                # 詳細分析結果
                st.markdown("---")
                tab1, tab2, tab3 = st.tabs(["■ 詳細分析", "■ エクスポート", "■ 市場データ"])
                
                with tab1:
                    # 表示用のresultを作成
                    display_result = result
                    
                    # COMPARISON_METRICSセクション全体を非表示
                    if "## COMPARISON_METRICS" in display_result:
                        metrics_start = display_result.find("## COMPARISON_METRICS")
                        metrics_end = display_result.find("##", metrics_start + 20)
                        if metrics_end == -1:
                            metrics_end = len(display_result)
                        display_result = display_result[:metrics_start] + display_result[metrics_end:]
                    
                    # セクション名だけのテキスト行を削除
                    for section_name in ['MARKET_ANALYSIS', 'COMPETITOR_ANALYSIS', 'GAP_ANALYSIS', 'ACTION_PLAN', 'RISK_OPPORTUNITY', 'DATA_SOURCES']:
                        display_result = display_result.replace(f"{section_name}\n\n", "")
                        display_result = display_result.replace(f"{section_name}\n", "")
                        display_result = display_result.replace(section_name, "")
                    
                    # セクションごとにBOX化
                    sections = display_result.split('##')
                    for section in sections:
                        if section.strip():
                            lines = section.strip().split('\n', 1)
                            if len(lines) == 2:
                                title = lines[0].strip()
                                content = lines[1].strip()
                                
                                if title in ['EXECUTIVE_SUMMARY']:
                                    continue
                                
                                st.markdown(f"""
                                <div style="padding: 15px; border-radius: 8px; background-color: #2d2d2d; margin: 15px 0; border-left: 4px solid #4a90e2;">
                                    <h3 style="color: #4a90e2; margin-top: 0;">■ {title}</h3>
                                    <div style="color: #e0e0e0;">
                                """, unsafe_allow_html=True)
                                
                                st.markdown(content)
                                
                                st.markdown("</div></div>", unsafe_allow_html=True)
                            else:
                                if section.strip() not in ['MARKET_ANALYSIS', 'COMPETITOR_ANALYSIS', 'GAP_ANALYSIS', 'ACTION_PLAN', 'RISK_OPPORTUNITY']:
                                    st.markdown(section)
                
                with tab2:
                    col_exp1, col_exp2 = st.columns(2)
                    
                    with col_exp1:
                        st.download_button(
                            label="▶ テキスト形式",
                            data=result,
                            file_name=f"{competitor_name}_analysis_{datetime.now().strftime('%Y%m%d')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col_exp2:
                        md_content = f"""# 競合分析レポート

**分析日**: {datetime.now().strftime('%Y年%m月%d日')}
**競合**: {competitor_name}
**自社**: {our_product}

---

{result}
"""
                        st.download_button(
                            label="▶ Markdown形式",
                            data=md_content,
                            file_name=f"{competitor_name}_analysis_{datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                
                with tab3:
                    st.markdown("### ■ 参照した市場データ")
                    
                    # DATA_SOURCESセクションを抽出して表示
                    if "## DATA_SOURCES" in result:
                        sources_start = result.find("## DATA_SOURCES")
                        sources_content = result[sources_start:]
                        
                        st.markdown("""
                        <div style="padding: 15px; border-radius: 8px; background-color: #1e3a5f; margin: 15px 0; border: 2px solid #4a90e2;">
                            <h4 style="color: #4a90e2; margin-top: 0;">📚 今回の分析で使用したデータソース</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # DATA_SOURCESの内容を表示（セクション名を除く）
                        sources_display = sources_content.replace("## DATA_SOURCES", "").strip()
                        st.markdown(sources_display)
                        
                        st.markdown("---")
                    
                    st.markdown("### ■ 組み込み市場データ（参考）")
                    st.markdown("""
                    <div style="padding: 15px; border-radius: 8px; background-color: #1a1a1a; border: 1px solid #4a90e2;">
                    """, unsafe_allow_html=True)
                    
                    st.code(MARKET_DATA, language="text")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"× {api_provider} APIエラー: {str(e)}")
                st.info("▶ トラブルシューティング: APIキーを確認してください")
                log_access(
                    st.session_state.get("username", "unknown"),
                    "analysis_error",
                    f"{api_provider} | エラー: {str(e)}"
                )

# 管理者用: アクセスログ表示
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
    st.markdown("**競合分析AI v2.7 (Dual Mode)**")
with col_f2:
    st.markdown(f"*Powered by {api_provider if 'api_provider' in locals() else 'AI'}*")
with col_f3:
    st.markdown(f"*{datetime.now().strftime('%Y/%m/%d')}*")
