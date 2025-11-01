#!/usr/bin/env python3
"""
連番PNGファイルをPDFに変換するスクリプト

使用例:
    python png_to_pdf.py -i /path/to/png/folder -o output.pdf
    python png_to_pdf.py -i /Users/fatowl/Desktop/KindleScreenshots/MyKindleBook -o book.pdf
    python png_to_pdf.py --input ./images --output combined.pdf --pattern "page_*.png"
"""

import os
import sys
import argparse
import glob
import re
from PIL import Image
import json

def natural_sort_key(text):
    """
    自然順序でソートするためのキー関数
    例: page_1.png, page_2.png, page_10.png の順序を正しく保つ
    """
    return [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', text)]

def find_png_files(input_folder, pattern="*.png"):
    """
    指定されたフォルダから連番PNGファイルを検索
    
    Args:
        input_folder (str): 検索対象のフォルダパス
        pattern (str): ファイル名パターン（デフォルト: "*.png"）
    
    Returns:
        list: ソートされたPNGファイルパスのリスト
    """
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"入力フォルダが見つかりません: {input_folder}")
    
    if not os.path.isdir(input_folder):
        raise NotADirectoryError(f"指定されたパスはフォルダではありません: {input_folder}")
    
    # パターンに基づいてファイルを検索
    search_pattern = os.path.join(input_folder, pattern)
    png_files = glob.glob(search_pattern)
    
    # PNGファイルのみをフィルタリング
    png_files = [f for f in png_files if f.lower().endswith('.png')]
    
    if not png_files:
        raise FileNotFoundError(f"PNGファイルが見つかりません: {search_pattern}")
    
    # 自然順序でソート
    png_files.sort(key=natural_sort_key)
    
    print(f"見つかったPNGファイル数: {len(png_files)}")
    print(f"最初のファイル: {os.path.basename(png_files[0])}")
    print(f"最後のファイル: {os.path.basename(png_files[-1])}")
    
    return png_files

