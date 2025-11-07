# AI プロバイダー切り替えガイド

このプロジェクトは、複数の AI プロバイダーに対応しています。

## 現在の状況

- **Claude API (Anthropic)**: `/login` で作成された API キーは Claude Code 専用で、一般的な API 呼び出しには使用できません
- **OpenAI GPT-4**: 代替として準備済み

## OpenAI GPT-4 への切り替え手順

### 1. OpenAI API キーの取得

組織の承認プロセスを経て、OpenAI API キーを取得してください。

### 2. ローカル環境での設定

```bash
# OpenAI パッケージのインストール
pip install -r requirements_openai.txt

# 環境変数の設定
export OPENAI_API_KEY="your-openai-api-key-here"

# テスト実行
python scripts/monitor.py
python scripts/report_generator_openai.py
```

### 3. GitHub Secrets の設定

GitHub リポジトリの Settings → Secrets and variables → Actions で以下を設定:

- **Name**: `OPENAI_API_KEY`
- **Value**: 取得した OpenAI API キー

### 4. GitHub Actions ワークフローの修正

`.github/workflows/monitor.yml` を以下のように修正:

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements_openai.txt  # ← 変更

- name: Generate Japanese report
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}  # ← 変更
  run: |
    python scripts/report_generator_openai.py  # ← 変更
```

## ファイル対応表

| 用途 | Claude (元) | OpenAI (代替) |
|------|-------------|---------------|
| レポート生成スクリプト | `scripts/report_generator.py` | `scripts/report_generator_openai.py` |
| 依存パッケージ | `requirements.txt` | `requirements_openai.txt` |
| 環境変数 | `ANTHROPIC_API_KEY` | `OPENAI_API_KEY` |
| GitHub Secret | `ANTHROPIC_API_KEY` | `OPENAI_API_KEY` |

## 主な違い

### Claude API (Anthropic)
- モデル: `claude-sonnet-4-5-20250929`
- より自然な日本語生成
- 長文の理解に優れる

### OpenAI GPT-4
- モデル: `gpt-4-turbo-preview`
- 広く使われており、サポートが充実
- 組織での承認が得やすい

## トラブルシューティング

### エラー: "OPENAI_API_KEY environment variable is required"

環境変数が設定されていません:

```bash
export OPENAI_API_KEY="your-api-key"
```

GitHub Actions の場合は、Secrets に設定されているか確認してください。

### API レート制限エラー

OpenAI API には使用量制限があります。エラーが発生した場合:

1. API 使用状況を確認: https://platform.openai.com/usage
2. レート制限を確認: https://platform.openai.com/account/rate-limits
3. 必要に応じてプランをアップグレード

## その他の AI プロバイダー

将来的に他のプロバイダーへの対応も可能です:

- **Google Gemini**: Google Cloud で利用可能
- **Azure OpenAI**: Enterprise 向け
- **AWS Bedrock**: Claude を含む複数の LLM

必要に応じて、同様の手順でスクリプトを作成できます。

---

**最終更新**: 2025-11-07
