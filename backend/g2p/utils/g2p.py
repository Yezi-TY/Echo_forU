# Copyright (c) 2024 Amphion.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator
from phonemizer.utils import list2str, str2list
from typing import List, Union, Optional, Dict
import os
import json
import sys
import logging

logger = logging.getLogger(__name__)

# separator=Separator(phone=' ', word=' _ ', syllable='|'),
separator = Separator(word=" _ ", syllable="|", phone=" ")

# 延迟加载 phonemizer backends
_phonemizer_backends: Dict[str, Optional[EspeakBackend]] = {}
_phonemizer_initialized = False


def _init_phonemizer_backends():
    """延迟初始化 phonemizer backends"""
    global _phonemizer_backends, _phonemizer_initialized
    
    if _phonemizer_initialized:
        return _phonemizer_backends
    
    _phonemizer_backends = {}
    
    # 逐个初始化，失败的语言不影响其他语言
    supported_languages = {
        "zh": "zh",
        "en": "en-us",
        "fr": "fr-fr",
        "de": "de",
    }
    
    # espeak 不支持日语和韩语，这些语言有专门的处理函数
    unsupported_languages = ["ja", "ko"]
    
    for lang, espeak_lang in supported_languages.items():
        try:
            _phonemizer_backends[lang] = EspeakBackend(
                espeak_lang, preserve_punctuation=False, with_stress=False, language_switch="remove-flags"
            )
        except RuntimeError as e:
            logger.warning(f"Failed to initialize EspeakBackend for {lang}: {e}")
            _phonemizer_backends[lang] = None
    
    # 标记不支持的语言
    for lang in unsupported_languages:
        _phonemizer_backends[lang] = None
        logger.info(f"Language '{lang}' uses specialized processing, not espeak")
    
    _phonemizer_initialized = True
    
    initialized_count = sum(1 for v in _phonemizer_backends.values() if v is not None)
    logger.info(f"Phonemizer backends initialized: {initialized_count}/{len(supported_languages)} supported languages")
    
    return _phonemizer_backends


def _get_phonemizer_backend(language: str) -> Optional[EspeakBackend]:
    """获取指定语言的 phonemizer backend"""
    backends = _init_phonemizer_backends()
    backend = backends.get(language)
    
    if backend is None:
        if language in ["ja", "ko"]:
            # 日语和韩语使用专门的处理函数，不需要 espeak
            return None
        raise RuntimeError(
            f"Phonemizer backend for language '{language}' is not available. "
            "Please install espeak: brew install espeak (macOS) or apt-get install espeak (Linux)."
        )
    
    return backend


lang2backend = {
    "zh": lambda: _get_phonemizer_backend("zh"),
    "ja": lambda: _get_phonemizer_backend("ja"),
    "en": lambda: _get_phonemizer_backend("en"),
    "fr": lambda: _get_phonemizer_backend("fr"),
    "ko": lambda: _get_phonemizer_backend("ko"),
    "de": lambda: _get_phonemizer_backend("de"),
}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mls_en.json"), "r") as f:
    json_data = f.read()
token = json.loads(json_data)


def phonemizer_g2p(text, language):
    langbackend = lang2backend[language]()  # 调用 lambda 获取实际的 backend
    phonemes = _phonemize(
        langbackend,
        text,
        separator,
        strip=True,
        njobs=1,
        prepend_text=False,
        preserve_empty_lines=False,
    )
    token_id = []
    if isinstance(phonemes, list):
        for phone in phonemes:
            phonemes_split = phone.split(" ")
            token_id.append([token[p] for p in phonemes_split if p in token])
    else:
        phonemes_split = phonemes.split(" ")
        token_id = [token[p] for p in phonemes_split if p in token]
    return phonemes, token_id


def _phonemize(  # pylint: disable=too-many-arguments
    backend,
    text: Union[str, List[str]],
    separator: Separator,
    strip: bool,
    njobs: int,
    prepend_text: bool,
    preserve_empty_lines: bool,
):
    """Auxiliary function to phonemize()

    Does the phonemization and returns the phonemized text. Raises a
    RuntimeError on error.

    """
    # remember the text type for output (either list or string)
    text_type = type(text)

    # force the text as a list
    text = [line.strip(os.linesep) for line in str2list(text)]

    # if preserving empty lines, note the index of each empty line
    if preserve_empty_lines:
        empty_lines = [n for n, line in enumerate(text) if not line.strip()]

    # ignore empty lines
    text = [line for line in text if line.strip()]

    if text:
        # phonemize the text
        phonemized = backend.phonemize(
            text, separator=separator, strip=strip, njobs=njobs
        )
    else:
        phonemized = []

    # if preserving empty lines, reinsert them into text and phonemized lists
    if preserve_empty_lines:
        for i in empty_lines:  # noqa
            if prepend_text:
                text.insert(i, "")
            phonemized.insert(i, "")

    # at that point, the phonemized text is a list of str. Format it as
    # expected by the parameters
    if prepend_text:
        return list(zip(text, phonemized))
    if text_type == str:
        return list2str(phonemized)
    return phonemized