def convert_png_to_pdf(png_files, output_pdf, quality=95, optimize=True):
    """
    PNGファイルリストをPDFに変換
    
    Args:
        png_files (list): PNGファイルパスのリスト
        output_pdf (str): 出力PDFファイルパス
        quality (int): JPEG品質（1-100、デフォルト: 95）
        optimize (bool): PDF最適化を行うか（デフォルト: True）
    """
    if not png_files:
        raise ValueError("変換するPNGファイルがありません")
    
    print(f"PDF変換を開始します...")
    print(f"出力ファイル: {output_pdf}")
    print(f"品質設定: {quality}")
    print(f"最適化: {'有効' if optimize else '無効'}")
    
    images = []
    failed_files = []
    
    for i, png_file in enumerate(png_files, 1):
        try:
            print(f"処理中 ({i}/{len(png_files)}): {os.path.basename(png_file)}")
            
            # 画像を開く
            img = Image.open(png_file)
            
            # RGBAモードの場合はRGBに変換（PDFはアルファチャンネルをサポートしない）
            if img.mode in ('RGBA', 'LA'):
                # 白い背景を作成
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[-1])  # アルファチャンネルをマスクとして使用
                else:
                    background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            images.append(img)
            
        except Exception as e:
            print(f"✗ エラー: {png_file} の読み込みに失敗しました: {e}")
            failed_files.append(png_file)
            continue
    
    if not images:
        raise RuntimeError("変換可能な画像がありませんでした")
    
    if failed_files:
        print(f"\n警告: {len(failed_files)}個のファイルの読み込みに失敗しました:")
        for failed_file in failed_files:
            print(f"  - {os.path.basename(failed_file)}")
    
    try:
        # PDFとして保存
        print(f"\nPDFファイルを作成中...")
        
        # 出力ディレクトリが存在しない場合は作成
        output_dir = os.path.dirname(output_pdf)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # 最初の画像を使ってPDFを作成し、残りの画像を追加
        images[0].save(
            output_pdf,
            save_all=True,
            append_images=images[1:],
            format='PDF',
            optimize=optimize,
            quality=quality
        )
        
        # ファイルサイズを確認
        if os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf)
            print(f"✓ PDF作成完了!")
            print(f"  ファイル: {output_pdf}")
            print(f"  サイズ: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
            print(f"  ページ数: {len(images)}")
        else:
            raise RuntimeError("PDFファイルが作成されませんでした")
            
    except Exception as e:
        raise RuntimeError(f"PDF作成に失敗しました: {e}")
    
    finally:
        # メモリを解放
        for img in images:
            img.close()

def load_config_for_pdf(config_file="config.json"):
    """
    設定ファイルからPDF変換用の設定を読み込む
    
    Args:
        config_file (str): 設定ファイルのパス
    
    Returns:
        dict: 設定辞書
    """
    default_config = {
        "output_folder": "/Users/fatowl/Desktop/KindleScreenshots",
        "book_title": "MyKindleBook",
        "pdf_output_folder": None,  # None の場合は入力フォルダと同じ場所
        "pdf_filename": None        # None の場合は book_title.pdf を使用
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                print(f"設定ファイル '{config_file}' を読み込みました")
        except Exception as e:
            print(f"設定ファイルの読み込みに失敗: {e}")
    
    return default_config

def parse_arguments():
    """
    コマンドライン引数を解析
    """
    parser = argparse.ArgumentParser(
        description="連番PNGファイルをPDFに変換するツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python png_to_pdf.py -i /path/to/png/folder -o output.pdf
  python png_to_pdf.py -i ./screenshots -o book.pdf --pattern "page_*.png"
  python png_to_pdf.py --config config.json -y  # 設定ファイルから自動設定（確認なし）
  python png_to_pdf.py -i /Users/fatowl/Desktop/KindleScreenshots/MyKindleBook -o MyBook.pdf -y
        """
    )
    
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="PNGファイルが格納されているフォルダパス"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="出力PDFファイルのパス"
    )
    
    parser.add_argument(
        "-p", "--pattern",
        type=str,
        default="*.png",
        help="ファイル名パターン（デフォルト: *.png）"
    )
    
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=95,
        choices=range(1, 101),
        metavar="1-100",
        help="PDF品質（1-100、デフォルト: 95）"
    )
    
    parser.add_argument(
        "--no-optimize",
        action="store_true",
        help="PDF最適化を無効にする"
    )
    
    parser.add_argument(
        "-c", "--config",
        type=str,
        default="config.json",
        help="設定ファイルのパス（デフォルト: config.json）"
    )
    
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="確認プロンプトをスキップして自動実行"
    )
    
    return parser.parse_args()

def main():
    """
    メイン処理
    """
    try:
        # コマンドライン引数を解析
        args = parse_arguments()
        
        # 設定ファイルを読み込み
        config = load_config_for_pdf(args.config)
        
        # 入力フォルダの決定
        if args.input:
            input_folder = args.input
        else:
            # 設定ファイルから自動設定
            input_folder = os.path.join(config["output_folder"], config["book_title"])
            print(f"設定ファイルから入力フォルダを自動設定: {input_folder}")
        
        # 出力ファイルの決定
        if args.output:
            output_pdf = args.output
        else:
            # 設定ファイルからPDF出力設定を取得
            pdf_output_folder = config.get("pdf_output_folder")
            pdf_filename = config.get("pdf_filename")
            book_title = config.get("book_title", "converted_book")
            
            # ファイル名の決定
            if pdf_filename:
                filename = pdf_filename
            else:
                filename = f"{book_title}.pdf"
            
            # 出力フォルダの決定
            if pdf_output_folder:
                output_pdf = os.path.join(pdf_output_folder, filename)
                print(f"PDF出力フォルダを設定ファイルから取得: {pdf_output_folder}")
            else:
                # PDF出力フォルダが指定されていない場合は、入力フォルダと同じ場所
                output_pdf = filename
                print(f"PDF出力フォルダが未指定のため、カレントディレクトリに出力")
            
            print(f"出力ファイル名を自動設定: {output_pdf}")
        
        print("=" * 60)
        print("PNG → PDF 変換ツール")
        print("=" * 60)
        print(f"入力フォルダ: {input_folder}")
        print(f"出力ファイル: {output_pdf}")
        print(f"ファイルパターン: {args.pattern}")
        print(f"品質設定: {args.quality}")
        print(f"最適化: {'無効' if args.no_optimize else '有効'}")
        print("=" * 60)
        
        # PNGファイルを検索
        png_files = find_png_files(input_folder, args.pattern)
        
        # 確認プロンプト（--yesオプションでスキップ可能）
        print(f"\n{len(png_files)}個のPNGファイルをPDFに変換します。")
        if not args.yes:
            response = input("続行しますか？ (y/N): ").strip().lower()
            if response not in ['y', 'yes', 'はい']:
                print("変換をキャンセルしました。")
                return
        else:
            print("自動実行モードで続行します。")
        
        # PDF変換を実行
        convert_png_to_pdf(
            png_files=png_files,
            output_pdf=output_pdf,
            quality=args.quality,
            optimize=not args.no_optimize
        )
        
        print("\n" + "=" * 60)
        print("✓ 変換が正常に完了しました！")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("✗ ユーザーによって処理が中断されました。")
        print("=" * 60)
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ エラーが発生しました: {e}")
        print(f"エラータイプ: {type(e).__name__}")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
