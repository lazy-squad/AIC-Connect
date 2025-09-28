from __future__ import annotations

AI_EXPERTISE_TAGS: tuple[str, ...] = (
  "LLMs",
  "RAG",
  "Agents",
  "Fine-tuning",
  "Prompting",
  "Vector DBs",
  "Embeddings",
  "Training",
  "Inference",
  "Ethics",
  "Safety",
  "Benchmarks",
  "Datasets",
  "Tools",
  "Computer Vision",
  "NLP",
  "Speech",
  "Robotics",
  "RL",
)


def is_valid_expertise_tag(tag: str) -> bool:
  return tag in AI_EXPERTISE_TAGS

