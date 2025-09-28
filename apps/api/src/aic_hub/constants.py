"""Constants used throughout the AIC Hub application."""

# Fixed AI taxonomy - immutable tags for consistent categorization
AI_TAGS = [
    # Core AI/ML
    "LLMs",           # Large Language Models
    "RAG",            # Retrieval-Augmented Generation
    "Agents",         # AI Agents & Multi-agent systems
    "Fine-tuning",    # Model fine-tuning
    "Prompting",      # Prompt engineering

    # Infrastructure
    "Vector DBs",     # Vector databases
    "Embeddings",     # Embedding models & techniques
    "Training",       # Model training
    "Inference",      # Model inference & deployment

    # Governance
    "Ethics",         # AI ethics
    "Safety",         # AI safety & alignment
    "Benchmarks",     # Evaluation & benchmarks
    "Datasets",       # Datasets & data preparation
    "Tools",          # AI tools & frameworks

    # Applications
    "Computer Vision", # CV applications
    "NLP",            # Natural Language Processing
    "Speech",         # Speech recognition & synthesis
    "Robotics",       # Robotics & embodied AI
    "RL"              # Reinforcement Learning
]

# Tag descriptions for UI display
TAG_DESCRIPTIONS = {
    "LLMs": "Large Language Models - Foundation models like GPT, Claude, LLaMA",
    "RAG": "Retrieval-Augmented Generation - Combining retrieval with generation",
    "Agents": "AI Agents & Multi-agent systems",
    "Fine-tuning": "Model fine-tuning techniques and best practices",
    "Prompting": "Prompt engineering and optimization",
    "Vector DBs": "Vector databases for similarity search",
    "Embeddings": "Embedding models & techniques",
    "Training": "Model training infrastructure and methods",
    "Inference": "Model inference & deployment",
    "Ethics": "AI ethics and responsible AI",
    "Safety": "AI safety & alignment research",
    "Benchmarks": "Evaluation metrics & benchmarks",
    "Datasets": "Datasets & data preparation",
    "Tools": "AI tools, frameworks, and libraries",
    "Computer Vision": "Computer vision applications and models",
    "NLP": "Natural Language Processing",
    "Speech": "Speech recognition & synthesis",
    "Robotics": "Robotics & embodied AI",
    "RL": "Reinforcement Learning"
}

# Related tags mapping for discovery
TAG_RELATIONSHIPS = {
    "RAG": ["Vector DBs", "Embeddings", "LLMs"],
    "Agents": ["LLMs", "Tools", "Prompting"],
    "Fine-tuning": ["LLMs", "Training", "Datasets"],
    "Prompting": ["LLMs", "Agents"],
    "Vector DBs": ["RAG", "Embeddings"],
    "Embeddings": ["RAG", "Vector DBs", "NLP"],
    "Training": ["Fine-tuning", "Datasets", "Inference"],
    "Inference": ["Training", "Tools"],
    "Computer Vision": ["Training", "Datasets", "Inference"],
    "NLP": ["LLMs", "Embeddings", "Prompting"],
    "Speech": ["NLP", "Training"],
    "Robotics": ["RL", "Computer Vision"],
    "RL": ["Agents", "Robotics", "Training"]
}