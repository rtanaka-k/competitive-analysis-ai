# 🚨 緊急セキュリティ対応ガイド

## ❌ GitHub Secret Scanning 警告への対応

GitHubがAPI Keyを検出した場合、**絶対に「Allow Secret」を選択しないでください**。

---

## ✅ 今すぐ実行すること（5分以内）

### Step 1: API Keyを無効化 🔴

#### Claude (Anthropic)
1. https://console.anthropic.com/settings/keys にアクセス
2. 該当するAPI Keyを見つける
3. **「Delete」をクリック**
4. 新しいKeyを作成

#### OpenAI
1. https://platform.openai.com/api-keys にアクセス
2. 該当するAPI Keyを見つける
   - 警告に表示されているKeyの先頭部分で検索
3. **「Revoke」ボタンをクリック**
4. 新しいKeyを作成

---

### Step 2: ファイルから削除 🗑️

#### 削除が必要なファイル

```bash
# これらのファイルをコミットしない
secrets.toml
secrets.toml.sample（実際のKeyが含まれている場合）
CODE_FIX_SUMMARY.md（実際のKeyが含まれている場合）
```

#### 確認方法

```bash
# 実際のKeyが含まれているか確認
git diff HEAD

# 含まれている場合は削除
git reset HEAD secrets.toml.sample
git checkout -- secrets.toml.sample
```

---

### Step 3: .gitignoreを確認 📝

`.gitignore`に以下が含まれているか確認：

```
# 機密情報
.streamlit/
secrets.toml
.env
*api_key*
*API_KEY*
*.pem
*.key
```

---

### Step 4: Git履歴から削除（重要！）⚠️

既にコミット済みの場合：

```bash
# 方法1: 最新コミットから削除（まだpushしていない場合）
git reset --soft HEAD~1
# ファイルを修正
git add .
git commit -m "Remove sensitive data"

# 方法2: 履歴から完全に削除（既にpushした場合）
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch secrets.toml.sample" \
  --prune-empty --tag-name-filter cat -- --all

# 強制push（⚠️ 注意: チームで共有している場合は事前連絡）
git push origin --force --all
```

---

## 🛡️ 今後の予防策

### 1. Streamlit Secrets機能を使用

```python
# ❌ 絶対にダメ
api_key = "sk-proj-xxxxx"

# ✅ 正しい方法
import streamlit as st
api_key = st.secrets["OPENAI_API_KEY"]
```

### 2. .gitignoreを徹底

```bash
# 必ず.gitignoreに追加
echo "secrets.toml" >> .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore"
```

### 3. Pre-commit hookを設定

```bash
# .git/hooks/pre-commit を作成
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
if git diff --cached | grep -E "(sk-|pk-|api_key|API_KEY)"; then
    echo "⚠️  API Key detected in commit! Aborting."
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

### 4. 環境変数を使用

```bash
# .env ファイル（.gitignoreに追加）
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-proj-xxxxx

# コードで読み込み
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

---

## 📊 被害を確認

### OpenAI Usage確認

1. https://platform.openai.com/usage にアクセス
2. 不正な使用がないか確認
3. 異常なスパイクがあれば即座にSupport連絡

### 請求額確認

1. https://platform.openai.com/account/billing/overview
2. 予期しない請求がないか確認

---

## 🚨 もし不正利用されていたら

### Step 1: OpenAI Supportに連絡

https://help.openai.com/en/

**件名**: "API Key Compromised - Request for Billing Review"

**本文**:
```
My API key was accidentally exposed on GitHub.
I have revoked the key immediately.

Could you please review any unusual activity and 
consider waiving charges from unauthorized use?

Key ID: [無効化したKeyのID]
Exposure period: [日時]
```

### Step 2: 課金制限を設定

https://platform.openai.com/account/limits

- **Usage limits**を設定
- **Notification alerts**を有効化

---

## ✅ チェックリスト

- [ ] API Keyを即座に無効化した
- [ ] 新しいAPI Keyを作成した
- [ ] ファイルから実際のKeyを削除した
- [ ] .gitignoreを確認・更新した
- [ ] Git履歴から削除した（必要な場合）
- [ ] Streamlit Secretsに新しいKeyを設定した
- [ ] 不正使用がないか確認した
- [ ] 今後の予防策を実装した

---

## 📞 緊急連絡先

- **OpenAI Support**: https://help.openai.com/
- **Anthropic Support**: support@anthropic.com
- **GitHub Support**: https://support.github.com/

---

## 💡 重要な教訓

```
API Key = クレジットカード番号と同じ

✅ Streamlit Secrets
✅ 環境変数
✅ .gitignore

❌ コードに直接書く
❌ GitHubにコミット
❌ 「後で消す」（消し忘れる）
```

---

**作成日**: 2026年1月16日  
**重要度**: 🔴 最高  
**対応時間**: ⏰ 5分以内
