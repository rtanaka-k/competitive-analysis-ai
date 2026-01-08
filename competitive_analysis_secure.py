# -*- coding: utf-8 -*-
import streamlit as st
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
    page_title="競合分析AI v2.1",
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
        st.title("競合分析AI v2.1")
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
    st.title("競合分析AI v2.1")
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
    api_key = st.text_input("Claude API Key", type="password")
    
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
    1. API Keyを入力
    2. 競合情報を入力
    3. 分析実行
    4. インタラクティブなグラフで確認
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
        st.error("● Claude API Keyを入力してください")
    elif not competitor_name or not our_product:
        st.error("● 競合タイトル名と自社タイトル名を入力してください")
    else:
        # アクセスログ記録
        log_access(
            st.session_state.get("username", "unknown"),
            "analysis_executed",
            f"競合:{competitor_name} vs 自社:{our_product}"
        )
        
        with st.spinner("市場データを分析中... (60-90秒)"):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                
                # プロンプト構築（前回と同じ内容）
                prompt = f"""
あなたはゲーム業界の競合分析専門家です。以下の市場データと情報を基に詳細な分析を実施してください。

{MARKET_DATA}

{reference_data}

【分析対象】
■ 競合タイトル
- タイトル名: {competitor_name}
- ジャンル: {competitor_genre}
- プラットフォーム: {', '.join(competitor_platform)}

■ 自社タイトル
- タイトル名: {our_product}
- ジャンル: {our_genre}
- プラットフォーム: {', '.join(our_platform)}

【分析タイプ】: {analysis_type}
【比較観点】: {', '.join(comparison_focus)}

【特記事項】
{additional_context if additional_context else "特になし"}

---

**【重要指示】以下を必ず守ってください:**
1. COMPARISON_METRICSは必ずJSON形式（```json ... ```）で出力
2. 全てのセクションで必ず表形式（Markdownテーブル）を使用
3. 箇条書き（-や•）は使用禁止
4. セクション名（MARKET_ANALYSIS、COMPETITOR_ANALYSIS等）を単独行で出力しない（必ず## セクション名の形式）

以下の形式で回答してください。**必ず数値データを引用**してください:

## EXECUTIVE_SUMMARY
*3-5行で結論と最重要ポイント簡潔に記載*

## COMPARISON_METRICS
**必ず以下の正確なJSON形式で出力**:
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

## MARKET_ANALYSIS
### 市場規模とトレンド

**必ず以下の表形式で出力（箇条書き禁止）**:

| 項目 | {competitor_name} | {our_product} |
|------|-------------------|---------------|
| 推定年間売上 | XXX億円（データ参照） | XXX億円（目標/推定） |
| 市場ランキング | TOP XX（RPG内） | TOP XX（目標） |
| DAU/MAU | XX万人/XX万人 | XX万人/XX万人（目標） |
| 主要ターゲット層 | XX代XX性 | XX代XX性 |
| 市場シェア | X.X% | X.X%（目標） |

*上記市場データから該当情報を引用し、具体的数値を記載*

### ジャンル特性

**必ず以下の表形式で出力（箇条書き禁止）**:

| 特性項目 | {competitor_name} | {our_product} |
|----------|-------------------|---------------|
| ジャンル適合度 | 高/中/低 + 理由 | 高/中/低 + 理由 |
| 差別化ポイント | 具体的特徴 | 具体的特徴 |
| CPI（ユーザー獲得単価） | XXX円 | XXX円（推定） |
| 主要収益モデル | [ガチャ/サブスク等] | [想定モデル] |

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

## DATA_SOURCES
*引用したデータソースを明記*
"""
                
                # API呼び出し
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result = message.content[0].text
                
                st.success("■ 分析完了")
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
                    st.markdown("""
                    <div style="padding: 15px; border-radius: 8px; background-color: #1a1a1a; border: 1px solid #4a90e2;">
                    """, unsafe_allow_html=True)
                    
                    st.code(MARKET_DATA, language="text")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"× エラー: {str(e)}")
                st.info("▶ トラブルシューティング: APIキーを確認してください")
                log_access(
                    st.session_state.get("username", "unknown"),
                    "analysis_error",
                    f"エラー: {str(e)}"
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
    st.markdown("**競合分析AI v2.1 (Secure)**")
with col_f2:
    st.markdown("*Powered by Claude Sonnet 4*")
with col_f3:
    st.markdown(f"*{datetime.now().strftime('%Y/%m/%d')}*")
