#!/usr/bin/env python3
"""
重複画像削除スクリプト
同一ディレクトリ内のPNGファイルから重複する画像を削除します。
画像の一致度は構造的類似性指数（SSIM）を使用して99%程度で判定します。
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import argparse
from datetime import datetime

import numpy as np

from utils.image_utils import load_and_resize_image, calculate_similarity


class DuplicateImageRemover:
    def __init__(self, directory: str, similarity_threshold: float = 0.99, backup: bool = True):
        """
        重複画像削除クラス
        
        Args:
            directory: 対象ディレクトリのパス
            similarity_threshold: 類似度の閾値（0.0-1.0）
            backup: 削除前にバックアップを作成するかどうか
        """
        self.directory = Path(directory)
        self.similarity_threshold = similarity_threshold
        self.backup = backup
        self.backup_dir = None
        
        if not self.directory.exists():
            raise ValueError(f"ディレクトリが存在しません: {directory}")
    
    def create_backup_directory(self) -> Path:
        """バックアップディレクトリを作成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.directory / f"backup_duplicates_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        self.backup_dir = backup_dir
        return backup_dir
    
    def get_png_files(self) -> List[Path]:
        """ディレクトリ内のPNGファイルを取得"""
        png_files = list(self.directory.glob("*.png"))
        png_files.extend(self.directory.glob("*.PNG"))
        return sorted(png_files)
    
    
    def find_duplicates(self) -> Dict[str, List[Path]]:
        """
        重複画像を検出
        
        Returns:
            重複グループの辞書（キー: 代表ファイル名、値: 重複ファイルのリスト）
        """
        png_files = self.get_png_files()
        
        if len(png_files) < 2:
            print("比較対象のPNGファイルが2つ未満です。")
            return {}
        
        print(f"{len(png_files)}個のPNGファイルを検査中...")
        
        # 画像を読み込み
        images = {}
        for file_path in png_files:
            img_array = load_and_resize_image(file_path)
            if img_array is not None:
                images[file_path] = img_array
            else:
                print(f"スキップ: {file_path}")
        
        # 重複グループを検出
        duplicate_groups = {}
        processed = set()
        
        file_list = list(images.keys())
        total_comparisons = len(file_list) * (len(file_list) - 1) // 2
        comparison_count = 0
        
        for i, file1 in enumerate(file_list):
            if file1 in processed:
                continue
                
            duplicates = []
            
            for j, file2 in enumerate(file_list[i+1:], i+1):
                comparison_count += 1
                if comparison_count % 100 == 0:
                    print(f"進捗: {comparison_count}/{total_comparisons} 比較完了")
                
                if file2 in processed:
                    continue
                
                similarity = calculate_similarity(images[file1], images[file2])
                
                if similarity >= self.similarity_threshold:
                    duplicates.append(file2)
                    processed.add(file2)
            
            if duplicates:
                duplicate_groups[str(file1)] = duplicates
                processed.add(file1)
        
        return duplicate_groups
    
    def remove_duplicates(self, duplicate_groups: Dict[str, List[Path]], dry_run: bool = False) -> int:
        """
        重複画像を削除
        
        Args:
            duplicate_groups: 重複グループ
            dry_run: 実際には削除せず、削除対象のみ表示
            
        Returns:
            削除されたファイル数
        """
        if not duplicate_groups:
            print("重複画像は見つかりませんでした。")
            return 0
        
        total_duplicates = sum(len(duplicates) for duplicates in duplicate_groups.values())
        
        if dry_run:
            print(f"\n=== ドライラン: {total_duplicates}個のファイルが削除対象です ===")
            for original, duplicates in duplicate_groups.items():
                print(f"\n保持: {Path(original).name}")
                for duplicate in duplicates:
                    print(f"  削除対象: {duplicate.name}")
            return total_duplicates
        
        # バックアップディレクトリを作成
        if self.backup:
            backup_dir = self.create_backup_directory()
            print(f"バックアップディレクトリ: {backup_dir}")
        
        deleted_count = 0
        
        print(f"\n=== {total_duplicates}個の重複ファイルを削除中 ===")
        
        for original, duplicates in duplicate_groups.items():
            print(f"\n保持: {Path(original).name}")
            
            for duplicate in duplicates:
                try:
                    # バックアップ
                    if self.backup:
                        backup_path = backup_dir / duplicate.name
                        shutil.copy2(duplicate, backup_path)
                        print(f"  バックアップ: {duplicate.name}")
                    
                    # 削除
                    duplicate.unlink()
                    print(f"  削除完了: {duplicate.name}")
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"  削除失敗: {duplicate.name} - {e}")
        
        return deleted_count
    
    def run(self, dry_run: bool = False) -> int:
        """
        重複画像削除を実行
        
        Args:
            dry_run: 実際には削除せず、削除対象のみ表示
            
        Returns:
            削除されたファイル数
        """
        print(f"ディレクトリ: {self.directory}")
        print(f"類似度閾値: {self.similarity_threshold:.1%}")
        print(f"バックアップ: {'有効' if self.backup else '無効'}")
        print("-" * 50)
        
        # 重複を検出
        duplicate_groups = self.find_duplicates()
        
        # 重複を削除
        deleted_count = self.remove_duplicates(duplicate_groups, dry_run)
        
        if not dry_run and deleted_count > 0:
            print(f"\n完了: {deleted_count}個のファイルを削除しました。")
            if self.backup:
                print(f"削除されたファイルは {self.backup_dir} にバックアップされています。")
        
        return deleted_count


