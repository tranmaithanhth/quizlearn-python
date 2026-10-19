"""Local English -> Vietnamese translation using a cached MarianMT model.

Dependencies (one-time):
    python -m pip install "transformers>=4.40,<5" sentencepiece torch

On first run the model (~300 MB) downloads from Hugging Face. Further
translations use local model files and do not call translation websites.
"""
import os

MODEL_ID = "Helsinki-NLP/opus-mt-en-vi"


class OfflineTranslator:
    def __init__(self):
        try:
            import torch
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                'Cần cài thư viện dịch offline: '
                'python -m pip install "transformers>=4.40,<5" sentencepiece torch'
            ) from exc
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() and os.environ.get("TOEIC_USE_CUDA") == "1" else "cpu"
        try:
            print(f"Loading offline English-Vietnamese model: {MODEL_ID} ({self.device})", flush=True)
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)
            self.model.to(self.device)
            self.model.eval()
        except Exception as exc:
            raise RuntimeError(
                f"Không tải được mô hình {MODEL_ID}. "
                "Lần đầu cần Internet và đủ dung lượng ổ đĩa."
            ) from exc

    def translate_batch(self, texts, batch_size=8):
        results = []
        for start in range(0, len(texts), batch_size):
            chunk = texts[start:start + batch_size]
            inputs = self.tokenizer(
                chunk, return_tensors="pt", padding=True,
                truncation=True, max_length=192,
            ).to(self.device)
            with self.torch.no_grad():
                output_ids = self.model.generate(
                    **inputs, max_new_tokens=192, num_beams=4
                )
            translated = self.tokenizer.batch_decode(
                output_ids, skip_special_tokens=True
            )
            results.extend(text.strip() for text in translated)
        return results
