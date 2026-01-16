# Copyright (c) 2024 Amphion.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from g2p.g2p import cleaners
from tokenizers import Tokenizer
from g2p.g2p.text_tokenizers import TextTokenizer
from g2p.language_segmentation import LangSegment as LS
import json
import re

LangSegment = LS()

class PhonemeBpeTokenizer:
    def __init__(self, vacab_path="./f5_tts/g2p/g2p/vocab.json"):
        self.lang2backend = {
            "zh": "zh",  # espeak 使用 "zh" 而不是 "cmn"
            "ja": "ja",
            "en": "en-us",
            "fr": "fr-fr",
            "ko": "ko",
            "de": "de",
        }
        self.text_tokenizers = {}
        self.int_text_tokenizers()

        with open(vacab_path, "r") as f:
            json_data = f.read()
        data = json.loads(json_data)
        self.vocab = data["vocab"]
        LangSegment.setfilters(["en", "zh", "ja", "ko", "fr", "de"])

    def int_text_tokenizers(self):
        """延迟初始化 text tokenizers，只在需要时创建"""
        # 确保 espeak 在 PATH 中
        import os
        espeak_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
        current_path = os.environ.get("PATH", "")
        for path in espeak_paths:
            if os.path.exists(os.path.join(path, "espeak")) and path not in current_path:
                os.environ["PATH"] = f"{path}:{current_path}"
                break
        
        for key, value in self.lang2backend.items():
            # 日语和韩语不使用 espeak，使用自己的处理逻辑
            if key in ["ja", "ko"]:
                # 这些语言有专门的处理函数，不需要 espeak TextTokenizer
                self.text_tokenizers[key] = None  # 标记为特殊处理
                continue
            
            try:
                self.text_tokenizers[key] = TextTokenizer(language=value)
            except RuntimeError as e:
                # 如果 espeak 不支持该语言，延迟到实际使用时再报错
                # 先存储语言配置，实际使用时再创建
                self.text_tokenizers[key] = {"language": value, "error": str(e)}
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to initialize TextTokenizer for {key}: {e}. Will retry when needed.")

    def tokenize(self, text, sentence, language):

        # 1. convert text to phoneme
        phonemes = []
        if language == "auto":
            seglist = LangSegment.getTexts(text)
            tmp_ph = []
            for seg in seglist:
                tmp_ph.append(
                    self._clean_text(
                        seg["text"], sentence, seg["lang"], ["cjekfd_cleaners"]
                    )
                )
            phonemes = "|_|".join(tmp_ph)
        else:
            phonemes = self._clean_text(text, sentence, language, ["cjekfd_cleaners"])
        # print('clean text: ', phonemes)

        # 2. tokenize phonemes
        phoneme_tokens = self.phoneme2token(phonemes)
        # print('encode: ', phoneme_tokens)

        # # 3. decode tokens [optional]
        # decoded_text = self.tokenizer.decode(phoneme_tokens)
        # print('decoded: ', decoded_text)

        return phonemes, phoneme_tokens

    def _get_text_tokenizer(self, language: str):
        """获取指定语言的 text tokenizer，如果未初始化则延迟初始化"""
        # 日语和韩语使用特殊处理，不需要 TextTokenizer
        if language in ["ja", "ko"]:
            return None
        
        # 确保 espeak 在 PATH 中
        import os
        espeak_paths = ["/opt/homebrew/bin", "/usr/local/bin"]
        current_path = os.environ.get("PATH", "")
        for path in espeak_paths:
            if os.path.exists(os.path.join(path, "espeak")) and path not in current_path:
                os.environ["PATH"] = f"{path}:{current_path}"
                break
        
        tokenizer = self.text_tokenizers.get(language)
        
        # 如果是延迟初始化的占位符
        if isinstance(tokenizer, dict):
            try:
                # 尝试初始化
                tokenizer = TextTokenizer(language=tokenizer["language"])
                self.text_tokenizers[language] = tokenizer
            except RuntimeError as e:
                raise RuntimeError(
                    f"Failed to initialize TextTokenizer for language '{language}': {e}. "
                    "Please install espeak: brew install espeak (macOS) or apt-get install espeak (Linux). "
                    "Also ensure espeak is in your PATH."
                ) from e
        
        if tokenizer is None and language not in ["ja", "ko"]:
            raise RuntimeError(
                f"TextTokenizer for language '{language}' is not available. "
                "Please install espeak: brew install espeak (macOS) or apt-get install espeak (Linux)."
            )
        
        return tokenizer
    
    def _clean_text(self, text, sentence, language, cleaner_names):
        # 确保 text_tokenizer 已初始化（日语和韩语除外，它们使用特殊处理）
        if language in self.text_tokenizers and language not in ["ja", "ko"]:
            tokenizer = self._get_text_tokenizer(language)
            # 更新字典中的值
            if isinstance(self.text_tokenizers[language], dict):
                self.text_tokenizers[language] = tokenizer
        
        for name in cleaner_names:
            cleaner = getattr(cleaners, name)
            if not cleaner:
                raise Exception("Unknown cleaner: %s" % name)
        text = cleaner(text, sentence, language, self.text_tokenizers)
        return text

    def phoneme2token(self, phonemes):
        tokens = []
        if isinstance(phonemes, list):
            for phone in phonemes:
                phone = phone.split("\t")[0]
                phonemes_split = phone.split("|")
                tokens.append(
                    [self.vocab[p] for p in phonemes_split if p in self.vocab]
                )
        else:
            phonemes = phonemes.split("\t")[0]
            phonemes_split = phonemes.split("|")
            tokens = [self.vocab[p] for p in phonemes_split if p in self.vocab]
        return tokens
