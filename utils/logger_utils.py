#!/usr/bin/env python3
"""
ロギング共通ユーティリティ

統一されたロギング設定を提供します。
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "kindle2pdf",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    ロガーを設定して返す
    
    Args:
        name: ロガー名
        level: ログレベル
        format_string: フォーマット文字列（Noneの場合はデフォルトを使用）
        
    Returns:
        設定済みのロガー
    """
    logger = logging.getLogger(name)
    
    # 既にハンドラーが設定されている場合はスキップ
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # フォーマット
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "kindle2pdf") -> logging.Logger:
    """
    ロガーを取得（設定されていない場合はデフォルト設定で作成）
    
    Args:
        name: ロガー名
        
    Returns:
        ロガー
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        setup_logger(name)
    
    return logger

