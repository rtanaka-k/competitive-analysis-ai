# OpenAI Vector Store セットアップガイド

## 📚 Vector Storeとは

OpenAI の Vector Store は、アップロードしたファイル（PDFなど）をAIが検索・参照できるようにする機能です。

### メリット
- ファミ通白書などのPDFをアップロードして、AIがその内容を参照できる
- 毎回PDFをアップロードする必要がない
- より正確なデータに基づいた分析が可能

---

## 🔧 セットアップ手順

### Step 1: OpenAI Platformにアクセス

https://platform.openai.com/

### Step 2: Vector Storeを作成

1. 左メニューから「Storage」→「Vector Stores」を選択
2. 「+ Create vector store」ボタンをクリック
3. 名前を設定（例: `KRAFTON_Market_Data`）
4. Expiration policy: `Never expire`（推奨）
5. 「Create」をクリック

### Step 3: ファイルをアップロード

1. 作成したVector Storeを開く
2. 「Add files」ボタンをクリック
3. 以下のファイルをアップロード:
   - ファミ通ゲーム白書2025.pdf
   - ファミ通モバイルゲーム白書2025.pdf
   - JOGAオンラインゲーム市場調査レポート（各年度）
   - その他の市場データ

### Step 4: Vector Store IDを取得

1. Vector Storeのページ上部にIDが表示されています
   - 例: `vs_abc123def456ghi789`
2. このIDをコピー

### Step 5: Streamlit Secretsに設定

`secrets.toml`に以下を追加:

```toml
OPENAI_VECTOR_STORE_ID = "vs_abc123def456ghi789"
```

---

## 💡 使用方法

### 現在の実装（基本版）

```python
# OpenAI Chat Completions API
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "あなたはゲーム業界の競合分析専門家です。"},
        {"role": "user", "content": prompt}
    ]
)
```

### Vector Store統合版（今後の実装）

```python
# Assistants API + Vector Store
assistant = client.beta.assistants.create(
    model="gpt-4-turbo",
    tools=[{"type": "file_search"}],
    tool_resources={
        "file_search": {
            "vector_store_ids": [vector_store_id]
        }
    }
)

thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=prompt
)

run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id
)
```

---

## 📊 ファイルフォーマット

### サポートされるファイル形式
- PDF
- TXT
- MD
- DOC/DOCX
- XLS/XLSX
- CSV

### ファイルサイズ制限
- 最大: 512 MB per file
- Vector Store全体: 100 GB

---

## 💰 コストについて

### Vector Store料金
- **Storage**: $0.10 / GB / day
- **Usage**: $0.20 / GB processed

### 例: 5つのPDF（各10MB）
- Total size: 50MB = 0.05GB
- Storage cost: $0.005 / day = $0.15 / month
- Processing (初回のみ): $0.01

**非常に安価です！**

---

## 🔄 更新方法

### 新しいファイルを追加

```python
# Pythonスクリプトで追加
file = client.files.create(
    file=open("new_report.pdf", "rb"),
    purpose="assistants"
)

client.beta.vector_stores.files.create(
    vector_store_id=vector_store_id,
    file_id=file.id
)
```

### または、Web UIから

1. Vector Storeページを開く
2. 「Add files」でアップロード

---

## ⚠️ 注意事項

### セキュリティ
- アップロードしたファイルはOpenAIのサーバーに保存されます
- 機密情報を含むファイルは慎重に扱ってください
- 社内の情報セキュリティポリシーを確認してください

### パフォーマンス
- 初回アップロード時はインデックス作成に時間がかかります（数分程度）
- 大量のファイルをアップロードすると検索精度が下がる可能性があります
- 推奨: 10-20ファイル程度

---

## 🚀 次のステップ

1. ✅ Vector Storeを作成
2. ✅ ファミ通白書などをアップロード
3. ✅ IDをStreamlit Secretsに設定
4. ⏳ アプリケーションでAssistants APIを実装（今後）

---

## 📝 トラブルシューティング

### Q: Vector Store IDが見つからない
A: https://platform.openai.com/storage/vector_stores で確認

### Q: ファイルがアップロードできない
A: ファイルサイズ（最大512MB）とフォーマットを確認

### Q: 検索結果が不正確
A: ファイルのテキスト抽出品質を確認（スキャンPDFは不可）

### Q: コストが心配
A: 月額数十円程度です。料金ダッシュボードで確認できます

---

## 📚 参考リンク

- OpenAI Platform: https://platform.openai.com/
- Vector Stores Documentation: https://platform.openai.com/docs/assistants/tools/file-search
- Assistants API Guide: https://platform.openai.com/docs/assistants/overview
- Pricing: https://openai.com/pricing

---

**作成日**: 2026年1月16日
**バージョン**: 1.0
