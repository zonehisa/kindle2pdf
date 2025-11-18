#!/usr/bin/env python3
"""
PNG→JPG変換スクリプトのテスト

テスト観点表:
| Case ID | Input / Precondition | Perspective (Equivalence / Boundary) | Expected Result | Notes |
|---------|---------------------|--------------------------------------|-----------------|-------|
| TC-N-01 | 有効なPNGファイル | Equivalence - normal | JPGファイルが作成される | - |
| TC-N-02 | RGB画像 | Equivalence - normal | 正常に変換される | - |
| TC-N-03 | RGBA画像 | Equivalence - normal | RGBに変換されてJPGが作成される | - |
| TC-N-04 | output_folder指定 | Equivalence - normal | 指定フォルダにJPGが保存される | - |
| TC-N-05 | delete_original=True | Equivalence - normal | 元のPNGファイルが削除される | - |
| TC-N-06 | quality=95 | Equivalence - normal | 指定品質で変換される | - |
| TC-A-01 | 存在しないPNGファイル | Boundary - 異常系 | Noneが返される | - |
| TC-A-02 | 存在しない入力フォルダ | Boundary - 異常系 | FileNotFoundErrorが発生 | - |
| TC-A-03 | ファイルパス（フォルダではない） | Boundary - 異常系 | NotADirectoryErrorが発生 | - |
| TC-A-04 | PNGファイルが0個 | Boundary - 異常系 | FileNotFoundErrorが発生 | - |
| TC-B-01 | quality=1 | Boundary - 最小値 | 最低品質で変換される | - |
| TC-B-02 | quality=100 | Boundary - 最大値 | 最高品質で変換される | - |
| TC-B-03 | quality=0 | Boundary - 範囲外（負） | エラーまたは無効な動作 | 実装による |
| TC-B-04 | quality=101 | Boundary - 範囲外（100超） | エラーまたは無効な動作 | 実装による |
"""

import pytest
import tempfile
import os
from pathlib import Path
from PIL import Image

from png_to_jpg import (
    find_png_files,
    convert_png_to_jpg,
    convert_folder
)


