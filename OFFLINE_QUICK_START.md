# 離線翻譯快速安裝指南

## 🚀 快速開始（三步驟）

### 步驟 1：安裝依賴套件

```bash
pip install transformers torch sentencepiece
```

或使用 requirements.txt：

```bash
pip install -r requirements.txt
```

### 步驟 2：下載翻譯模型

**方法 A：自動下載（推薦）**

在有網路的環境中執行：

```bash
python download_models.py
```

這會下載所有支援的翻譯模型（約 3.6GB）。

**方法 B：首次使用時自動下載**

- 直接使用應用程式
- 首次翻譯某語言對時會自動下載模型
- 需要等待 5-10 分鐘（視網路速度）

### 步驟 3：使用離線翻譯

啟動應用程式：

```bash
python main.py
```

應用程式會自動使用離線翻譯模式！

## 📦 無網路環境部署

### 在有網路的電腦上

1. **下載模型**：
   ```bash
   python download_models.py
   ```

2. **找到模型位置**：
   - Windows: `C:\Users\{用戶名}\.cache\huggingface\`
   - Linux/Mac: `~/.cache/huggingface/`

3. **打包模型**：
   ```bash
   # Windows（使用檔案總管壓縮）
   壓縮 C:\Users\{用戶名}\.cache\huggingface\ 為 models.zip
   
   # Linux/Mac
   tar -czf models.tar.gz ~/.cache/huggingface/
   ```

### 在無網路的電腦上

1. **複製模型檔案**：
   - 將 `models.zip` 或 `models.tar.gz` 複製到目標電腦

2. **解壓縮到正確位置**：
   ```bash
   # Windows
   解壓縮到 C:\Users\{用戶名}\.cache\huggingface\
   
   # Linux/Mac
   tar -xzf models.tar.gz -C ~/
   ```

3. **安裝依賴套件**（如果尚未安裝）：
   ```bash
   pip install -r requirements.txt
   ```

4. **執行應用程式**：
   ```bash
   python main.py
   ```

## ✅ 驗證安裝

執行測試：

```bash
python -c "
from src.translator import TranslationManager
tm = TranslationManager(use_offline=True)
print('離線翻譯可用:', tm.is_offline_available())
if tm.is_offline_available():
    result = tm.translate('Hello', 'en', 'zh-CN')
    print('測試翻譯結果:', result)
"
```

預期輸出：
```
離線翻譯可用: True
測試翻譯結果: 你好
```

## 📊 支援的語言

| 來源 → 目標 | 模型大小 | 支援 |
|------------|---------|------|
| 英文 → 簡體中文 | ~300MB | ✅ |
| 簡體中文 → 英文 | ~300MB | ✅ |
| 英文 → 日文 | ~300MB | ✅ |
| 日文 → 英文 | ~300MB | ✅ |
| 英文 → 韓文 | ~300MB | ✅ |
| 韓文 → 英文 | ~300MB | ✅ |
| 英文 → 法文 | ~300MB | ✅ |
| 英文 → 德文 | ~300MB | ✅ |
| 英文 → 西班牙文 | ~300MB | ✅ |

**注意**：繁體中文會自動轉為簡體中文模型

## 💡 使用技巧

### 首次使用某語言對會較慢

```
第一次翻譯: ~5-10秒（載入模型）
後續翻譯: <1秒（使用快取的模型）
```

### 只下載需要的模型

修改 `download_models.py`，只保留需要的模型：

```python
# 僅下載英中互譯
MODELS = [
    ("英文->簡體中文", "Helsinki-NLP/opus-mt-en-zh"),
    ("簡體中文->英文", "Helsinki-NLP/opus-mt-zh-en"),
]
```

### 加速翻譯

1. **使用 GPU**（如有 NVIDIA 顯卡）：
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu118
   ```

2. **只下載常用語言對**（減少記憶體使用）

## ⚠️ 常見問題

### Q: 安裝 torch 時出現 DLL 錯誤

**A**: 安裝 CPU 版本：
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Q: 記憶體不足

**A**: 
1. 關閉其他程式
2. 一次只載入一個語言對
3. 翻譯後重啟應用程式釋放記憶體

### Q: 下載模型很慢

**A**: 
1. 使用鏡像站（如清華鏡像）
2. 使用 VPN
3. 分批下載模型

### Q: 找不到模型檔案

**A**: 
1. 確認解壓縮到正確位置
2. 檢查目錄結構是否正確
3. 設定環境變數：
   ```bash
   export TRANSFORMERS_CACHE=/path/to/models
   ```

## 📞 技術支援

詳細文檔請參閱：
- `OFFLINE_TRANSLATION_GUIDE.md` - 完整安裝指南
- `TRANSLATION_GUIDE.md` - 翻譯功能使用指南

## 🎯 效能參考

### CPU (Intel i5-10400)
- 短句: ~1秒
- 段落: ~3秒

### GPU (NVIDIA GTX 1060)
- 短句: ~0.3秒
- 段落: ~0.8秒

### 記憶體使用
- 基礎: ~500MB
- 載入 1 個模型: ~1GB
- 載入 4 個模型: ~2.5GB

