# 競合分析AI v2.1 (セキュア版)

ゲーム業界の競合タイトル分析ツール - Claude Sonnet 4搭載

## 🔐 セキュリティ機能

- ✅ **ベーシック認証**: ユーザー名とパスワードによる認証
- ✅ **アクセスログ**: すべての操作履歴を記録
- ✅ **複数ユーザー管理**: チームメンバー個別にアカウント設定
- ✅ **管理者ダッシュボード**: アクセスログ閲覧機能
- ✅ **セキュアなパスワード比較**: hmacを使用

## ✨ 機能

- 📊 インタラクティブなレーダーチャート比較
- 📈 市場データに基づく分析
- 🎯 2タイトル間の詳細比較表
- 📝 エクスポート機能（テキスト・Markdown）
- 🌙 ダークモード対応UI
- 🔒 エンタープライズグレードのセキュリティ

## 📋 必要な環境

- Python 3.8以上
- Claude API Key（Anthropic）
- Streamlit Cloud アカウント（本番デプロイ用）

## 🚀 クイックスタート

### ローカル開発環境

```bash
# 1. 依存関係インストール
pip install -r requirements.txt

# 2. 実行
streamlit run competitive_analysis_secure.py

# 3. ブラウザで http://localhost:8501 を開く

# 4. デフォルトアカウントでログイン
#    ユーザー名: admin
#    パスワード: krafton2024
```

### Streamlit Cloudデプロイ

詳細は `DEPLOY_GUIDE_SECURE.md` を参照してください。

## 👥 ユーザー管理

### デフォルトユーザー

Secrets未設定時は以下のアカウントが利用可能：

```
ユーザー名: admin
パスワード: krafton2024
```

### 本番環境用ユーザー設定

Streamlit CloudのSecrets設定：

```toml
# ユーザー認証
[users.admin]
password = "your_strong_password"
display_name = "管理者"

[users.your_name]
password = "another_password"
display_name = "あなたの名前"

# Claude API Key（必須）
ANTHROPIC_API_KEY = "sk-ant-api03-XXXXX"
```

**重要**: `ANTHROPIC_API_KEY`を必ず設定してください。設定しないとツールが動作しません。

詳細は `secrets.toml.sample` を参照。

## 📊 使い方

1. **ログイン**: ユーザー名とパスワードを入力
2. **API Key入力**: Claude API Keyを入力（または事前設定）
3. **タイトル情報入力**: 競合と自社の情報を入力
4. **分析実行**: ボタンをクリック
5. **結果確認**: レーダーチャートと詳細分析を確認
6. **エクスポート**: 必要に応じてレポートをダウンロード

## 🔧 技術スタック

- **Frontend**: Streamlit 1.28+
- **AI**: Anthropic Claude Sonnet 4
- **Visualization**: Plotly 5.18+
- **Data**: Pandas 2.0+
- **Security**: hmac (標準ライブラリ)

## 🗂️ ファイル構成

```
competitive-analysis-secure/
├── competitive_analysis_secure.py  # メインアプリ
├── requirements.txt                # 依存関係
├── .gitignore                      # Git除外設定
├── README.md                       # このファイル
├── DEPLOY_GUIDE_SECURE.md          # デプロイガイド
├── secrets.toml.sample             # Secrets設定サンプル
└── logs/                           # アクセスログ（自動生成）
    └── access_log.csv
```

## 🔒 セキュリティに関する注意事項

### ⚠️ 絶対にやってはいけないこと

- ❌ `secrets.toml`をGitにコミット
- ❌ パスワードをコードにハードコーディング
- ❌ デフォルトパスワードを本番環境で使用
- ❌ アクセスログを公開リポジトリにプッシュ

### ✅ 推奨事項

- ✅ 強力なパスワードを使用（12文字以上、英数字+記号）
- ✅ 定期的にパスワードを変更（3-6ヶ月ごと）
- ✅ アクセスログを定期的に確認
- ✅ 不要になったユーザーは即座に削除

## 🛠️ トラブルシューティング

### ログインできない

- Streamlit CloudのSecrets設定を確認
- ブラウザのキャッシュをクリア
- デフォルトアカウントを試す

### アクセスログが表示されない

- 管理者権限（`admin`ユーザー）でログイン
- `logs`ディレクトリの権限を確認

### レーダーチャートが表示されない

- Claude API Keyが正しいか確認
- JSONデータが正しく生成されているか確認（詳細分析タブ）

## 📝 変更履歴

### v2.1 (2025-01-07)
- 🔐 ベーシック認証機能追加
- 📊 アクセスログ記録機能追加
- 👥 複数ユーザー管理機能追加
- 🎨 表のスタイリング改善（ダークモード対応）
- 📋 2タイトル比較表形式に統一

### v2.0 (2025-01-06)
- 📊 レーダーチャート追加
- 🎨 UI/UX改善
- 📈 詳細分析機能強化

## 🤝 サポート

問題が発生した場合：

1. `DEPLOY_GUIDE_SECURE.md`のトラブルシューティングセクションを確認
2. アクセスログでエラー内容を確認
3. 社内のIT部門に連絡

## 📄 ライセンス

KRAFTON Japan 社内利用限定

## 🙏 謝辞

- Anthropic Claude API
- Streamlit
- Plotly
