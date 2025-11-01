# Kindless - Kindle スクリーンショット自動化ツール

Kindle本のスクリーンショットを自動で撮影し、PDFに変換するPythonツールです。

## 概要

このツールは以下の機能を提供します：

1. **kindless.py** - Kindleアプリのスクリーンショットを自動撮影
2. **png_to_pdf.py** - 撮影したPNGファイルをPDFに変換
3. **remove_duplicate_images.py** - 重複画像を自動検出・削除

## 必要な環境

- Python 3.6以上（**Python 3.13は非対応**）
- macOS / Windows / Linux対応
- Kindleアプリ（デスクトップ版）

### Python バージョンに関する注意

⚠️ **Python 3.13では動作しません**

このツールはPython 3.13では正常に動作しないことが確認されています。以下のバージョンでの使用を推奨します：

- **推奨**: Python 3.8 〜 3.12
- **最小要件**: Python 3.6以上
- **非対応**: Python 3.13以降

## インストール

1. リポジトリをクローンまたはダウンロード
2. 仮想環境を作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows
```

3. 必要なパッケージをインストール
```bash
# 方法1: requirements.txtを使用（推奨）
pip install -r requirements.txt

# 方法2: 個別にインストール
pip install pyautogui pillow scikit-image
```

## 設定

`config.json`ファイルで設定をカスタマイズできます：

```json
{
    "output_folder": "/Users/username/Desktop/KindleScreenshots",
    "book_title": "本のタイトル",
    "page_delay": 2,
    "num_pages": 100,
    "pdf_output_folder": "/Users/username/Desktop/PDFs",
    "pdf_filename": null,
    "similarity_threshold": 0.99
}
```

### 設定項目の説明

| 項目 | 説明 | デフォルト値 | 範囲・形式 |
|------|------|-------------|-----------|
| `output_folder` | スクリーンショットの保存先フォルダ | `~/Documents` | フォルダパス |
| `book_title` | 本のタイトル（サブフォルダ名として使用） | `"KindleBook"` | 文字列 |
| `page_delay` | ページめくり後の待機時間（秒） | `2` | 1-10 |
| `num_pages` | キャプチャするページ数 | `100` | 1-2000 |
| `pdf_output_folder` | PDF出力先フォルダ | `null`（カレントディレクトリ） | フォルダパス |
| `pdf_filename` | PDF出力ファイル名 | `null`（book_title.pdf） | ファイル名 |
| `similarity_threshold` | 重複画像判定の類似度閾値 | `0.99` | 0.0-1.0 |

#### 画像一致度閾値について

`similarity_threshold`は重複画像を検出する際の類似度閾値です：

- **0.99（推奨）**: 非常に高精度。ほぼ同一の画像のみを重複と判定
- **0.95**: 高精度。わずかな違いがある画像も重複と判定
- **0.90**: 中精度。より多くの類似画像を重複と判定
- **0.85以下**: 低精度。異なる画像も重複と誤判定する可能性が高い

**注意**: 値を下げすぎると、異なるページの画像も重複として削除される可能性があります。

## 使用方法

### 統合パイプライン（推奨）

全ての処理を一度に実行する統合スクリプトが利用できます：

```bash
# 全ての処理を順番に実行（スクリーンショット → 重複削除 → PDF変換）
python kindle2pdf.py

# ドライランモード（実際の処理は行わず、計画のみ表示）
python kindle2pdf.py --dry-run

# スクリーンショットをスキップして重複削除とPDF変換のみ実行
python kindle2pdf.py --skip-screenshots

# 重複削除をスキップ
python kindle2pdf.py --skip-duplicates

# カスタム設定ファイルを使用
python kindle2pdf.py --config my_config.json
```

#### 統合パイプラインの特徴

- **自動化**: 3つの処理を順番に自動実行
- **設定ファイル連携**: `config.json`から全ての設定を自動読み込み
- **エラーハンドリング**: 各ステップでのエラー検出と適切な停止
- **進捗表示**: 各ステップの実行状況を詳細表示
- **柔軟性**: 必要に応じて特定のステップをスキップ可能
- **ドライラン**: 実際の処理前に実行計画を確認

### 個別スクリプトの使用方法

#### 1. スクリーンショット撮影

```bash
python kindless.py -t "本のタイトル" -p 100 -d 2
```

オプション：
- `-t, --title`: 本のタイトル（保存フォルダ名）
- `-p, --pages`: キャプチャするページ数
- `-d, --delay`: ページめくり後の待機時間（秒）
- `-o, --output`: 出力フォルダのパス
- `-c, --config`: 設定ファイルのパス

#### 2. PDF変換

```bash
python png_to_pdf.py -i /path/to/screenshots -o output.pdf
```

オプション：
- `-i, --input`: PNGファイルが格納されているフォルダ
- `-o, --output`: 出力PDFファイルのパス
- `-p, --pattern`: ファイル名パターン（デフォルト: *.png）
- `-q, --quality`: PDF品質（1-100、デフォルト: 95）
- `-y, --yes`: 確認プロンプトをスキップ

#### 3. 重複画像削除

```bash
python remove_duplicate_images.py --dry-run
```

基本的な使用方法：
```bash
# 現在のディレクトリで重複画像を検出（削除はしない）
python remove_duplicate_images.py --dry-run

