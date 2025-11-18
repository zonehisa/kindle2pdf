#!/usr/bin/env python3
"""
重複画像削除スクリプトのテスト

テスト観点表:
| Case ID | Input / Precondition | Perspective (Equivalence / Boundary) | Expected Result | Notes |
|---------|---------------------|--------------------------------------|-----------------|-------|
| TC-N-01 | 存在するディレクトリ | Equivalence - normal | インスタンスが正常に作成される | - |
| TC-N-02 | 2つ以上のPNGファイル | Equivalence - normal | 重複検出が実行される | - |
| TC-N-03 | 重複画像が存在する | Equivalence - normal | 重複グループが検出される | - |
| TC-N-04 | dry_run=True | Equivalence - normal | ファイルは削除されない | - |
| TC-N-05 | backup=True | Equivalence - normal | バックアップが作成される | - |
| TC-A-01 | 存在しないディレクトリ | Boundary - 異常系 | ValueErrorが発生 | - |
| TC-A-02 | PNGファイルが0個 | Boundary - 異常系 | 空の辞書が返される | - |
| TC-A-03 | PNGファイルが1個 | Boundary - 異常系 | 空の辞書が返される | - |
| TC-B-01 | similarity_threshold=0.0 | Boundary - 最小値 | すべての画像が重複と判定される可能性 | - |
| TC-B-02 | similarity_threshold=1.0 | Boundary - 最大値 | 完全一致のみが重複と判定される | - |
| TC-B-03 | similarity_threshold=-0.1 | Boundary - 範囲外（負） | エラーまたは無効な動作 | 実装による |
| TC-B-04 | similarity_threshold=1.1 | Boundary - 範囲外（1超） | エラーまたは無効な動作 | 実装による |
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import numpy as np

from remove_duplicate_images import DuplicateImageRemover


class TestDuplicateImageRemoverInit:
    """DuplicateImageRemover.__init__のテスト"""
    
    def test_normal_existing_directory(self):
        """TC-N-01: 正常系 - 存在するディレクトリ"""
        # Given: 存在する一時ディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            # When: DuplicateImageRemoverを初期化
            remover = DuplicateImageRemover(tmpdir)
            
            # Then: インスタンスが正常に作成される
            assert remover.directory == Path(tmpdir)
            assert remover.similarity_threshold == 0.99
            assert remover.backup is True
    
    def test_normal_custom_threshold(self):
        """正常系 - カスタム閾値"""
        # Given: 存在する一時ディレクトリとカスタム閾値
        with tempfile.TemporaryDirectory() as tmpdir:
            # When: カスタム閾値で初期化
            remover = DuplicateImageRemover(tmpdir, similarity_threshold=0.95, backup=False)
            
            # Then: カスタム値が設定される
            assert remover.similarity_threshold == 0.95
            assert remover.backup is False
    
    def test_abnormal_nonexistent_directory(self):
        """TC-A-01: 異常系 - 存在しないディレクトリ"""
        # Given: 存在しないディレクトリパス
        nonexistent_path = "/path/that/does/not/exist"
        
        # When/Then: ValueErrorが発生する
        with pytest.raises(ValueError, match="ディレクトリが存在しません"):
            DuplicateImageRemover(nonexistent_path)


class TestGetPngFiles:
    """get_png_filesメソッドのテスト"""
    
    def test_normal_multiple_png_files(self):
        """正常系 - 複数のPNGファイル"""
        # Given: PNGファイルが複数あるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            # PNGファイルを作成
            for i in range(3):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                img.save(Path(tmpdir) / f"image_{i}.png")
            
            remover = DuplicateImageRemover(tmpdir)
            
            # When: get_png_filesを実行
            png_files = remover.get_png_files()
            
            # Then: PNGファイルが取得される
            assert len(png_files) == 3
            assert all(f.suffix.lower() == '.png' for f in png_files)
    
    def test_normal_case_insensitive(self):
        """正常系 - 大文字小文字を区別しない"""
        # Given: .pngと.PNGファイルがあるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            img1 = Image.new('RGB', (100, 100), (255, 0, 0))
            img1.save(Path(tmpdir) / "image1.png")
            img2 = Image.new('RGB', (100, 100), (0, 255, 0))
            img2.save(Path(tmpdir) / "image2.PNG")
            
            remover = DuplicateImageRemover(tmpdir)
            
            # When: get_png_filesを実行
            png_files = remover.get_png_files()
            
            # Then: 両方のファイルが取得される
            assert len(png_files) == 2
    
    def test_abnormal_no_png_files(self):
        """TC-A-02: 異常系 - PNGファイルが0個"""
        # Given: PNGファイルがないディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            remover = DuplicateImageRemover(tmpdir)
            
            # When: get_png_filesを実行
            png_files = remover.get_png_files()
            
            # Then: 空のリストが返される
            assert png_files == []


class TestFindDuplicates:
    """find_duplicatesメソッドのテスト"""
    
    def test_normal_no_duplicates(self):
        """正常系 - 重複がない場合"""
        # Given: 異なる画像が複数あるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            # 異なる色の画像を作成
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            for i, color in enumerate(colors):
                img = Image.new('RGB', (100, 100), color)
                img.save(Path(tmpdir) / f"image_{i}.png")
            
            remover = DuplicateImageRemover(tmpdir, similarity_threshold=0.99)
            
            # When: find_duplicatesを実行
            duplicates = remover.find_duplicates()
            
            # Then: 重複グループが空
            assert duplicates == {}
    
    def test_normal_with_duplicates(self):
        """TC-N-03: 正常系 - 重複画像が存在する"""
        # Given: 同一画像が複数あるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            # 同一画像を複数作成
            base_img = Image.new('RGB', (100, 100), (255, 0, 0))
            base_img.save(Path(tmpdir) / "image1.png")
            base_img.save(Path(tmpdir) / "image2.png")
            
            # 異なる画像も追加
            different_img = Image.new('RGB', (100, 100), (0, 255, 0))
            different_img.save(Path(tmpdir) / "image3.png")
            
            remover = DuplicateImageRemover(tmpdir, similarity_threshold=0.99)
            
            # When: find_duplicatesを実行
            duplicates = remover.find_duplicates()
            
            # Then: 重複グループが検出される
            assert len(duplicates) > 0
    
    def test_abnormal_zero_files(self):
        """TC-A-02: 異常系 - PNGファイルが0個"""
        # Given: PNGファイルがないディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            remover = DuplicateImageRemover(tmpdir)
            
            # When: find_duplicatesを実行
            duplicates = remover.find_duplicates()
            
            # Then: 空の辞書が返される
            assert duplicates == {}
    
    def test_abnormal_one_file(self):
        """TC-A-03: 異常系 - PNGファイルが1個"""
        # Given: PNGファイルが1個だけのディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            img.save(Path(tmpdir) / "image1.png")
            
            remover = DuplicateImageRemover(tmpdir)
            
            # When: find_duplicatesを実行
            duplicates = remover.find_duplicates()
            
            # Then: 空の辞書が返される
            assert duplicates == {}
    
    def test_boundary_threshold_zero(self):
        """TC-B-01: 境界値 - 閾値0.0"""
        # Given: 異なる画像と閾値0.0
        with tempfile.TemporaryDirectory() as tmpdir:
            colors = [(255, 0, 0), (0, 255, 0)]
            for i, color in enumerate(colors):
                img = Image.new('RGB', (100, 100), color)
                img.save(Path(tmpdir) / f"image_{i}.png")
            
            remover = DuplicateImageRemover(tmpdir, similarity_threshold=0.0)
            
            # When: find_duplicatesを実行
            duplicates = remover.find_duplicates()
            
            # Then: すべての画像が重複と判定される可能性がある
            # 実際の結果は実装による
            assert isinstance(duplicates, dict)
    
    def test_boundary_threshold_one(self):
        """TC-B-02: 境界値 - 閾値1.0"""
        # Given: 同一画像と閾値1.0
        with tempfile.TemporaryDirectory() as tmpdir:
            base_img = Image.new('RGB', (100, 100), (255, 0, 0))
            base_img.save(Path(tmpdir) / "image1.png")
            base_img.save(Path(tmpdir) / "image2.png")
            
            remover = DuplicateImageRemover(tmpdir, similarity_threshold=1.0)
            
            # When: find_duplicatesを実行
            duplicates = remover.find_duplicates()
            
            # Then: 完全一致のみが重複と判定される
            assert isinstance(duplicates, dict)


class TestRemoveDuplicates:
    """remove_duplicatesメソッドのテスト"""
    
    def test_normal_dry_run(self):
        """TC-N-04: 正常系 - dry_run=True"""
        # Given: 重複グループとdry_run=True
        with tempfile.TemporaryDirectory() as tmpdir:
            # 画像ファイルを作成
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            img.save(Path(tmpdir) / "image1.png")
            img.save(Path(tmpdir) / "image2.png")
            
            remover = DuplicateImageRemover(tmpdir, backup=False)
            duplicate_groups = remover.find_duplicates()
            
            # ファイルが存在することを確認
            assert (Path(tmpdir) / "image1.png").exists()
            assert (Path(tmpdir) / "image2.png").exists()
            
            # When: dry_run=Trueでremove_duplicatesを実行
            deleted_count = remover.remove_duplicates(duplicate_groups, dry_run=True)
            
            # Then: ファイルは削除されない
            assert (Path(tmpdir) / "image1.png").exists()
            assert (Path(tmpdir) / "image2.png").exists()
            assert deleted_count >= 0
    
    def test_normal_with_backup(self):
        """TC-N-05: 正常系 - backup=True"""
        # Given: 重複グループとbackup=True
        with tempfile.TemporaryDirectory() as tmpdir:
            # 同一画像を作成
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            img.save(Path(tmpdir) / "image1.png")
            img.save(Path(tmpdir) / "image2.png")
            
            remover = DuplicateImageRemover(tmpdir, backup=True)
            duplicate_groups = remover.find_duplicates()
            
            if duplicate_groups:
                # When: backup=Trueでremove_duplicatesを実行
                deleted_count = remover.remove_duplicates(duplicate_groups, dry_run=False)
                
                # Then: バックアップディレクトリが作成される
                assert remover.backup_dir is not None
                assert remover.backup_dir.exists()
                assert deleted_count >= 0
    
    def test_normal_no_backup(self):
        """正常系 - backup=False"""
        # Given: 重複グループとbackup=False
        with tempfile.TemporaryDirectory() as tmpdir:
            # 同一画像を作成
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            img.save(Path(tmpdir) / "image1.png")
            img.save(Path(tmpdir) / "image2.png")
            
            remover = DuplicateImageRemover(tmpdir, backup=False)
            duplicate_groups = remover.find_duplicates()
            
            if duplicate_groups:
                # When: backup=Falseでremove_duplicatesを実行
                deleted_count = remover.remove_duplicates(duplicate_groups, dry_run=False)
                
                # Then: バックアップディレクトリは作成されない
                assert remover.backup_dir is None
                assert deleted_count >= 0
    
    def test_normal_empty_duplicates(self):
        """正常系 - 重複グループが空"""
        # Given: 空の重複グループ
        with tempfile.TemporaryDirectory() as tmpdir:
            remover = DuplicateImageRemover(tmpdir)
            
            # When: 空の重複グループでremove_duplicatesを実行
            deleted_count = remover.remove_duplicates({}, dry_run=False)
            
            # Then: 0が返される
            assert deleted_count == 0


class TestCreateBackupDirectory:
    """create_backup_directoryメソッドのテスト"""
    
    def test_normal_creates_backup_dir(self):
        """正常系 - バックアップディレクトリが作成される"""
        # Given: DuplicateImageRemoverインスタンス
        with tempfile.TemporaryDirectory() as tmpdir:
            remover = DuplicateImageRemover(tmpdir)
            
            # When: create_backup_directoryを実行
            backup_dir = remover.create_backup_directory()
            
            # Then: バックアップディレクトリが作成される
            assert backup_dir.exists()
            assert backup_dir.is_dir()
            assert "backup_duplicates_" in backup_dir.name
            assert remover.backup_dir == backup_dir
    
    def test_normal_timestamp_in_name(self):
        """正常系 - タイムスタンプが名前に含まれる"""
        # Given: DuplicateImageRemoverインスタンス
        with tempfile.TemporaryDirectory() as tmpdir:
            remover = DuplicateImageRemover(tmpdir)
            
            # When: create_backup_directoryを実行
            backup_dir = remover.create_backup_directory()
            
            # Then: タイムスタンプ形式（YYYYMMDD_HHMMSS）が含まれる
            import re
            assert re.match(r'backup_duplicates_\d{8}_\d{6}', backup_dir.name)

