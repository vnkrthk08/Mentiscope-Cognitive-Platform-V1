from typing import Dict, Any, List, Tuple
from app.domain.speech.value_objects.word_timestamp import WordTimestamp
from app.domain.speech.value_objects.confidence_score import ConfidenceScore
from app.domain.speech.value_objects.language import Language


class TranscriptNormalizer:
    """Normalizes raw provider-specific response schemas into unified value objects."""

    @staticmethod
    def normalize_whisper(raw: Dict[str, Any]) -> Tuple[str, List[WordTimestamp], ConfidenceScore, Language]:
        text = raw.get("text", "")
        word_list = []
        confidences = []

        for seg in raw.get("segments", []):
            for w in seg.get("words", []):
                word_val = w.get("word", "").strip()
                start = float(w.get("start", 0.0))
                end = float(w.get("end", 0.0))
                prob = float(w.get("probability", 1.0))
                
                word_list.append(WordTimestamp(word=word_val, start_time=start, end_time=end, confidence=prob))
                confidences.append(prob)

        avg_conf = sum(confidences) / len(confidences) if confidences else 1.0
        score = ConfidenceScore(overall_score=avg_conf, per_word_scores=confidences)
        lang = Language(language_code=raw.get("language", "en"), confidence=1.0)

        return text, word_list, score, lang

    @staticmethod
    def normalize_azure(raw: Dict[str, Any]) -> Tuple[str, List[WordTimestamp], ConfidenceScore, Language]:
        text = raw.get("DisplayText", "")
        word_list = []
        confidences = []

        nbest = raw.get("NBest", [{}])
        if nbest:
            best = nbest[0]
            overall = float(best.get("Confidence", 1.0))
            for w in best.get("Words", []):
                word_val = w.get("Word", "").strip()
                # Azure offsets/durations are in 100-nanosecond units (1s = 10,000,000 units)
                offset = float(w.get("Offset", 0.0)) / 10000000.0
                duration = float(w.get("Duration", 0.0)) / 10000000.0
                conf = float(w.get("Confidence", 1.0))

                word_list.append(
                    WordTimestamp(
                        word=word_val,
                        start_time=offset,
                        end_time=offset + duration,
                        confidence=conf,
                    )
                )
                confidences.append(conf)
        
        avg_conf = sum(confidences) / len(confidences) if confidences else 1.0
        score = ConfidenceScore(overall_score=avg_conf, per_word_scores=confidences)
        lang = Language(language_code="en", confidence=1.0)

        return text, word_list, score, lang

    @staticmethod
    def normalize_deepgram(raw: Dict[str, Any]) -> Tuple[str, List[WordTimestamp], ConfidenceScore, Language]:
        results = raw.get("results", {})
        channels = results.get("channels", [{}])
        alt = channels[0].get("alternatives", [{}])[0] if channels else {}

        text = alt.get("transcript", "")
        word_list = []
        confidences = []

        for w in alt.get("words", []):
            word_val = w.get("word", "").strip()
            start = float(w.get("start", 0.0))
            end = float(w.get("end", 0.0))
            conf = float(w.get("confidence", 1.0))

            word_list.append(WordTimestamp(word=word_val, start_time=start, end_time=end, confidence=conf))
            confidences.append(conf)

        avg_conf = float(alt.get("confidence", sum(confidences) / len(confidences) if confidences else 1.0))
        score = ConfidenceScore(overall_score=avg_conf, per_word_scores=confidences)
        lang = Language(language_code="en", confidence=1.0)

        return text, word_list, score, lang

    @classmethod
    def normalize(
        cls, provider_name: str, raw_response: Dict[str, Any]
    ) -> Tuple[str, List[WordTimestamp], ConfidenceScore, Language]:
        """Dispatches normalizer parsing logic matching target provider name."""
        name = provider_name.lower()
        if "whisper" in name:
            return cls.normalize_whisper(raw_response)
        elif "azure" in name:
            return cls.normalize_azure(raw_response)
        elif "deepgram" in name:
            return cls.normalize_deepgram(raw_response)
        else:
            raise ValueError(f"No normalization parser found for provider '{provider_name}'.")