# 指定ディレクトリで重複画像を削除
python remove_duplicate_images.py -d /path/to/images

# 類似度90%で重複を判定
python remove_duplicate_images.py -t 0.9

# ディレクトリと類似度を両方指定
python remove_duplicate_images.py -d /path/to/images -t 0.95

# バックアップなしで削除
python remove_duplicate_images.py --no-backup
```

オプション：
- `directory`: 対象ディレクトリのパス（位置引数）
- `-d, --directory`: 対象ディレクトリのパス（オプション引数）
- `-t, --threshold`: 類似度の閾値（0.0-1.0、デフォルト: 0.99）
- `--dry-run`: 実際には削除せず、削除対象のみ表示
- `--no-backup`: 削除前のバックアップを作成しない

##### 重複画像削除の特徴

- **高精度判定**: SSIM（構造的類似性指数）による99%精度の重複判定
- **安全機能**: 削除前の自動バックアップ（`backup_duplicates_YYYYMMDD_HHMMSS`フォルダ）
- **ドライラン機能**: `--dry-run`で削除対象を事前確認
- **進捗表示**: 大量ファイル処理時の進捗状況表示
- **RGBA対応**: 透明度付き画像も適切に処理

## ⚠️ 重要な注意点

### 権限設定（macOS）

macOSでは以下の権限設定が必要です：

1. **システム環境設定** → **セキュリティとプライバシー** → **プライバシー**
2. **「画面録画」** でPythonまたはターミナルを許可
3. **「アクセシビリティ」** でPythonまたはターミナルを許可
4. 設定変更後、ターミナルを再起動

### 権限設定（Windows）

- 管理者権限でコマンドプロンプトまたはPowerShellを実行
- ウイルス対策ソフトがpyautoguiをブロックしていないか確認
- Windows Defenderの例外設定を確認

### 使用上の注意

1. **フェイルセーフ機能**: マウスを画面左上角に移動すると処理が停止します
2. **Kindleアプリの準備**: 撮影開始前にKindleアプリを開き、最初のページを表示してください
3. **画面の妨害禁止**: 撮影中は他のアプリケーションを操作しないでください
4. **ページめくり方法**: 
   - macOS: スペースキー → 右矢印キー → 画面右側クリック
   - Windows: 右矢印キー → スペースキー → 画面右側クリック → PageDownキー
5. **連続エラー**: 3回連続でエラーが発生すると自動停止します
6. **無限ループ防止**: 2000ページを超えると強制終了します

### パス指定時の注意（重要）

⚠️ **チルダ（~）の使用について**

コマンドライン引数でパスを指定する際は、以下の点にご注意ください：

```bash
# ❌ 間違った例（チルダが正しく展開されない場合があります）
python png_to_pdf.py --input ~/Documents/BookTitle --output ~/Documents/BookTitle.pdf

# ✅ 正しい例（絶対パスを使用）
python png_to_pdf.py --input /Users/username/Documents/BookTitle --output /Users/username/Documents/BookTitle.pdf

# ✅ または相対パスを使用
python png_to_pdf.py --input ../Documents/BookTitle --output ../Documents/BookTitle.pdf
```

**問題の詳細:**
- チルダ（`~`）がPythonスクリプト内で正しく展開されない場合、ファイルが予期しない場所に保存される可能性があります
- 例：`~/Documents/file.pdf` → `./~/Documents/file.pdf`（現在のディレクトリ下に`~`フォルダが作成される）

**推奨される対処法:**
1. **絶対パス**を使用する（最も確実）
2. **相対パス**を使用する
3. 設定ファイル（`config.json`）で事前にパスを設定する

### ファイル形式とサイズ

- スクリーンショット: PNG形式
- 出力PDF: RGB形式（アルファチャンネルは白背景に変換）
- ファイル名: `page_0001.png`, `page_0002.png`...の連番形式

## トラブルシューティング

### よくあるエラー

1. **Python 3.13互換性エラー**: Python 3.12以下のバージョンを使用してください
2. **権限エラー**: 上記の権限設定を確認してください
3. **ページめくり失敗**: Kindleアプリがアクティブか確認してください
4. **ファイル保存エラー**: 出力フォルダの書き込み権限を確認してください
5. **PDF変換エラー**: PNGファイルが破損していないか確認してください
6. **重複画像削除エラー**: scikit-imageライブラリがインストールされているか確認してください

### Python バージョン確認方法

現在のPythonバージョンを確認するには：

```bash
python --version
# または
python3 --version
```

Python 3.13を使用している場合は、以下の方法で適切なバージョンをインストールしてください：

```bash
# pyenvを使用する場合（推奨）
pyenv install 3.12.0
pyenv local 3.12.0

# または仮想環境で特定のバージョンを指定
python3.12 -m venv venv
```

### デバッグ情報

エラーが発生した場合、以下の情報が表示されます：
- エラータイプ
- ファイルパス
- ファイルサイズ
- OS情報

## ライセンス

このプロジェクトは個人利用を目的としています。商用利用や著作権で保護されたコンテンツの無断複製は禁止されています。

## 免責事項

- このツールの使用は自己責任で行ってください
- 著作権法を遵守して使用してください
- 商用利用や配布は著作権者の許可を得てください
- 開発者は本ツールの使用による一切の損害について責任を負いません
