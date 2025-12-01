import json
import os
from src.settings import ASSET_PATH

class LocalizationManager:
    def __init__(self, default_lang="tr"):
        self.current_lang = default_lang
        self.data = {}
        self.load_language(default_lang)

    def load_language(self, lang_code):
        """Dili değiştirir ve JSON dosyasını yükler."""
        file_path = os.path.join(ASSET_PATH, "data", "languages", f"{lang_code}.json")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            self.current_lang = lang_code
            print(f"Dil Yüklendi: {lang_code}")
        except FileNotFoundError:
            print(f"HATA: Dil dosyası bulunamadı: {file_path}")
            # Hata durumunda boş sözlük veya hardcoded fallback yapılabilir
            self.data = {}

    def get(self, key_path):
        """
        Nokta notasyonu ile metni çeker.
        Örnek: get("ui.start_game") -> "BAŞLA"
        """
        keys = key_path.split(".")
        val = self.data
        
        try:
            for k in keys:
                val = val[k]
            return val
        except (KeyError, TypeError):
            return f"MISSING:{key_path}"