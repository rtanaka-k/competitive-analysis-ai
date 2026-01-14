# 競合分析AI v2.1 (セキュア版) - デプロイガイド

## 🔐 セキュリティ機能

- **ベーシック認証**: ユーザー名とパスワードによる認証
- **アクセスログ**: すべての操作を記録
- **ユーザー管理**: 複数ユーザーの個別管理
- **管理者機能**: アクセスログ閲覧

## 📦 必要なファイル

1. `competitive_analysis_secure.py` - メインアプリ（セキュリティ統合済み）
2. `requirements.txt` - 依存関係リスト
3. `.gitignore` - Git除外設定
4. `README.md` - ドキュメント
5. `secrets.toml.sample` - Secrets設定サンプル

## 🚀 Streamlit Cloudへのデプロイ

### ステップ1: GitHubリポジトリ作成

```bash
# 1. 作業ディレクトリに移動
cd "C:\Users\r.tanaka\OneDrive - KRAFTON\デスクトップ\Python_script"

# 2. Git初期化
git init

# 3. ファイルを追加
git add competitive_analysis_secure.py requirements.txt .gitignore README.md

# 4. コミット
git commit -m "Initial commit: 競合分析AI v2.1 (セキュア版)"

# 5. メインブランチに変更
git branch -M main

# 6. リモートリポジトリ追加
git remote add origin https://github.com/YOUR_USERNAME/competitive-analysis-secure.git

# 7. プッシュ
git push -u origin main
```

### ステップ2: Streamlit Cloudでデプロイ

1. https://share.streamlit.io/ にアクセス
2. GitHubアカウントでサインイン
3. 「New app」をクリック
4. 以下を設定:
   - **Repository**: YOUR_USERNAME/competitive-analysis-secure
   - **Branch**: main
   - **Main file path**: competitive_analysis_secure.py
5. 「Deploy!」をクリック

### ステップ3: Secrets設定（重要！）

アプリのダッシュボードで：

1. **Settings** → **Secrets**
2. `secrets.toml.sample`の内容をコピー
3. パスワードを実際の値に変更
4. 以下のように貼り付け:

```toml
# ユーザー認証設定
[users.admin]
password = "your_strong_password_123"
display_name = "管理者"

[users.tanaka]
password = "tanaka_password_456"
display_name = "田中"

[users.sjha]
password = "sjha_password_789"
display_name = "Jha"

[users.moriya]
password = "moriya_password_abc"
display_name = "森谷"

[users.kuyeon]
password = "kuyeon_password_def"
display_name = "Kuyeon"

# Claude API Key（必須）
ANTHROPIC_API_KEY = "sk-ant-api03-XXXXX"
```

5. **Save**をクリック

**重要**: `ANTHROPIC_API_KEY`は必須です。設定しないとツールが動作しません。

### ステップ4: 動作確認

1. デプロイ完了後、URLにアクセス
2. ログイン画面が表示されることを確認
3. テストアカウントでログイン:
   - ユーザー名: `admin`
   - パスワード: Secretsで設定した値

## 🔑 デフォルト認証

Secretsが未設定の場合、以下のデフォルトアカウントが使用できます：

```
ユーザー名: admin
パスワード: krafton2024
```

**本番環境では必ずSecretsを設定してください！**

## 📊 管理者機能

管理者アカウント（`admin`）でログインすると：

1. サイドバーに「管理者機能」セクションが表示
2. 「アクセスログを表示」ボタンをクリック
3. 全ユーザーの操作履歴を確認可能

### アクセスログの内容

- **timestamp**: 操作日時
- **username**: ユーザー名
- **display_name**: 表示名
- **action**: 操作内容（login, analysis_executed, logout等）
- **details**: 詳細情報

## 🔄 ユーザーの追加方法

Streamlit CloudのSecrets設定に追加：

```toml
[users.new_user]
password = "new_password_123"
display_name = "新規ユーザー"
```

保存すると即座に反映されます（再デプロイ不要）。

## 🆘 トラブルシューティング

### ログインできない

1. Secretsが正しく設定されているか確認
2. パスワードにスペースや特殊文字が含まれていないか確認
3. ブラウザのキャッシュをクリア

### アクセスログが表示されない

1. `logs`ディレクトリが作成されているか確認
2. 管理者権限でログインしているか確認

### Secretsの更新が反映されない

1. Streamlit Cloudで「Reboot app」を実行
2. 数分待ってから再度アクセス

## 🔒 セキュリティのベストプラクティス

1. **強力なパスワード**: 最低12文字、英数字+記号
2. **定期的な変更**: 3-6ヶ月ごとにパスワード更新
3. **アクセスログ監視**: 定期的に不審なアクティビティをチェック
4. **最小権限の原則**: 必要なユーザーにのみアクセス権を付与

## 📝 ログファイルの管理

アクセスログは`logs/access_log.csv`に保存されます。

定期的にバックアップを取ることを推奨します：

```bash
# ローカル開発環境の場合
cp logs/access_log.csv logs/access_log_backup_$(date +%Y%m%d).csv
```

## ⚠️ 注意事項

- Secretsファイルは**絶対にGitにコミットしない**
- `.gitignore`に`secrets.toml`が含まれていることを確認
- 本番環境ではデフォルトパスワードを必ず変更

## 🎉 完了！

これで、セキュアな競合分析AIツールのデプロイが完了です。

チームメンバーにURLとログイン情報を共有してください。
