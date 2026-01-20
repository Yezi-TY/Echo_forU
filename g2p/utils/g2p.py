# Copyright (c) 2024 Amphion.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import json
import sys
import logging

# 在导入 phonemizer 之前，确保 espeak 在 PATH 中
espeak_paths = [
    "/opt/homebrew/bin",  # macOS Homebrew
    "/usr/local/bin",      # Linux/macOS
    r"C:\Program Files\eSpeak NG",  # Windows 默认安装路径
    r"C:\Program Files (x86)\eSpeak NG",  # Windows 32位安装路径
]
current_path = os.environ.get("PATH", "")
path_separator = ";" if sys.platform == "win32" else ":"
for path in espeak_paths:
    # Windows 上检查 espeak-ng.exe，Unix 上检查 espeak
    espeak_name = "espeak-ng.exe" if sys.platform == "win32" else "espeak"
    espeak_full_path = os.path.join(path, espeak_name)
    if os.path.exists(espeak_full_path) and path not in current_path:
        os.environ["PATH"] = f"{path}{path_separator}{current_path}"
        break

# 设置 espeak 共享库路径（phonemizer 需要）
if "PHONEMIZER_ESPEAK_LIBRARY" not in os.environ:
    espeak_lib_paths = [
        "/opt/homebrew/lib/libespeak.dylib",  # macOS Homebrew
        "/opt/homebrew/lib/libespeak.1.dylib",  # macOS Homebrew
        "/usr/local/lib/libespeak.dylib",  # macOS/Linux
        r"C:\Program Files\eSpeak NG\libespeak-ng.dll",  # Windows 默认安装路径
        r"C:\Program Files (x86)\eSpeak NG\libespeak-ng.dll",  # Windows 32位安装路径
    ]
    for lib_path in espeak_lib_paths:
        if os.path.exists(lib_path):
            os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = lib_path
            break

from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator
from phonemizer.utils import list2str, str2list
from typing import List, Union, Optional, Dict

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
        "zh": "cmn",  # espeak-ng 使用 "cmn" 作为中文（Mandarin），"zh" 是 mbrola 语音可能无法加载
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


def _get_phonemizer_backend(language: str) -> EspeakBackend:
    """获取指定语言的 phonemizer backend"""
    backends = _init_phonemizer_backends()
    backend = backends.get(language)
    
    if backend is None:
        raise RuntimeError(
            f"Phonemizer backend for language '{language}' is not available. "
            "Please install espeak: brew install espeak (macOS) or apt-get install espeak (Linux)"
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

# Windows 上默认编码可能是 cp936/gbk，mls_en.json 含 IPA 字符会解码失败；
# 这里显式用 UTF-8（兼容 UTF-8 BOM 用 utf-8-sig）
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "mls_en.json"), "r", encoding="utf-8-sig") as f:
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
