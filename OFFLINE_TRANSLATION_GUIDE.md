# 離線翻譯功能安裝指南

## 概述

為了支援無網路環境的翻譯需求，我們新增了基於 **Hugging Face Transformers** 和 **MarianMT 模型**的離線翻譯功能。

## 系統需求

### 硬體需求
- **記憶體**: 至少 4GB RAM（建議 8GB）
- **儲存空間**: 每個翻譯模型約 300MB，建議預留 5GB 空間
- **處理器**: 支援 CPU 和 GPU（GPU 可大幅提升速度）

### 軟體需求
- Python 3.8 或更高版本
- pip 套件管理器

## 安裝步驟

### 步驟 1：安裝依賴套件

```bash
pip install -r requirements.txt
```

這將安裝以下關鍵套件：
- `transformers>=4.30.0` - Hugging Face 轉換器庫
- `torch>=2.0.0` - PyTorch（深度學習框架）
- `sentencepiece>=0.1.99` - 文字處理工具

### 步驟 2：下載翻譯模型（首次使用）

**重要**：首次使用某個語言對時，系統會自動從 Hugging Face 下載模型。建議在有網路的環境下先下載好所需模型。

#### 手動預下載模型

在有網路的電腦上執行：

```python
from transformers import MarianMTModel, MarianTokenizer

# 下載英文->中文模型
model_name = "Helsinki-NLP/opus-mt-en-zh"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# 儲存到本地
tokenizer.save_pretrained("./models/en-zh")
model.save_pretrained("./models/en-zh")
```

#### 支援的語言對

| 來源語言 | 目標語言 | 模型名稱 |
|---------|---------|---------|
| 英文 | 簡體中文 | Helsinki-NLP/opus-mt-en-zh |
| 簡體中文 | 英文 | Helsinki-NLP/opus-mt-zh-en |
| 英文 | 日文 | Helsinki-NLP/opus-mt-en-jap |
| 日文 | 英文 | Helsinki-NLP/opus-mt-jap-en |
| 英文 | 韓文 | Helsinki-NLP/opus-mt-en-ko |
| 韓文 | 英文 | Helsinki-NLP/opus-mt-ko-en |
| 英文 | 法文 | Helsinki-NLP/opus-mt-en-fr |
| 法文 | 英文 | Helsinki-NLP/opus-mt-fr-en |
| 英文 | 德文 | Helsinki-NLP/opus-mt-en-de |
| 德文 | 英文 | Helsinki-NLP/opus-mt-de-en |
| 英文 | 西班牙文 | Helsinki-NLP/opus-mt-en-es |
| 西班牙文 | 英文 | Helsinki-NLP/opus-mt-es-en |

### 步驟 3：模型移轉（無網路環境）

如果您的工作環境沒有網路：

1. **在有網路的電腦上**：
   ```bash
   # 下載所需模型
   python download_models.py
   ```

2. **複製模型檔案**：
   - 模型預設儲存在：`~/.cache/huggingface/hub/`（Linux/Mac）
   - 或：`C:\Users\{用戶名}\.cache\huggingface\hub\`（Windows）
   - 將整個 `hub` 資料夾複製到目標電腦的相同位置

3. **設定環境變數（可選）**：
   ```bash
   # Linux/Mac
   export TRANSFORMERS_CACHE=/path/to/models
   
   # Windows
   set TRANSFORMERS_CACHE=C:\path\to\models
   ```

## 使用方式

### 預設為離線模式

應用程式預設會優先使用離線翻譯：

```python
# 在 src/main_window.py 中
self.translation_manager = TranslationManager(use_offline=True)
```

### 切換模式

如果需要切換到線上模式（需要網路）：

```python
# 使用線上翻譯
self.translation_manager.set_offline_mode(False)

# 使用離線翻譯
self.translation_manager.set_offline_mode(True)
```

### 檢查離線功能可用性

```python
if translation_manager.is_offline_available():
    print("離線翻譯可用")
else:
    print("離線翻譯不可用，將使用線上翻譯")
```

## 工作流程

### 離線翻譯流程

```
1. 用戶選取文字
   ↓
2. 檢查離線模式是否啟用
   ↓
3. 檢查語言對是否有對應模型
   ↓
4. 載入模型（首次使用）或從快取獲取
   ↓
5. 執行離線翻譯
   ↓
6. 如果失敗，自動回退到線上翻譯（如有網路）
```

### 支援的翻譯模式

1. **純離線模式**：
   - 優先使用本地模型
   - 如果模型不存在或失敗，返回錯誤訊息
   
2. **混合模式（預設）**：
   - 優先使用離線模型
   - 如果失敗，自動回退到線上翻譯

## 性能優化

### 模型快取

系統會自動快取已載入的模型，避免重複載入：

```python
# 第一次使用某語言對時載入模型（較慢）
translation_manager.translate("Hello", "en", "zh-CN")  # ~5-10秒