def main():
    parser = argparse.ArgumentParser(
        description="同一ディレクトリ内のPNGファイルから重複する画像を削除します。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 現在のディレクトリで重複画像を検出（削除はしない）
  python remove_duplicate_images.py --dry-run
  
  # 指定ディレクトリで重複画像を削除（位置引数）
  python remove_duplicate_images.py /path/to/images
  
  # 指定ディレクトリで重複画像を削除（オプション引数）
  python remove_duplicate_images.py -d /path/to/images
  
  # 類似度90%で重複を判定
  python remove_duplicate_images.py --threshold 0.9
  
  # ディレクトリと類似度を両方指定
  python remove_duplicate_images.py -d /path/to/images -t 0.95
  
  # バックアップなしで削除
  python remove_duplicate_images.py --no-backup
        """
    )
    
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="対象ディレクトリのパス（デフォルト: 現在のディレクトリ）"
    )
    
    parser.add_argument(
        "-d", "--directory",
        dest="target_directory",
        help="対象ディレクトリのパス（位置引数と同じ機能）"
    )
    
    parser.add_argument(
        "-t", "--threshold",
        type=float,
        default=0.99,
        help="類似度の閾値（0.0-1.0、デフォルト: 0.99）"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="実際には削除せず、削除対象のみ表示"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="削除前のバックアップを作成しない"
    )
    
    args = parser.parse_args()
    
    # ディレクトリの決定（-d オプションが指定されていれば優先）
    target_dir = args.target_directory if args.target_directory else args.directory
    
    # 引数の検証
    if not 0.0 <= args.threshold <= 1.0:
        print("エラー: 類似度閾値は0.0から1.0の間で指定してください。")
        sys.exit(1)
    
    try:
        # 重複画像削除を実行
        remover = DuplicateImageRemover(
            directory=target_dir,
            similarity_threshold=args.threshold,
            backup=not args.no_backup
        )
        
        deleted_count = remover.run(dry_run=args.dry_run)
        
        if args.dry_run:
            print(f"\nドライラン完了: {deleted_count}個のファイルが削除対象です。")
            print("実際に削除するには --dry-run オプションを外して再実行してください。")
        
    except KeyboardInterrupt:
        print("\n処理が中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
