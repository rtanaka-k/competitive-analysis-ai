#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テキストファイルから市場データキャッシュを生成（Prompt Caching用）
"""

import os
import re

def load_text_file(file_path: str, max_chars: int = None) -> str:
    """
    テキストファイルを読み込み
    
    Args:
        file_path: ファイルパス
        max_chars: 最大文字数（Noneなら全て）
    
    Returns:
        テキスト
    """
    print(f"Loading: {os.path.basename(file_path)}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        if max_chars:
            text = text[:max_chars]
        
        # クリーニング
        text = clean_text(text)
        
        char_count = len(text)
        token_estimate = char_count // 4
        
        print(f"  Loaded: {char_count:,} characters (~{token_estimate:,} tokens)")
        
        return text
        
    except Exception as e:
        print(f"  Error: {e}")
        return ""

def clean_text(text: str) -> str:
    """
    テキストをクリーニング
    """
    # CRLF を LF に統一
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 連続する空白を1つに
    text = re.sub(r' +', ' ', text)
    
    # 連続する改行を2つまでに
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def load_market_data() -> str:
    """
    市場データを読み込んで結合
    
    Returns:
        結合されたテキスト
    """
    # Prompt Cachingの制限: 200,000 tokens (約800,000文字)
    # 安全のため、各ファイル200,000文字までに制限
    
    files = [
        {
            "path": "/mnt/project/PDF書籍_ファミ通ゲーム白書2025.pdf",
            "max_chars": 200000,
            "name": "ファミ通ゲーム白書2025"
        },
        {
            "path": "/mnt/project/PDF書籍_ファミ通モバイルゲーム白書2025.pdf",
            "max_chars": 200000,
            "name": "ファミ通モバイルゲーム白書2025"
        },
        {
            "path": "/mnt/project/JOGAオンラインゲーム市場調査レポート2025.pdf",
            "max_chars": 150000,
            "name": "JOGAオンラインゲーム市場調査レポート2025"
        }
    ]
    
    combined_text = ""
    total_chars = 0
    
    for file_info in files:
        print(f"\n{'='*60}")
        text = load_text_file(file_info["path"], file_info["max_chars"])
        
        if text:
            combined_text += f"\n\n【出典: {file_info['name']}】\n{text}"
            total_chars += len(text)
    
    print(f"\n{'='*60}")
    print(f"Total combined text: {total_chars:,} characters")
    estimated_tokens = total_chars // 4
    print(f"Estimated tokens: {estimated_tokens:,} tokens")
    
    # Prompt Cachingの制限チェック
    TOKEN_LIMIT = 200000
    
    if estimated_tokens > TOKEN_LIMIT:
        print(f"\n⚠️  WARNING: Estimated tokens ({estimated_tokens:,}) exceeds limit ({TOKEN_LIMIT:,})")
        print("   Recommend: Reduce max_chars in this script")
        excess = estimated_tokens - TOKEN_LIMIT
        reduction_needed = excess * 4
        print(f"   Need to reduce: ~{reduction_needed:,} characters")
    elif estimated_tokens > TOKEN_LIMIT * 0.9:
        print(f"\n⚠️  CAUTION: Estimated tokens ({estimated_tokens:,}) is close to limit ({TOKEN_LIMIT:,})")
    else:
        print(f"\n✅ Estimated tokens ({estimated_tokens:,}) is safely within limit ({TOKEN_LIMIT:,})")
    
    return combined_text

def save_market_data(output_path: str = "/home/claude/market_data_cache.txt"):
    """
    市場データをファイルに保存
    """
    print("="*60)
    print("Generating market data cache for Prompt Caching...")
    print("="*60)
    
    market_data = load_market_data()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(market_data)
    
    file_size_kb = os.path.getsize(output_path) / 1024
    
    print(f"\n{'='*60}")
    print(f"✅ Saved to: {output_path}")
    print(f"📊 File size: {file_size_kb:.2f} KB")
    print("="*60)
    
    return output_path

if __name__ == "__main__":
    # 市場データキャッシュを生成
    cache_file = save_market_data()
    
    print("\n✅ Market data cache created successfully!")
    print(f"\n📁 Cache file: {cache_file}")
    print("\nNext steps:")
    print("1. Review the cache file content")
    print("2. If too large, adjust max_chars in this script")
    print("3. Integrate into competitive_analysis_dual_full.py")
    print("4. Deploy and test!")
