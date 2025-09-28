#!/usr/bin/env python3
"""
Seed script for Articles feature demo data.
Creates sample users, articles, and drafts to showcase the Articles functionality.
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

# Add the src directory to the Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aic_hub.config import settings
from aic_hub.models import User, Article
from aic_hub.constants import AI_TAGS
from aic_hub.utils import slugify

# Sample user data
SAMPLE_USERS = [
    {
        "email": "alex.chen@airesearch.org",
        "display_name": "Dr. Alex Chen",
        "username": "alexchen",
        "bio": "AI Research Scientist specializing in Large Language Models and multimodal AI systems. PhD in Computer Science from Stanford.",
        "company": "OpenAI",
        "location": "San Francisco, CA",
        "expertise_tags": ["LLMs", "Fine-tuning", "Prompting", "Training"],
        "github_username": "alexchen-ai"
    },
    {
        "email": "sarah.williams@vectorlab.com",
        "display_name": "Sarah Williams",
        "username": "sarahw",
        "bio": "Building the next generation of RAG systems. Passionate about making AI more accessible and reliable.",
        "company": "Vector Labs",
        "location": "New York, NY",
        "expertise_tags": ["RAG", "Vector DBs", "Embeddings", "Search"],
        "github_username": "sarah-vectorlabs"
    },
    {
        "email": "marcus.rodriguez@ethicsai.org",
        "display_name": "Marcus Rodriguez",
        "username": "marcusr",
        "bio": "AI Safety researcher focused on alignment and responsible AI development. Former Google DeepMind researcher.",
        "company": "Anthropic",
        "location": "London, UK",
        "expertise_tags": ["Safety", "Ethics", "Benchmarks", "RL"],
        "github_username": "marcus-ai-safety"
    },
    {
        "email": "lisa.thompson@robotics.edu",
        "display_name": "Prof. Lisa Thompson",
        "username": "lisathompson",
        "bio": "Robotics and Computer Vision professor. Working on embodied AI and robot learning systems.",
        "company": "MIT",
        "location": "Cambridge, MA",
        "expertise_tags": ["Robotics", "Computer Vision", "RL", "Training"],
        "github_username": "lisa-mit-robotics"
    },
    {
        "email": "david.kim@aistartup.io",
        "display_name": "David Kim",
        "username": "davidkim",
        "bio": "Building AI-powered tools for developers. Previously led ML engineering at Stripe.",
        "company": "AI Startup Inc",
        "location": "Austin, TX",
        "expertise_tags": ["Tools", "Inference", "Agents", "NLP"],
        "github_username": "david-ai-tools"
    }
]

# Sample article data with rich Tiptap content
SAMPLE_ARTICLES = [
    {
        "title": "Building Production-Ready RAG Systems: Lessons from the Trenches",
        "author_email": "sarah.williams@vectorlab.com",
        "summary": "A comprehensive guide to building RAG systems that actually work in production, covering everything from vector databases to evaluation metrics.",
        "tags": ["RAG", "Vector DBs", "Embeddings", "Tools"],
        "published": True,
        "view_count": 1247,
        "days_ago": 5,
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Introduction"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Retrieval-Augmented Generation (RAG) has become the go-to architecture for building AI applications that need to work with domain-specific knowledge. However, there's a huge gap between the simple RAG tutorials you see online and what it takes to build a production system that actually works reliably."}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "After building and deploying dozens of RAG systems over the past two years, I've learned some hard lessons about what works and what doesn't. This post shares the key insights that will save you months of debugging and user complaints."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "The Hidden Complexity of RAG"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Most RAG tutorials make it look simple: chunk your documents, embed them, store in a vector database, and retrieve + generate. In reality, each of these steps has dozens of decisions that dramatically impact your system's performance."}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Chunking strategy: Fixed-size vs semantic vs hierarchical"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Embedding model choice: Domain-specific vs general-purpose"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Vector database configuration: Index types, similarity metrics, scaling"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Retrieval parameters: Top-k, similarity thresholds, reranking"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Production Lessons"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Here are the most important lessons I've learned:"}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "1. Evaluation is Everything"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "You cannot build a good RAG system without proper evaluation. Set up evaluation pipelines from day one with:"}
                    ]
                },
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {
                            "type": "text",
                            "text": "from ragas import evaluate\nfrom datasets import Dataset\n\n# Create evaluation dataset\neval_data = Dataset.from_dict({\n    \"question\": [\"What is the capital of France?\"],\n    \"answer\": [\"Paris is the capital of France.\"],\n    \"contexts\": [[\"France is a country in Europe. Its capital is Paris.\"]],\n    \"ground_truths\": [[\"Paris\"]]\n})\n\n# Evaluate your RAG system\nresult = evaluate(\n    eval_data,\n    metrics=[\"answer_relevancy\", \"faithfulness\", \"context_recall\"]\n)\nprint(result)"
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "2. Hybrid Search Beats Pure Vector Search"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Pure vector search often misses exact matches and important keywords. Combine it with traditional keyword search for better results:"}
                    ]
                },
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {
                            "type": "text",
                            "text": "# Hybrid search with vector + BM25\nvector_results = vector_search(query, top_k=20)\nkeyword_results = bm25_search(query, top_k=20)\n\n# Combine and rerank\ncombined_results = rerank(\n    vector_results + keyword_results,\n    query=query,\n    top_k=5\n)"
                        }
                    ]
                },
                {
                    "type": "blockquote",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "💡 "},
                                {"type": "text", "text": "Pro tip: Use a reranking model like Cohere's rerank-3 or BGE reranker to combine different retrieval methods effectively.", "marks": [{"type": "bold"}]}
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Conclusion"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Building production RAG systems is hard, but following these principles will set you up for success. Remember: start simple, measure everything, and iterate based on real user feedback."}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "What challenges have you faced building RAG systems? I'd love to hear about your experiences in the comments below."}
                    ]
                }
            ]
        }
    },
    {
        "title": "The Future of AI Agents: Beyond Simple Chatbots",
        "author_email": "alex.chen@airesearch.org",
        "summary": "Exploring the evolution of AI agents from simple chatbots to sophisticated autonomous systems that can reason, plan, and execute complex tasks.",
        "tags": ["Agents", "LLMs", "Prompting", "Tools"],
        "published": True,
        "view_count": 892,
        "days_ago": 12,
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The AI landscape is rapidly evolving from simple question-answering systems to sophisticated agents capable of autonomous reasoning and action. This transformation represents one of the most significant developments in artificial intelligence since the advent of large language models."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "What Makes an Agent Different?"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Traditional chatbots are reactive - they respond to user inputs but don't maintain state or pursue goals independently. AI agents, by contrast, are:"}
                    ]
                },
                {
                    "type": "orderedList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Autonomous", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - They can pursue goals without constant human guidance"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Stateful", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - They remember previous interactions and context"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Tool-enabled", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - They can interact with external systems and APIs"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Goal-oriented", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - They work towards specific objectives"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Agent Architecture Patterns"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Modern AI agents typically follow one of several architectural patterns:"}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "ReAct Pattern"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The ReAct (Reasoning + Acting) pattern combines reasoning traces with task-specific actions:"}
                    ]
                },
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {
                            "type": "text",
                            "text": "# Example ReAct agent loop\nwhile not task_complete:\n    # Reasoning step\n    thought = llm.generate(f\"Thought: {current_state}\")\n    \n    # Action step\n    if \"Action:\" in thought:\n        action = parse_action(thought)\n        observation = execute_action(action)\n        current_state += f\"\\nObservation: {observation}\"\n    else:\n        # Final answer\n        return extract_answer(thought)"
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Multi-Agent Systems"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Complex tasks often benefit from multiple specialized agents working together:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Research Agent", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Gathers information from various sources"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Analysis Agent", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Processes and synthesizes information"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Writing Agent", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Creates final output in desired format"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "blockquote",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "The key insight is that specialized agents often outperform general-purpose ones on specific tasks, much like how specialized teams work better than generalists in complex projects."}
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Challenges and Limitations"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Despite their promise, current AI agents face several challenges:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Reliability", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Agents can get stuck in loops or make unexpected decisions"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Cost", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Multiple LLM calls can be expensive for complex tasks"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Safety", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Autonomous systems need careful guardrails"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "The Road Ahead"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "As we look to the future, AI agents will likely become more sophisticated, reliable, and integrated into our daily workflows. The next few years will be crucial in determining how these systems evolve and what new capabilities emerge."}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "What excites me most is the potential for agents to augment human creativity and productivity in ways we're only beginning to imagine."}
                    ]
                }
            ]
        }
    },
    {
        "title": "AI Safety in Practice: Lessons from Deploying LLMs at Scale",
        "author_email": "marcus.rodriguez@ethicsai.org",
        "summary": "Real-world experiences and practical guidelines for safely deploying large language models in production environments.",
        "tags": ["Safety", "Ethics", "LLMs", "Benchmarks"],
        "published": True,
        "view_count": 645,
        "days_ago": 8,
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "As AI systems become more powerful and widespread, ensuring their safe deployment has become critical. This post shares practical lessons from deploying LLMs in production environments and the safety measures that actually work."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "The Safety Stack"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Effective AI safety requires multiple layers of protection:"}
                    ]
                },
                {
                    "type": "orderedList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Pre-training safety", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Data filtering and model architecture choices"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Fine-tuning safety", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Constitutional AI, RLHF, and safety-focused training"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Inference-time safety", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Input/output filtering and monitoring"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Application-level safety", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Human oversight and fail-safes"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "blockquote",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "⚠️ ", "marks": [{"type": "bold"}]},
                                {"type": "text", "text": "Remember: No single safety measure is sufficient. Defense in depth is essential for robust AI safety."}
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Practical Safety Measures"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Here are the safety measures we've found most effective in production:"}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Input Validation"}]
                },
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {
                            "type": "text",
                            "text": "def validate_input(user_input: str) -> tuple[bool, str]:\n    \"\"\"Validate user input for safety concerns.\"\"\"\n    \n    # Check for prompt injection attempts\n    if detect_prompt_injection(user_input):\n        return False, \"Potential prompt injection detected\"\n    \n    # Check for harmful content\n    toxicity_score = toxicity_classifier(user_input)\n    if toxicity_score > TOXICITY_THRESHOLD:\n        return False, \"Content violates safety guidelines\"\n    \n    # Check for PII\n    if contains_pii(user_input):\n        return False, \"Personal information detected\"\n    \n    return True, \"Input validated\""
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Output Monitoring"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Monitoring AI outputs is crucial for catching safety issues in real-time:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Automated toxicity detection on all outputs"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Factual accuracy checks for sensitive topics"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Human review queues for high-risk scenarios"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Evaluation and Testing"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Regular safety evaluation is essential. We use several benchmarks:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "TruthfulQA", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " for measuring truthfulness"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "HarmBench", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " for harmful output detection"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Custom adversarial tests", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " for domain-specific risks"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Looking Forward"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "AI safety is an evolving field. As models become more capable, our safety measures must evolve too. The key is building safety into systems from the ground up, not as an afterthought."}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "What safety measures have you found effective in your AI deployments? Share your experiences - we all benefit from learning together."}
                    ]
                }
            ]
        }
    },
    {
        "title": "Computer Vision Meets Robotics: Teaching Robots to See and Act",
        "author_email": "lisa.thompson@robotics.edu",
        "summary": "How advances in computer vision are enabling robots to better understand and interact with the physical world.",
        "tags": ["Robotics", "Computer Vision", "Training", "RL"],
        "published": True,
        "view_count": 423,
        "days_ago": 3,
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The intersection of computer vision and robotics is where some of the most exciting AI breakthroughs are happening. Teaching robots to see and understand their environment is crucial for creating truly autonomous systems."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "The Challenge of Embodied Vision"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Computer vision for robotics is fundamentally different from static image analysis. Robots need to:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Process visual information in real-time"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Understand 3D spatial relationships"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Handle dynamic environments with moving objects"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Integrate visual understanding with motor control"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Recent Advances"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Several breakthrough approaches are transforming robotic vision:"}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Neural Radiance Fields (NeRF) for Robotics"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "NeRF technology is enabling robots to build detailed 3D models of their environment from just a few camera views."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Vision-Language Models"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Models like CLIP and DALL-E are helping robots understand objects and scenes through natural language descriptions."}
                    ]
                },
                {
                    "type": "codeBlock",
                    "attrs": {"language": "python"},
                    "content": [
                        {
                            "type": "text",
                            "text": "# Example: Using CLIP for object detection in robotics\nimport clip\nimport torch\n\nmodel, preprocess = clip.load(\"ViT-B/32\")\n\ndef find_object(image, object_description):\n    \"\"\"Find object in image using natural language.\"\"\"\n    \n    # Process image\n    image_input = preprocess(image).unsqueeze(0)\n    text_input = clip.tokenize([object_description])\n    \n    # Get features\n    with torch.no_grad():\n        image_features = model.encode_image(image_input)\n        text_features = model.encode_text(text_input)\n    \n    # Calculate similarity\n    similarity = torch.cosine_similarity(image_features, text_features)\n    return similarity.item()"
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Training Challenges"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Training robotic vision systems presents unique challenges:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Sim-to-real gap", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Models trained in simulation often fail in real environments"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Data collection", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Gathering diverse, labeled robotic data is expensive and time-consuming"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Safety constraints", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Robots must learn without damaging themselves or their environment"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "blockquote",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "Our approach combines large-scale simulation with careful real-world fine-tuning to bridge the sim-to-real gap effectively."}
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Future Directions"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The future of robotic vision is incredibly promising. We're moving toward robots that can:"}
                    ]
                },
                {
                    "type": "orderedList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Understand complex scenes as well as humans"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Learn new visual concepts from just a few examples"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Reason about physics and object interactions"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Collaborate naturally with humans in shared spaces"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The next decade will be transformative for robotics as vision capabilities continue to improve exponentially."}
                    ]
                }
            ]
        }
    },
    {
        "title": "Building AI Tools That Developers Actually Want to Use",
        "author_email": "david.kim@aistartup.io",
        "summary": "Insights from building developer-focused AI tools and what makes the difference between tools that get adopted vs. abandoned.",
        "tags": ["Tools", "Inference", "Agents", "NLP"],
        "published": True,
        "view_count": 1156,
        "days_ago": 1,
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The AI tools landscape is exploding, but most tools fail to gain meaningful adoption. After building and shipping multiple developer-focused AI tools, I've learned what separates the winners from the abandoned GitHub repos."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "The Developer Adoption Challenge"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Developers are notoriously picky about their tools. They'll abandon anything that:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Takes more than 5 minutes to set up"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Doesn't work reliably out of the box"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Requires changing their existing workflow significantly"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Produces output that needs extensive manual cleanup"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "blockquote",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {"type": "text", "text": "💡 The best AI tools feel like magic - they solve a real problem with minimal effort from the user."}
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Principles That Work"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Here are the key principles I've found for building successful AI developer tools:"}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "1. Start with the Workflow, Not the Technology"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Don't build an AI tool and then look for a problem. Instead:"}
                    ]
                },
                {
                    "type": "orderedList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Identify a specific pain point in developer workflows"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Understand the current tools and processes"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Design a solution that fits into existing workflows"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Use AI as an implementation detail, not the main feature"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "2. Optimize for Time to Value"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Developers will give up quickly if they don't see immediate value. Design for the fastest possible path to a working solution:"}
                    ]
                },
                {
                    "type": "codeBlock",
                    "attrs": {"language": "bash"},
                    "content": [
                        {
                            "type": "text",
                            "text": "# Bad: Complex setup process\nnpm install complex-ai-tool\ncomplex-ai-tool init\ncomplex-ai-tool configure --model gpt-4 --temperature 0.7\ncomplex-ai-tool setup-auth --api-key YOUR_KEY\ncomplex-ai-tool run\n\n# Good: Simple one-liner\nnpx simple-ai-tool \"convert this CSV to JSON\" data.csv"
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "3. Make It Debuggable"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Developers need to understand what went wrong when tools fail. Provide:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Clear error messages with actionable next steps"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Verbose modes that show the AI's reasoning"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Ways to inspect and modify intermediate outputs"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Common Mistakes to Avoid"}]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "The \"Everything Tool\" Trap"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Many AI tools try to do everything and end up doing nothing well. Focus on solving one specific problem exceptionally well rather than being mediocre at many things."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Ignoring Edge Cases"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "AI tools often work great on demo data but fail on real-world edge cases. Spend time testing with:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Large files that might hit context limits"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Malformed or unusual input data"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Network failures and API rate limits"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Different operating systems and environments"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "Success Stories"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Tools that have achieved strong developer adoption tend to follow these patterns:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "GitHub Copilot", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Integrates seamlessly into existing editors"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Cursor", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Familiar VS Code experience with AI enhancements"}
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": "Vercel v0", "marks": [{"type": "bold"}]},
                                        {"type": "text", "text": " - Generates working code, not just snippets"}
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "The Future of AI Developer Tools"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The next wave of successful AI developer tools will likely:"}
                    ]
                },
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Understand entire codebases, not just individual files"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Provide real-time collaboration between human and AI"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Learn from team-specific patterns and preferences"}]
                                }
                            ]
                        },
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [{"type": "text", "text": "Integrate across the entire development lifecycle"}]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The key is remembering that developers want tools that make them more productive, not tools that show off AI capabilities. Focus on the human experience, and the AI will follow."}
                    ]
                }
            ]
        }
    }
]

# Sample draft articles
SAMPLE_DRAFTS = [
    {
        "title": "Understanding Transformer Architecture: A Visual Guide",
        "author_email": "alex.chen@airesearch.org",
        "summary": "A comprehensive visual explanation of how transformer models work, from attention mechanisms to positional encoding.",
        "tags": ["LLMs", "Training", "NLP"],
        "published": False,
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "The transformer architecture revolutionized natural language processing and forms the backbone of modern AI systems like GPT and BERT. This guide breaks down how transformers work with clear visualizations."}
                    ]
                },
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "The Attention Mechanism"}]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "At the heart of transformers is the attention mechanism, which allows the model to focus on different parts of the input sequence when processing each token..."}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "[DRAFT: Need to add more technical details and diagrams]"}
                    ]
                }
            ]
        }
    },
    {
        "title": "Scaling Vector Databases for Production RAG Systems",
        "author_email": "sarah.williams@vectorlab.com",
        "summary": "Performance optimization techniques for vector databases handling millions of embeddings in production RAG applications.",
        "tags": ["Vector DBs", "RAG", "Inference"],
        "published": False,
        "content": {
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "As RAG applications scale to handle millions of documents, vector database performance becomes critical. This post covers optimization strategies we've learned from running large-scale RAG systems."}
                    ]
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "[DRAFT: Outline key points - indexing strategies, memory optimization, query performance]"}
                    ]
                }
            ]
        }
    }
]

async def create_sample_users(session):
    """Create sample users for the demo."""
    print("Creating sample users...")
    created_users = {}

    for user_data in SAMPLE_USERS:
        # Check if user already exists
        stmt = select(User).where(User.email == user_data["email"])
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            created_users[user_data["email"]] = existing_user
            print(f"  User {user_data['display_name']} already exists")
            continue

        # Create new user
        user = User(
            id=uuid4(),
            email=user_data["email"],
            display_name=user_data["display_name"],
            username=user_data["username"],
            bio=user_data["bio"],
            company=user_data["company"],
            location=user_data["location"],
            expertise_tags=user_data["expertise_tags"],
            github_username=user_data["github_username"],
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
        )

        session.add(user)
        created_users[user_data["email"]] = user
        print(f"  Created user: {user_data['display_name']}")

    await session.commit()
    return created_users

async def create_sample_articles(session, users):
    """Create sample articles for the demo."""
    print("Creating sample articles...")

    for article_data in SAMPLE_ARTICLES:
        author = users[article_data["author_email"]]

        # Check if article already exists
        stmt = select(Article).where(Article.title == article_data["title"])
        result = await session.execute(stmt)
        existing_article = result.scalar_one_or_none()

        if existing_article:
            print(f"  Article '{article_data['title']}' already exists")
            continue

        # Generate slug
        slug = slugify(article_data["title"])

        # Check slug uniqueness
        counter = 1
        original_slug = slug
        while True:
            stmt = select(Article).where(Article.slug == slug)
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                break
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Create article
        created_at = datetime.utcnow() - timedelta(days=article_data["days_ago"])
        published_at = created_at if article_data["published"] else None

        article = Article(
            id=uuid4(),
            author_id=author.id,
            title=article_data["title"],
            slug=slug,
            content=json.dumps(article_data["content"]),
            summary=article_data["summary"],
            tags=article_data["tags"],
            status="published" if article_data["published"] else "draft",
            view_count=article_data.get("view_count", 0),
            like_count=random.randint(5, 50),
            published_at=published_at,
            created_at=created_at,
            updated_at=created_at + timedelta(hours=random.randint(1, 48))
        )

        session.add(article)
        print(f"  Created article: {article_data['title']}")

    await session.commit()

async def create_sample_drafts(session, users):
    """Create sample draft articles."""
    print("Creating sample drafts...")

    for draft_data in SAMPLE_DRAFTS:
        author = users[draft_data["author_email"]]

        # Check if draft already exists
        stmt = select(Article).where(Article.title == draft_data["title"])
        result = await session.execute(stmt)
        existing_article = result.scalar_one_or_none()

        if existing_article:
            print(f"  Draft '{draft_data['title']}' already exists")
            continue

        # Generate slug
        slug = slugify(draft_data["title"])

        # Create draft
        created_at = datetime.utcnow() - timedelta(days=random.randint(1, 7))

        article = Article(
            id=uuid4(),
            author_id=author.id,
            title=draft_data["title"],
            slug=slug,
            content=json.dumps(draft_data["content"]),
            summary=draft_data["summary"],
            tags=draft_data["tags"],
            status="draft",
            view_count=0,
            like_count=0,
            published_at=None,
            created_at=created_at,
            updated_at=created_at + timedelta(hours=random.randint(1, 24))
        )

        session.add(article)
        print(f"  Created draft: {draft_data['title']}")

    await session.commit()

async def main():
    """Main seeding function."""
    print("Starting article data seeding...")

    # Create database engine and session using the app's settings
    # This ensures we use the same database configuration as the main app
    from aic_hub.db import get_engine

    engine = get_engine()

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        # Create sample data
        users = await create_sample_users(session)
        await create_sample_articles(session, users)
        await create_sample_drafts(session, users)

    await engine.dispose()
    print("Article data seeding completed!")

if __name__ == "__main__":
    asyncio.run(main())