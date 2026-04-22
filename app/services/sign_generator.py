import os

class SignGenerator:
    def __init__(self, assets_dir=None):
        if assets_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            assets_dir = os.path.join(base_dir, "assets")
        self.assets_dir = assets_dir
        self.assets_map = self._build_assets_map()

    def _build_assets_map(self):
        assets_map = {}
        if not os.path.exists(self.assets_dir):
            return assets_map
            
        for filename in os.listdir(self.assets_dir):
            name = os.path.splitext(filename)[0].lower()
            # Store full absolute path for desktop use
            assets_map[name] = os.path.join(self.assets_dir, filename)
        return assets_map

    def get_sign_sequence(self, text):
        if not text:
            return []
            
        import re
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text) 
        words = text.split()
        sequence = []
        
        i = 0
        while i < len(words):
            match_found = False
            for length in range(min(5, len(words) - i), 0, -1):
                phrase = " ".join(words[i : i + length])
                if phrase in self.assets_map:
                    print(f"DEBUG: Found sign match for '{phrase}': {self.assets_map[phrase]}")
                    sequence.append({
                        "word": phrase,
                        "asset": self.assets_map[phrase] # This is now the absolute path
                    })
                    i += length
                    match_found = True
                    break
            
            if not match_found:
                print(f"DEBUG: No sign match for '{words[i]}'")
                i += 1
                
        return sequence
