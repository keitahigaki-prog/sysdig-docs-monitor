# Sysdig Documentation Monitor

Sysdigドキュメントの更新を自動監視し、Claude AIを使用してお客様向けの日本語レポートを生成するシステムです。

## 📋 機能

- **RSSフィード監視**: 6種類のSysdig RSSフィードを監視
  - Agent Release Notes
  - Serverless Agent Release Notes
  - Monitor SaaS Release Notes
  - Secure SaaS Release Notes
  - On-Premises Release Notes
  - Falco Rules Release Notes

- **Webページ監視**: 重要なドキュメントページを監視
  - Linux Host Shield Release Notes
  - Deprecation/EOL Information

- **AI解析**: Claude APIを使用して変更内容を解析
  - 重要度の自動判定（Critical/High/Medium/Low）
  - 技術内容の日本語要約
  - お客様への影響分析
  - 推奨アクションの提示

- **自動レポート生成**: Markdownフォーマットで読みやすいレポートを生成

## 🏗️ アーキテクチャ

```
sysdig-docs-monitor/
├── .github/
│   └── workflows/
│       └── monitor.yml          # GitHub Actionsワークフロー（毎日実行）
├── scripts/
│   ├── monitor.py               # ドキュメント監視スクリプト
│   └── report_generator.py      # Claude API使用レポート生成
├── data/                         # 監視データ保存（Gitで管理）
│   ├── latest.json              # 最新の監視結果
│   └── changes_*.json           # 変更検出履歴
├── reports/                      # 生成されたレポート（Gitで管理）
│   └── sysdig_report_*.md       # 日本語レポート
├── requirements.txt              # Python依存パッケージ
└── README.md                     # このファイル
```

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/YOUR_USERNAME/sysdig-docs-monitor.git
cd sysdig-docs-monitor
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

Claude APIキーを取得して環境変数に設定:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 4. GitHub Secretsの設定

GitHubリポジトリの Settings → Secrets and variables → Actions で以下を設定:

- `ANTHROPIC_API_KEY`: Claude APIキー

## 💻 使い方

### ローカルで実行

```bash
# 監視実行
python scripts/monitor.py

# レポート生成（監視実行後）
python scripts/report_generator.py
```

### GitHub Actionsでの自動実行

- **自動実行**: 毎日0:00 UTC（日本時間9:00 AM）に自動実行
- **手動実行**: GitHub ActionsタブからWorkflowを手動トリガー可能

### レポートの確認

1. **GitHubリポジトリ**: `reports/` ディレクトリにコミットされます
2. **GitHub Artifacts**: Actions実行結果から90日間ダウンロード可能

## 📊 レポート例

```markdown
# Sysdig ドキュメント監視レポート

**レポート日時:** 2025年11月7日 09:00:00
**変更検出:** あり ⚠️

---

## エグゼクティブサマリー

本日の監視で2件の重要な更新を検出しました...

---

## 📡 RSSフィード更新情報

### [High] Secure SaaS Release - バージョン 7.8.0

**概要:**
新しい脅威検知機能とパフォーマンス改善が含まれています...

**お客様への影響:**
- 既存環境への影響は最小限
- 新機能の活用により、セキュリティポスチャが向上

**推奨アクション:**
- リリースノート全文の確認
- 検証環境でのテスト実施

---
```

## 🔧 カスタマイズ

### 監視頻度の変更

`.github/workflows/monitor.yml` の `cron` を編集:

```yaml
schedule:
  - cron: '0 */6 * * *'  # 6時間ごとに実行
```

### 監視対象の追加

`scripts/monitor.py` の `rss_feeds` または `web_urls` に追加:

```python
self.web_urls = {
    "host_shield": "https://docs.sysdig.com/...",
    "new_page": "https://docs.sysdig.com/your-new-page/",  # 追加
}
```

### レポート形式の変更

`scripts/report_generator.py` の `system_prompt` を編集して、Claude AIの分析スタイルを調整できます。

## 📈 監視データの履歴

- `data/latest.json`: 最新の監視結果
- `data/changes_YYYYMMDD_HHMMSS.json`: 変更検出時のスナップショット
- すべてGitで管理され、変更履歴を追跡可能

## 🛠️ トラブルシューティング

### エラー: "ANTHROPIC_API_KEY environment variable is required"

Claude APIキーが設定されていません:

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

GitHubの場合は、Secretsに設定されているか確認してください。

### エラー: "No monitoring data found"

`monitor.py` を先に実行してください:

```bash
python scripts/monitor.py
python scripts/report_generator.py
```

### レポートが生成されない

1. `data/latest.json` が存在するか確認
2. APIキーが正しく設定されているか確認
3. ログを確認してエラー内容を特定

## 📝 ライセンス

MIT License

## 🤝 貢献

Pull Requestを歓迎します！

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📮 お問い合わせ

質問や提案がありましたら、Issueを作成してください。

---

**生成日**: 2025-11-07
**バージョン**: 1.0.0
