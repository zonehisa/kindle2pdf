#!/usr/bin/env python3
"""
設定ファイル読み込み共通ユーティリティ

設定ファイルの読み込みとデフォルト設定の管理を提供します。
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


# デフォルト設定
DEFAULT_CONFIG = {
    "output_folder": os.path.join(os.path.expanduser("~"), "Documents"),
    "book_title": "KindleBook",
    "page_delay": 2,
    "num_pages": 100,
    "similarity_threshold": 0.99,
    "jpg_quality": 95,
    "pdf_output_folder": None,
    "pdf_filename": None,
    "pages_per_pdf": None,
    "cleanup_after_pdf": None,
}


class ConfigLoader:
    """
    設定ファイル読み込みクラス
    """
    
    def __init__(self, default_config: Optional[Dict[str, Any]] = None):
        """
        Args:
            default_config: デフォルト設定辞書（Noneの場合はDEFAULT_CONFIGを使用）
        """
        self.default_config = default_config or DEFAULT_CONFIG.copy()
    
    def load(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """
        設定ファイルを読み込み
        
        Args:
            config_file: 設定ファイルのパス（Noneの場合はconfig.jsonを探す）
            
        Returns:
            設定辞書
        """
        config = self.default_config.copy()
        
        if config_file is None:
            config_file = "config.json"
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    config.update(user_config)
            except (json.JSONDecodeError, IOError) as e:
                # エラーは無視してデフォルト設定を使用
                pass
        
        return config


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    設定ファイルを読み込む関数（後方互換性のため）
    
    Args:
        config_file: 設定ファイルのパス
        
    Returns:
        設定辞書
    """
    loader = ConfigLoader()
    return loader.load(config_file)

