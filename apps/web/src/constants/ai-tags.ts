export const AI_EXPERTISE_TAGS = [
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
] as const;

export type ExpertiseTag = (typeof AI_EXPERTISE_TAGS)[number];
