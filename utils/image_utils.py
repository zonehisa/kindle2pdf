#!/usr/bin/env python3
"""
画像処理共通ユーティリティ

画像の読み込み、リサイズ、形式変換、類似度計算などの共通処理を提供します。
"""

import re
from pathlib import Path
from typing import Tuple, Optional, Union
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


def natural_sort_key(text: str) -> list:
    """
    自然順序でソートするためのキー関数
    
    例: page_1.png, page_2.png, page_10.png の順序を正しく保つ
    
    Args:
        text: ソート対象の文字列
        
    Returns:
        ソートキーのリスト
    """
    return [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', text)]


def convert_rgba_to_rgb(img: Image.Image, background_color: Tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    """
    RGBA/LA画像をRGBに変換
    
    Args:
        img: PIL Imageオブジェクト
        background_color: 背景色（RGBタプル、デフォルト: 白）
        
    Returns:
        RGBに変換されたPIL Imageオブジェクト
    """
    if img.mode in ('RGBA', 'LA'):
        # 白い背景を作成
        background = Image.new('RGB', img.size, background_color)
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[-1])  # アルファチャンネルをマスクとして使用
        else:
            background.paste(img, mask=img.split()[-1])
        return background
    elif img.mode != 'RGB':
        return img.convert('RGB')
    return img


def load_and_resize_image(
    image_path: Union[str, Path],
    target_size: Tuple[int, int] = (256, 256)
) -> Optional[np.ndarray]:
    """
    画像を読み込み、比較用にリサイズ・グレースケール変換
    
    Args:
        image_path: 画像ファイルのパス
        target_size: リサイズ後のサイズ
        
    Returns:
        グレースケール画像の配列、失敗時はNone
    """
    try:
        with Image.open(image_path) as img:
            # RGBAの場合はRGBに変換
            img = convert_rgba_to_rgb(img)
            
            # リサイズ
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            
            # グレースケールに変換
            img_gray = img.convert('L')
            
            # numpy配列に変換
            return np.array(img_gray)
            
    except Exception as e:
        return None


def calculate_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    2つの画像の類似度をSSIMで計算
    
    Args:
        img1: 画像1の配列
        img2: 画像2の配列
        
    Returns:
        類似度（0.0-1.0）
    """
    try:
        # SSIMを計算
        similarity = ssim(img1, img2, data_range=255)
        return similarity
    except Exception as e:
        return 0.0

