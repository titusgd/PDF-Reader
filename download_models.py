#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
離線翻譯模型下載工具
在有網路的環境中執行此腳本，下載所需的翻譯模型
"""

from transformers import MarianMTModel, MarianTokenizer
import sys

# 需要下載的模型列表
MODELS = [
    ("英文->簡體中文", "Helsinki-NLP/opus-mt-en-zh"),
    ("簡體中文->英文", "Helsinki-NLP/opus-mt-zh-en"),
    ("英文->日文", "Helsinki-NLP/opus-mt-en-jap"),
    ("日文->英文", "Helsinki-NLP/opus-mt-jap-en"),
    ("英文->韓文", "Helsinki-NLP/opus-mt-en-ko"),
    ("韓文->英文", "Helsinki-NLP/opus-mt-ko-en"),
    ("英文->法文", "Helsinki-NLP/opus-mt-en-fr"),
    ("法文->英文", "Helsinki-NLP/opus-mt-fr-en"),
    ("英文->德文", "Helsinki-NLP/opus-mt-en-de"),
    ("德文->英文", "Helsinki-NLP/opus-mt-de-en"),
    ("英文->西班牙文", "Helsinki-NLP/opus-mt-en-es"),
    ("西班牙文->英文", "Helsinki-NLP/opus-mt-es-en"),
]


def download_model(name, model_name):
    """下載單個模型"""
    try:
        print(f"\n下載模型: {name} ({model_name})")
        print("=" * 60)
        
        # 下載 tokenizer
        print("  [1/2] 下載 Tokenizer...")
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        print("  ✓ Tokenizer 下載完成")
        
        # 下載模型
        print("  [2/2] 下載模型...")
        model = MarianMTModel.from_pretrained(model_name)
        print("  ✓ 模型下載完成")
        
        print(f"✓ 完成: {name}")
        return True
        
    except Exception as e:
        print(f"✗ 錯誤: {name}")
        print(f"  錯誤訊息: {e}")
        return False


def main():
    """主函數"""
    print("=" * 60)
    print("PDF 閱讀器 - 離線翻譯模型下載工具")
    print("=" * 60)
    print(f"\n將下載 {len(MODELS)} 個翻譯模型")
    print("每個模型約 300MB，總共約 3.6GB")
    print("\n注意：此過程需要穩定的網路連線\n")
    
    # 詢問確認
    response = input("是否繼續下載？(y/n): ")
    if response.lower() not in ['y', 'yes', '是']:
        print("已取消下載")
        return
    
    # 下載模型
    success_count = 0
    failed_models = []
    
    for i, (name, model_name) in enumerate(MODELS, 1):
        print(f"\n進度: [{i}/{len(MODELS)}]")
        
        if download_model(name, model_name):
            success_count += 1
        else:
            failed_models.append((name, model_name))
    
    # 顯示結果
    print("\n" + "=" * 60)
    print("下載完成！")
    print("=" * 60)
    print(f"成功: {success_count}/{len(MODELS)}")
    
    if failed_models:
        print(f"失敗: {len(failed_models)}/{len(MODELS)}")
        print("\n失敗的模型:")
        for name, model_name in failed_models:
            print(f"  - {name} ({model_name})")
        print("\n您可以稍後重新執行此腳本下載失敗的模型")
    else:
        print("\n所有模型下載成功！")
        print("您現在可以在無網路環境中使用離線翻譯功能")
    
    print("\n模型儲存位置:")
    import os
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    print(f"  {cache_dir}")
    print("\n如需在無網路環境使用，請將上述目錄複製到目標電腦的相同位置")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n使用者中斷下載")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n發生錯誤: {e}")
        sys.exit(1)

