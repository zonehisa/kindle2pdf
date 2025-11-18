#!/usr/bin/env python3
"""
画像→PDF変換スクリプトのテスト

テスト観点表:
| Case ID | Input / Precondition | Perspective (Equivalence / Boundary) | Expected Result | Notes |
|---------|---------------------|--------------------------------------|-----------------|-------|
| TC-N-01 | PNGファイル複数 | Equivalence - normal | PDFが作成される | - |
| TC-N-02 | JPGファイル複数 | Equivalence - normal | PDFが作成される | - |
| TC-N-03 | PNGとJPGの混合 | Equivalence - normal | PDFが作成される | - |
| TC-N-04 | RGBA画像 | Equivalence - normal | RGBに変換されてPDFが作成される | - |
| TC-N-05 | pages_per_pdf指定 | Equivalence - normal | 分割されたPDFが作成される | - |
| TC-N-06 | optimize=True | Equivalence - normal | 最適化されたPDFが作成される | - |
| TC-A-01 | 存在しない入力フォルダ | Boundary - 異常系 | FileNotFoundErrorが発生 | - |
| TC-A-02 | 画像ファイルが0個 | Boundary - 異常系 | FileNotFoundErrorが発生 | - |
| TC-A-03 | 空の画像ファイルリスト | Boundary - 異常系 | ValueErrorが発生 | - |
| TC-B-01 | pages_per_pdf=1 | Boundary - 最小値 | 1ページごとに分割される | - |
| TC-B-02 | pages_per_pdf=1000 | Boundary - 最大値 | 大きなPDFが作成される | - |
| TC-B-03 | quality=1 | Boundary - 最小値 | 最低品質でPDFが作成される | - |
| TC-B-04 | quality=100 | Boundary - 最大値 | 最高品質でPDFが作成される | - |
"""

import pytest
import tempfile
import os
from pathlib import Path
from PIL import Image

from image_to_pdf import (
    find_image_files,
    convert_images_to_pdf
)


class TestFindImageFiles:
    """find_image_files関数のテスト"""
    
    def test_normal_png_files(self):
        """TC-N-01: 正常系 - PNGファイル複数"""
        # Given: 複数のPNGファイルがあるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                img.save(Path(tmpdir) / f"image_{i}.png")
            
            # When: find_image_filesを実行
            image_files = find_image_files(tmpdir)
            
            # Then: PNGファイルが取得される
            assert len(image_files) == 3
            assert all(f.endswith('.png') for f in image_files)
    
    def test_normal_jpg_files(self):
        """TC-N-02: 正常系 - JPGファイル複数"""
        # Given: 複数のJPGファイルがあるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                img = Image.new('RGB', (100, 100), (0, 255, 0))
                img.save(Path(tmpdir) / f"image_{i}.jpg")
            
            # When: find_image_filesを実行
            image_files = find_image_files(tmpdir)
            
            # Then: JPGファイルが取得される
            assert len(image_files) == 3
            assert all(f.endswith('.jpg') for f in image_files)
    
    def test_normal_mixed_files(self):
        """TC-N-03: 正常系 - PNGとJPGの混合"""
        # Given: PNGとJPGファイルが混在するディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            img1 = Image.new('RGB', (100, 100), (255, 0, 0))
            img1.save(Path(tmpdir) / "image1.png")
            img2 = Image.new('RGB', (100, 100), (0, 255, 0))
            img2.save(Path(tmpdir) / "image2.jpg")
            
            # When: find_image_filesを実行
            image_files = find_image_files(tmpdir)
            
            # Then: 両方のファイルが取得される
            assert len(image_files) == 2
            assert any(f.endswith('.png') for f in image_files)
            assert any(f.endswith('.jpg') for f in image_files)
    
    def test_normal_with_pattern(self):
        """正常系 - パターン指定"""
        # Given: PNGとJPGファイルがあるディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            img1 = Image.new('RGB', (100, 100), (255, 0, 0))
            img1.save(Path(tmpdir) / "image1.png")
            img2 = Image.new('RGB', (100, 100), (0, 255, 0))
            img2.save(Path(tmpdir) / "image2.jpg")
            
            # When: パターンを指定してfind_image_filesを実行
            image_files = find_image_files(tmpdir, pattern="*.png")
            
            # Then: PNGファイルのみが取得される
            assert len(image_files) == 1
            assert image_files[0].endswith('.png')
    
    def test_abnormal_nonexistent_folder(self):
        """TC-A-01: 異常系 - 存在しない入力フォルダ"""
        # Given: 存在しないフォルダパス
        nonexistent_path = "/path/that/does/not/exist"
        
        # When/Then: FileNotFoundErrorが発生
        with pytest.raises(FileNotFoundError, match="入力フォルダが見つかりません"):
            find_image_files(nonexistent_path)
    
    def test_abnormal_no_image_files(self):
        """TC-A-02: 異常系 - 画像ファイルが0個"""
        # Given: 画像ファイルがないディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            # When/Then: FileNotFoundErrorが発生
            with pytest.raises(FileNotFoundError, match="画像ファイル（PNG/JPG）が見つかりません"):
                find_image_files(tmpdir)


