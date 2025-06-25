# セキュリティガイド - プライベート利用のための設定

## 🔒 アクセス制限の方法

### 1. ローカル環境での利用（最も安全）

```bash
# ローカルネットワーク内のみでアクセス
streamlit run app.py

# 外部からのアクセスを完全にブロック
streamlit run app.py --server.address localhost
```

### 2. Streamlit Cloudでのプライベート利用

#### パスワード保護の設定

1. **`.streamlit/secrets.toml`を作成**（ローカル）:
```toml
password = "your-very-strong-password-here-12345!"
```

2. **Streamlit Cloudの設定**:
   - アプリをデプロイ後、Settings → Secrets
   - 上記の内容を貼り付け

3. **アクセス時**:
   - URLを知っていてもパスワードが必要
   - パスワードなしではダッシュボードにアクセス不可

#### 追加のセキュリティ対策

1. **URL を推測困難にする**:
   - リポジトリ名をランダムに（例: `analytics-x7k9m2`）
   - 公開リポジトリリストから除外

2. **GitHub リポジトリをプライベートに**:
   ```bash
   # GitHubでプライベートリポジトリとして作成
   # Streamlit CloudはプライベートリポジトリもサポートOK
   ```

### 3. VPN経由でのアクセス（企業向け）

自宅や会社のVPNを使用：
1. VPNサーバーを設定
2. ローカルでStreamlitを起動
3. VPN経由でのみアクセス可能

### 4. 自宅サーバーでのホスティング

```bash
# Dockerを使用した例
docker run -d \
  -p 8501:8501 \
  -v $(pwd):/app \
  --name analytics \
  python:3.11 \
  bash -c "cd /app && pip install -r requirements.txt && streamlit run app.py"
```

## 🛡️ API キーの保護

### やってはいけないこと
- ❌ GitHubにAPIキーをコミット
- ❌ 公開URLでパスワードなし運用
- ❌ 本番用APIキーをテスト環境で使用

### 推奨事項
- ✅ 環境ごとに異なるAPIキー使用
- ✅ 定期的なAPIキーのローテーション
- ✅ 最小権限の原則（読み取り専用キーを使用）
- ✅ IPアドレス制限（可能な場合）

## 🔐 Streamlit Cloudでの安全な設定手順

1. **初回セットアップ**:
```bash
# ローカルでパスワードを設定
echo 'password = "SuperSecurePassword123!"' > .streamlit/secrets.toml

# .gitignoreに追加されていることを確認
cat .gitignore | grep secrets.toml
```

2. **デプロイ後**:
   - Streamlit Cloud管理画面 → Settings → Secrets
   - パスワードを設定
   - Save

3. **アクセステスト**:
   - ブラウザのプライベートモードで確認
   - パスワードなしでアクセスできないことを確認

## 📊 利用状況の監視

Streamlit Cloudでは以下が確認可能：
- アクセスログ
- 使用状況統計
- エラーログ

定期的に確認して不正アクセスがないかチェックしましょう。

## 🚨 セキュリティインシデント時の対応

1. **即座に実行**:
   - 全APIキーの無効化
   - Streamlitアプリの停止
   - パスワードの変更

2. **調査**:
   - アクセスログの確認
   - 不正利用の範囲特定

3. **復旧**:
   - 新しいAPIキーの発行
   - パスワードの再設定
   - アプリの再デプロイ

## 💡 おすすめの構成

個人利用の場合：
1. **開発/テスト**: ローカル環境
2. **本番**: Streamlit Cloud + パスワード保護
3. **バックアップ**: 定期的なデータエクスポート

これで安全にプライベート利用できます！