# 翻譯功能安裝指南

## 快速安裝

1. **更新依賴套件**

```bash
pip install -r requirements.txt
```

2. **驗證安裝**

```bash
python -c "from deep_translator import GoogleTranslator; print('deep-translator 安裝成功！')"
```

3. **啟動應用程式**

```bash
python main.py
```

## 套件說明

### deep-translator

`deep-translator` 是一個輕量級的 Python 翻譯庫，支援多種翻譯引擎：
- Google Translate
- Microsoft Translator
- DeepL
- PONS
- LibreTranslate
- 等等

目前我們使用 Google Translate 作為預設翻譯引擎。

### 優勢

相比之前的 `argostranslate`：
- ✅ **更輕量**：不需要下載大型語言模型
- ✅ **更快速**：直接使用線上 API
- ✅ **更穩定**：沒有複雜的依賴（PyTorch、spaCy 等）
- ✅ **更簡單**：無需管理語言包
- ✅ **支援更多語言**：依賴 Google Translate 的語言支援

### 限制

- ⚠️ 需要網路連線
- ⚠️ 受 Google Translate 使用限制

## 使用範例

在 Python 中測試翻譯功能：

```python
from deep_translator import GoogleTranslator

# 英文翻譯成繁體中文
translator = GoogleTranslator(source='en', target='zh-TW')
result = translator.translate("Hello, world!")
print(result)  # 輸出：你好世界！

# 自動偵測來源語言
translator = GoogleTranslator(source='auto', target='zh-TW')
result = translator.translate("Bonjour")
print(result)  # 輸出：你好
```

## 疑難排解

### 安裝失敗

如果遇到安裝問題，請嘗試：

```bash
# 升級 pip
python -m pip install --upgrade pip

# 重新安裝 deep-translator
pip uninstall deep-translator
pip install deep-translator>=1.11.0
```

### 網路連線問題

確保可以連線到 Google Translate：

```bash
# Windows
ping translate.google.com

# 測試翻譯 API
python -c "from deep_translator import GoogleTranslator; print(GoogleTranslator(source='en', target='zh-TW').translate('test'))"
```

### 防火牆設定

如果防火牆阻擋連線，請確保允許 Python 應用程式連線到：
- `translate.google.com`
- `translate.googleapis.com`

## 進階設定

### 更換翻譯引擎

未來版本將支援切換不同的翻譯引擎。目前可以手動修改 `src/translator.py` 來使用其他引擎。

例如使用 DeepL：

```python
from deep_translator import DeepL

translator = DeepL(api_key="your-api-key", source="en", target="zh", use_free_api=True)
```

### 離線翻譯

如需離線翻譯功能，可以考慮：
1. 使用 LibreTranslate（自架翻譯服務）
2. 整合本地翻譯模型（如 Hugging Face Transformers）

這些功能可能在未來版本中實作。

## 相關資源

- [deep-translator GitHub](https://github.com/nidhaloff/deep-translator)
- [deep-translator 文檔](https://deep-translator.readthedocs.io/)
- [Google Translate 支援的語言](https://cloud.google.com/translate/docs/languages)