class TestFindPngFiles:
    """find_png_files関数のテスト"""
    
    def test_normal_multiple_png_files(self):
        """TC-N-01: 正常系 - 複数のPNGファイル"""
        # Given: 複数のPNGファイルがあるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                img.save(Path(tmpdir) / f"image_{i}.png")
            
            # When: find_png_filesを実行
            png_files = find_png_files(tmpdir)
            
            # Then: PNGファイルが取得される
            assert len(png_files) == 3
            assert all(f.endswith('.png') for f in png_files)
    
    def test_normal_sorted_order(self):
        """正常系 - 自然順序でソートされる"""
        # Given: 連番のPNGファイル
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in [1, 2, 10]:
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                img.save(Path(tmpdir) / f"image_{i}.png")
            
            # When: find_png_filesを実行
            png_files = find_png_files(tmpdir)
            
            # Then: 正しい順序でソートされる（1, 2, 10の順）
            assert len(png_files) == 3
            assert 'image_1.png' in png_files[0]
            assert 'image_10.png' in png_files[2]
    
    def test_abnormal_nonexistent_folder(self):
        """TC-A-02: 異常系 - 存在しない入力フォルダ"""
        # Given: 存在しないフォルダパス
        nonexistent_path = "/path/that/does/not/exist"
        
        # When/Then: FileNotFoundErrorが発生
        with pytest.raises(FileNotFoundError, match="入力フォルダが見つかりません"):
            find_png_files(nonexistent_path)
    
    def test_abnormal_not_a_directory(self):
        """TC-A-03: 異常系 - ファイルパス（フォルダではない）"""
        # Given: ファイルパス
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # When/Then: NotADirectoryErrorが発生
            with pytest.raises(NotADirectoryError, match="指定されたパスはフォルダではありません"):
                find_png_files(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_abnormal_no_png_files(self):
        """TC-A-04: 異常系 - PNGファイルが0個"""
        # Given: PNGファイルがないディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            # When/Then: FileNotFoundErrorが発生
            with pytest.raises(FileNotFoundError, match="PNGファイルが見つかりません"):
                find_png_files(tmpdir)


class TestConvertPngToJpg:
    """convert_png_to_jpg関数のテスト"""
    
    def test_normal_rgb_image(self):
        """TC-N-02: 正常系 - RGB画像"""
        # Given: RGB PNGファイル
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            png_path = Path(tmpdir) / "test.png"
            img.save(png_path)
            
            # When: convert_png_to_jpgを実行
            jpg_path = convert_png_to_jpg(str(png_path))
            
            # Then: JPGファイルが作成される
            assert jpg_path is not None
            assert os.path.exists(jpg_path)
            assert jpg_path.endswith('.jpg')
            
            # JPGファイルが読み込めることを確認
            jpg_img = Image.open(jpg_path)
            assert jpg_img.format == 'JPEG'
            jpg_img.close()
    
    def test_normal_rgba_image(self):
        """TC-N-03: 正常系 - RGBA画像"""
        # Given: RGBA PNGファイル
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
            png_path = Path(tmpdir) / "test.png"
            img.save(png_path)
            
            # When: convert_png_to_jpgを実行
            jpg_path = convert_png_to_jpg(str(png_path))
            
            # Then: JPGファイルが作成される（RGBに変換される）
            assert jpg_path is not None
            assert os.path.exists(jpg_path)
            
            # JPGファイルがRGBモードであることを確認
            jpg_img = Image.open(jpg_path)
            assert jpg_img.mode == 'RGB'
            jpg_img.close()
    
    def test_normal_with_output_folder(self):
        """TC-N-04: 正常系 - output_folder指定"""
        # Given: PNGファイルと出力フォルダ
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            png_path = Path(tmpdir) / "test.png"
            img.save(png_path)
            
            output_folder = Path(tmpdir) / "output"
            
            # When: output_folderを指定してconvert_png_to_jpgを実行
            jpg_path = convert_png_to_jpg(str(png_path), output_folder=str(output_folder))
            
            # Then: 指定フォルダにJPGが保存される
            assert jpg_path is not None
            assert output_folder.exists()
            assert str(output_folder) in jpg_path
    
    def test_normal_delete_original(self):
        """TC-N-05: 正常系 - delete_original=True"""
        # Given: PNGファイル
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            png_path = Path(tmpdir) / "test.png"
            img.save(png_path)
            
            # When: delete_original=Trueでconvert_png_to_jpgを実行
            jpg_path = convert_png_to_jpg(str(png_path), delete_original=True)
            
            # Then: 元のPNGファイルが削除される
            assert jpg_path is not None
            assert not png_path.exists()
            assert os.path.exists(jpg_path)
    
    def test_normal_keep_original(self):
        """正常系 - delete_original=False"""
        # Given: PNGファイル
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            png_path = Path(tmpdir) / "test.png"
            img.save(png_path)
            
            # When: delete_original=Falseでconvert_png_to_jpgを実行
            jpg_path = convert_png_to_jpg(str(png_path), delete_original=False)
            
            # Then: 元のPNGファイルが保持される
            assert jpg_path is not None
            assert png_path.exists()
            assert os.path.exists(jpg_path)
    
    def test_normal_custom_quality(self):
        """TC-N-06: 正常系 - カスタム品質"""
        # Given: PNGファイルとカスタム品質
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            png_path = Path(tmpdir) / "test.png"
            img.save(png_path)
            
            # When: quality=85でconvert_png_to_jpgを実行
            jpg_path = convert_png_to_jpg(str(png_path), quality=85)
            
            # Then: JPGファイルが作成される
            assert jpg_path is not None
            assert os.path.exists(jpg_path)
    
    def test_boundary_quality_min(self):
        """TC-B-01: 境界値 - quality=1（最小値）"""
        # Given: PNGファイルとquality=1
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            png_path = Path(tmpdir) / "test.png"
            img.save(png_path)
            
            # When: quality=1でconvert_png_to_jpgを実行
            jpg_path = convert_png_to_jpg(str(png_path), quality=1)
            
            # Then: JPGファイルが作成される
            assert jpg_path is not None
            assert os.path.exists(jpg_path)
    
    def test_boundary_quality_max(self):
        """TC-B-02: 境界値 - quality=100（最大値）"""
        # Given: PNGファイルとquality=100
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            png_path = Path(tmpdir) / "test.png"
            img.save(png_path)
            
            # When: quality=100でconvert_png_to_jpgを実行
            jpg_path = convert_png_to_jpg(str(png_path), quality=100)
            
            # Then: JPGファイルが作成される
            assert jpg_path is not None
            assert os.path.exists(jpg_path)
    
    def test_abnormal_nonexistent_file(self):
        """TC-A-01: 異常系 - 存在しないPNGファイル"""
        # Given: 存在しないファイルパス
        nonexistent_path = "/path/that/does/not/exist.png"
        
        # When: convert_png_to_jpgを実行
        result = convert_png_to_jpg(nonexistent_path)
        
        # Then: Noneが返される
        assert result is None


class TestConvertFolder:
    """convert_folder関数のテスト"""
    
    def test_normal_convert_multiple_files(self):
        """正常系 - 複数ファイルの変換"""
        # Given: 複数のPNGファイルがあるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                img.save(Path(tmpdir) / f"image_{i}.png")
            
            # When: convert_folderを実行
            convert_folder(tmpdir, delete_original=False)
            
            # Then: JPGファイルが作成される
            jpg_files = list(Path(tmpdir).glob("*.jpg"))
            assert len(jpg_files) == 3
    
    def test_normal_with_output_folder(self):
        """正常系 - 出力フォルダ指定"""
        # Given: PNGファイルがあるディレクトリと出力フォルダ
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            img.save(Path(tmpdir) / "test.png")
            
            output_folder = Path(tmpdir) / "output"
            
            # When: 出力フォルダを指定してconvert_folderを実行
            convert_folder(tmpdir, output_folder=str(output_folder), delete_original=False)
            
            # Then: 出力フォルダにJPGが作成される
            assert output_folder.exists()
            jpg_files = list(output_folder.glob("*.jpg"))
            assert len(jpg_files) == 1
    
    def test_normal_delete_original(self):
        """正常系 - 元ファイル削除"""
        # Given: PNGファイルがあるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            img.save(Path(tmpdir) / "test.png")
            
            # When: delete_original=Trueでconvert_folderを実行
            convert_folder(tmpdir, delete_original=True)
            
            # Then: PNGファイルが削除され、JPGファイルが作成される
            png_files = list(Path(tmpdir).glob("*.png"))
            jpg_files = list(Path(tmpdir).glob("*.jpg"))
            assert len(png_files) == 0
            assert len(jpg_files) == 1