class TestConvertImagesToPdf:
    """convert_images_to_pdf関数のテスト"""
    
    def test_normal_png_to_pdf(self):
        """正常系 - PNGからPDF"""
        # Given: PNGファイルのリスト
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(3):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                png_path = Path(tmpdir) / f"image_{i}.png"
                img.save(png_path)
                image_files.append(str(png_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: convert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf))
            
            # Then: PDFファイルが作成される
            assert output_pdf.exists()
            assert output_pdf.stat().st_size > 0
    
    def test_normal_jpg_to_pdf(self):
        """正常系 - JPGからPDF"""
        # Given: JPGファイルのリスト
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(3):
                img = Image.new('RGB', (100, 100), (0, 255, 0))
                jpg_path = Path(tmpdir) / f"image_{i}.jpg"
                img.save(jpg_path, 'JPEG')
                image_files.append(str(jpg_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: convert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf))
            
            # Then: PDFファイルが作成される
            assert output_pdf.exists()
            assert output_pdf.stat().st_size > 0
    
    def test_normal_rgba_to_pdf(self):
        """TC-N-04: 正常系 - RGBA画像からPDF"""
        # Given: RGBA PNGファイルのリスト
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(2):
                img = Image.new('RGBA', (100, 100), (255, 0, 0, 128))
                png_path = Path(tmpdir) / f"image_{i}.png"
                img.save(png_path)
                image_files.append(str(png_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: convert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf))
            
            # Then: PDFファイルが作成される（RGBに変換される）
            assert output_pdf.exists()
            assert output_pdf.stat().st_size > 0
    
    def test_normal_pages_per_pdf(self):
        """TC-N-05: 正常系 - pages_per_pdf指定"""
        # Given: 複数の画像ファイルとpages_per_pdf=2
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(5):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                png_path = Path(tmpdir) / f"image_{i}.png"
                img.save(png_path)
                image_files.append(str(png_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: pages_per_pdf=2でconvert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf), pages_per_pdf=2)
            
            # Then: 分割されたPDFファイルが作成される
            # 5ページを2ページごとに分割すると3つのPDFが作成される
            pdf_files = list(Path(tmpdir).glob("output_*.pdf"))
            assert len(pdf_files) == 3
    
    def test_boundary_pages_per_pdf_one(self):
        """TC-B-01: 境界値 - pages_per_pdf=1"""
        # Given: 複数の画像ファイルとpages_per_pdf=1
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(3):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                png_path = Path(tmpdir) / f"image_{i}.png"
                img.save(png_path)
                image_files.append(str(png_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: pages_per_pdf=1でconvert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf), pages_per_pdf=1)
            
            # Then: 3つのPDFファイルが作成される
            pdf_files = list(Path(tmpdir).glob("output_*.pdf"))
            assert len(pdf_files) == 3
    
    def test_normal_optimize_true(self):
        """TC-N-06: 正常系 - optimize=True"""
        # Given: 画像ファイルとoptimize=True
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(2):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                png_path = Path(tmpdir) / f"image_{i}.png"
                img.save(png_path)
                image_files.append(str(png_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: optimize=Trueでconvert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf), optimize=True)
            
            # Then: PDFファイルが作成される
            assert output_pdf.exists()
    
    def test_normal_optimize_false(self):
        """正常系 - optimize=False"""
        # Given: 画像ファイルとoptimize=False
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(2):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                png_path = Path(tmpdir) / f"image_{i}.png"
                img.save(png_path)
                image_files.append(str(png_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: optimize=Falseでconvert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf), optimize=False)
            
            # Then: PDFファイルが作成される
            assert output_pdf.exists()
    
    def test_boundary_quality_min(self):
        """TC-B-03: 境界値 - quality=1"""
        # Given: 画像ファイルとquality=1
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(2):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                png_path = Path(tmpdir) / f"image_{i}.png"
                img.save(png_path)
                image_files.append(str(png_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: quality=1でconvert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf), quality=1)
            
            # Then: PDFファイルが作成される
            assert output_pdf.exists()
    
    def test_boundary_quality_max(self):
        """TC-B-04: 境界値 - quality=100"""
        # Given: 画像ファイルとquality=100
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            for i in range(2):
                img = Image.new('RGB', (100, 100), (255, 0, 0))
                png_path = Path(tmpdir) / f"image_{i}.png"
                img.save(png_path)
                image_files.append(str(png_path))
            
            output_pdf = Path(tmpdir) / "output.pdf"
            
            # When: quality=100でconvert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf), quality=100)
            
            # Then: PDFファイルが作成される
            assert output_pdf.exists()
    
    def test_abnormal_empty_list(self):
        """TC-A-03: 異常系 - 空の画像ファイルリスト"""
        # Given: 空のリスト
        image_files = []
        output_pdf = "/tmp/test.pdf"
        
        # When/Then: ValueErrorが発生
        with pytest.raises(ValueError, match="変換する画像ファイルがありません"):
            convert_images_to_pdf(image_files, output_pdf)
    
    def test_normal_output_directory_creation(self):
        """正常系 - 出力ディレクトリの自動作成"""
        # Given: 画像ファイルと存在しない出力ディレクトリ
        with tempfile.TemporaryDirectory() as tmpdir:
            image_files = []
            img = Image.new('RGB', (100, 100), (255, 0, 0))
            png_path = Path(tmpdir) / "image.png"
            img.save(png_path)
            image_files.append(str(png_path))
            
            output_dir = Path(tmpdir) / "output" / "subdir"
            output_pdf = output_dir / "output.pdf"
            
            # When: convert_images_to_pdfを実行
            convert_images_to_pdf(image_files, str(output_pdf))
            
            # Then: 出力ディレクトリが作成され、PDFが保存される
            assert output_dir.exists()
            assert output_pdf.exists()

