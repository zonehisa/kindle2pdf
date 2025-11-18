#!/usr/bin/env python3
"""
設定ファイル読み込みユーティリティのテスト

テスト観点表:
| Case ID | Input / Precondition | Perspective (Equivalence / Boundary) | Expected Result | Notes |
|---------|---------------------|--------------------------------------|-----------------|-------|
| TC-N-01 | 有効なJSON設定ファイル | Equivalence - normal | 設定が正しく読み込まれる | - |
| TC-N-02 | 設定ファイルなし | Equivalence - normal | デフォルト設定が返される | - |
| TC-N-03 | 部分的な設定ファイル | Equivalence - normal | デフォルトとマージされる | - |
| TC-A-01 | 無効なJSONファイル | Boundary - 異常系 | デフォルト設定が返される | - |
| TC-A-02 | 存在しないファイルパス | Boundary - 異常系 | デフォルト設定が返される | - |
| TC-B-01 | 空のJSONファイル | Boundary - 空 | デフォルト設定が返される | - |
| TC-B-02 | Noneを渡す | Boundary - NULL | デフォルト設定が返される | - |
"""

import pytest
import json
import tempfile
import os
from utils.config_utils import load_config, ConfigLoader, DEFAULT_CONFIG


class TestLoadConfig:
    """load_config関数のテスト"""
    
    def test_normal_valid_config_file(self):
        """TC-N-01: 正常系 - 有効なJSON設定ファイル"""
        # Given: 有効なJSON設定ファイル
        config_data = {
            "book_title": "TestBook",
            "num_pages": 50,
            "page_delay": 3
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(config_data, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # When: load_configを実行
            result = load_config(tmp_path)
            
            # Then: 設定が正しく読み込まれる
            assert result["book_title"] == "TestBook"
            assert result["num_pages"] == 50
            assert result["page_delay"] == 3
            # デフォルト値も存在する
            assert "output_folder" in result
        finally:
            os.unlink(tmp_path)
    
    def test_normal_no_config_file(self):
        """TC-N-02: 正常系 - 設定ファイルなし"""
        # Given: 存在しない設定ファイルパス
        nonexistent_path = "/path/that/does/not/exist.json"
        
        # When: load_configを実行
        result = load_config(nonexistent_path)
        
        # Then: デフォルト設定が返される
        assert result == DEFAULT_CONFIG
    
    def test_normal_partial_config_file(self):
        """TC-N-03: 正常系 - 部分的な設定ファイル"""
        # Given: 一部の設定のみを含むJSONファイル
        config_data = {
            "book_title": "PartialBook"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(config_data, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # When: load_configを実行
            result = load_config(tmp_path)
            
            # Then: デフォルトとマージされる
            assert result["book_title"] == "PartialBook"
            assert result["num_pages"] == DEFAULT_CONFIG["num_pages"]
            assert result["page_delay"] == DEFAULT_CONFIG["page_delay"]
        finally:
            os.unlink(tmp_path)
    
    def test_abnormal_invalid_json(self):
        """TC-A-01: 異常系 - 無効なJSONファイル"""
        # Given: 無効なJSONファイル
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write("{ invalid json }")
            tmp_path = tmp_file.name
        
        try:
            # When: load_configを実行
            result = load_config(tmp_path)
            
            # Then: デフォルト設定が返される
            assert result == DEFAULT_CONFIG
        finally:
            os.unlink(tmp_path)
    
    def test_abnormal_nonexistent_file(self):
        """TC-A-02: 異常系 - 存在しないファイルパス"""
        # Given: 存在しないファイルパス
        nonexistent_path = "/nonexistent/path/config.json"
        
        # When: load_configを実行
        result = load_config(nonexistent_path)
        
        # Then: デフォルト設定が返される
        assert result == DEFAULT_CONFIG
    
    def test_boundary_empty_json(self):
        """TC-B-01: 境界値 - 空のJSONファイル"""
        # Given: 空のJSONファイル
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_file.write("{}")
            tmp_path = tmp_file.name
        
        try:
            # When: load_configを実行
            result = load_config(tmp_path)
            
            # Then: デフォルト設定が返される
            assert result == DEFAULT_CONFIG
        finally:
            os.unlink(tmp_path)
    
    def test_boundary_none(self):
        """TC-B-02: 境界値 - Noneを渡す"""
        # Given: Noneを渡す（config.jsonが存在する場合は読み込まれる）
        # When: load_configを実行
        result = load_config(None)
        
        # Then: 設定が返される（config.jsonが存在する場合は読み込まれる）
        assert isinstance(result, dict)
        assert "book_title" in result
        assert "num_pages" in result


class TestConfigLoader:
    """ConfigLoaderクラスのテスト"""
    
    def test_custom_default_config(self):
        """正常系 - カスタムデフォルト設定"""
        # Given: カスタムデフォルト設定
        custom_default = {
            "book_title": "CustomBook",
            "num_pages": 200
        }
        loader = ConfigLoader(default_config=custom_default)
        
        # When: loadを実行（設定ファイルなし）
        result = loader.load("/nonexistent/path.json")
        
        # Then: カスタムデフォルトが使用される
        assert result["book_title"] == "CustomBook"
        assert result["num_pages"] == 200
    
    def test_load_with_valid_file(self):
        """正常系 - 有効なファイルでload"""
        # Given: 有効なJSON設定ファイル
        config_data = {
            "book_title": "LoaderTestBook"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            json.dump(config_data, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            loader = ConfigLoader()
            # When: loadを実行
            result = loader.load(tmp_path)
            
            # Then: 設定が読み込まれる
            assert result["book_title"] == "LoaderTestBook"
        finally:
            os.unlink(tmp_path)
    
    def test_load_with_none(self):
        """正常系 - Noneを渡してload"""
        # Given: ConfigLoaderインスタンス
        loader = ConfigLoader()
        
        # When: Noneを渡してloadを実行（config.jsonが存在する場合は読み込まれる）
        result = loader.load(None)
        
        # Then: 設定が返される（config.jsonが存在する場合は読み込まれる）
        assert isinstance(result, dict)
        assert "book_title" in result
        assert "num_pages" in result