# 後續使用同語言對（快速）
translation_manager.translate("World", "en", "zh-CN")  # <1秒
```

### 批次翻譯

對於大量文字，建議使用批次翻譯：

```python
texts = ["Hello", "World", "How are you?"]
translation_manager.translate_batch(texts, "en", "zh-CN")
```

## 疑難排解

### 問題 1：模型下載失敗

**錯誤訊息**：`OSError: Can't load model`

**解決方法**：
1. 檢查網路連線（首次下載需要網路）
2. 手動下載模型並放置到正確位置
3. 確認防火牆沒有阻擋 huggingface.co

### 問題 2：記憶體不足

**錯誤訊息**：`RuntimeError: out of memory`

**解決方法**：
1. 關閉其他佔用記憶體的應用程式
2. 使用較小的文字片段進行翻譯
3. 重新啟動應用程式釋放記憶體

### 問題 3：翻譯速度慢

**原因**：CPU 運算速度較慢

**解決方法**：
1. 使用 GPU 加速（如果有 NVIDIA 顯卡）：
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```
2. 減少翻譯文字長度
3. 考慮升級硬體

### 問題 4：找不到 torch.dll（Windows）

**解決方法**：
```bash
# 安裝 CPU 版本的 PyTorch
pip uninstall torch
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## 模型品質

### MarianMT 模型特點

- ✅ **體積小**：每個模型約 300MB
- ✅ **速度快**：CPU 上也能快速翻譯
- ✅ **品質好**：基於大規模平行語料訓練
- ⚠️ **專業術語**：可能不如 Google Translate 準確
- ⚠️ **繁體中文**：僅支援簡體中文，繁體需轉換

### 翻譯品質對比

| 翻譯引擎 | 品質 | 速度 | 網路需求 | 模型大小 |
|---------|------|------|---------|---------|
| Google Translate | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 需要 | N/A |
| MarianMT (離線) | ⭐⭐⭐⭐ | ⭐⭐⭐ | 不需要 | 300MB/模型 |

## 完全離線部署

### 準備工作（在有網路的電腦）

1. **建立模型下載腳本**：

```python
# download_models.py
from transformers import MarianMTModel, MarianTokenizer

models = [
    "Helsinki-NLP/opus-mt-en-zh",
    "Helsinki-NLP/opus-mt-zh-en",
    "Helsinki-NLP/opus-mt-en-jap",
    "Helsinki-NLP/opus-mt-jap-en",
]

for model_name in models:
    print(f"下載: {model_name}")
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    print(f"完成: {model_name}")
```

2. **執行下載**：
```bash
python download_models.py
```

3. **打包模型**：
```bash
# Linux/Mac
tar -czf models.tar.gz ~/.cache/huggingface/

# Windows（使用 7-Zip）
7z a models.zip C:\Users\{用戶名}\.cache\huggingface\
```

### 部署到離線環境

1. 將 `models.tar.gz` 或 `models.zip` 複製到目標電腦
2. 解壓縮到相同的快取目錄
3. 確認目錄結構：
   ```
   ~/.cache/huggingface/hub/
   └── models--Helsinki-NLP--opus-mt-en-zh/
       ├── snapshots/
       └── refs/
   ```

## 測試離線翻譯

```bash
# 測試腳本
python -c "
from src.translator import TranslationManager

tm = TranslationManager(use_offline=True)

if tm.is_offline_available():
    print('離線翻譯可用')
    result = tm.translate('Hello, world!', 'en', 'zh-CN')
    print(f'翻譯結果: {result}')
else:
    print('離線翻譯不可用')
"
```

## 注意事項

1. **首次使用較慢**：載入模型需要時間（5-10秒）
2. **模型快取**：已載入的模型會保留在記憶體中
3. **繁體中文**：系統會自動將繁體需求轉為簡體模型
4. **自動回退**：離線翻譯失敗時會嘗試線上翻譯

## 進階設定

### 使用 GPU 加速

如果有 NVIDIA 顯卡：

```bash
# 安裝 CUDA 版本的 PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### 自訂模型路徑

```python
import os
os.environ['TRANSFORMERS_CACHE'] = '/custom/path/to/models'
```

## 效能參考

### CPU 翻譯速度
- 短句（<50字）：~1秒
- 中段（50-200字）：~3秒
- 長段（200-500字）：~8秒

### GPU 翻譯速度（NVIDIA GTX 1060）
- 短句（<50字）：~0.3秒
- 中段（50-200字）：~0.8秒
- 長段（200-500字）：~2秒

