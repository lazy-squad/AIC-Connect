# Demo Data for AIC Hub

This directory contains a demo data seeding script that creates realistic sample users for testing and demonstration purposes.

## Features

The demo data includes:
- 15 diverse user profiles with realistic backgrounds
- GitHub-style profile information (avatars, bios, companies, locations)
- Expertise tags covering all AI domains in the platform
- Varied geographic locations (San Francisco, London, Tokyo, etc.)
- Different company affiliations (OpenAI, DeepMind, Anthropic, etc.)
- Staggered creation timestamps for realistic data distribution

## Usage

### Prerequisites

1. Ensure PostgreSQL is running and accessible
2. Run database migrations: `uv run alembic upgrade head`
3. Make sure the `.env` file has correct database configuration

### Commands

```bash
# Create demo users (default)
uv run python seed_demo_data.py

# Explicitly create demo users
uv run python seed_demo_data.py create

# Show statistics about existing users
uv run python seed_demo_data.py stats

# Clean up demo users
uv run python seed_demo_data.py clean
```

## Sample Users

The script creates 15 users with the following profiles:

### AI Researchers & Engineers
- **Sarah Chen** (Anthropic) - LLMs, Ethics, Safety, NLP
- **Alex Rivera** (Pinecone) - RAG, Vector DBs, Embeddings, Tools
- **Yuki Tanaka** (Waymo) - Computer Vision, Robotics, Training, Datasets
- **Marcus Johnson** (DeepMind) - Agents, Prompting, RL, LLMs
- **Elena Volkov** (Alignment Research Center) - Safety, Ethics, LLMs, Benchmarks

### Industry Specialists
- **Priya Patel** (HealthTalk AI) - NLP, LLMs, Ethics, Fine-tuning
- **David Kim** (Scale AI) - Training, Inference, Tools, Datasets
- **Carlos Mendoza** (Hugging Face) - Fine-tuning, Datasets, LLMs, Tools
- **Aisha Okonkwo** (Mozilla) - Speech, NLP, Ethics, Datasets
- **Jin Wang** (Boston Dynamics) - Robotics, RL, Computer Vision, Training

### Tools & Platform Builders
- **Lisa Zhang** (OpenAI) - Tools, LLMs, Inference, Embeddings
- **Ahmed Hassan** (AI21 Labs) - Benchmarks, Datasets, LLMs, Safety
- **Sophie Martin** (Freelance) - LLMs, Fine-tuning, Tools, Prompting

### Academia & Product
- **Raj Gupta** (Stanford University) - Computer Vision, NLP, LLMs, Training
- **Maria Silva** (Microsoft) - LLMs, Tools, Ethics, Inference

## Login Credentials

All demo users have the same password for easy testing:
- **Password**: `demo123`

Example login:
- Email: `sarah.chen@example.com`
- Password: `demo123`

## Geographic Distribution

Users are spread across major AI hubs:
- San Francisco, CA (2 users)
- International: London, Tokyo, Bangalore, Barcelona, Oxford, Lagos, Boston, Tel Aviv, Paris, Palo Alto, São Paulo

## Company Distribution

Users represent diverse AI ecosystem:
- Big Tech: OpenAI, DeepMind, Microsoft, Google Brain alumni
- AI Startups: Anthropic, Pinecone, Scale AI, Hugging Face
- Research Institutions: Stanford, Alignment Research Center
- Autonomous Vehicles: Waymo
- Open Source: Mozilla, Hugging Face
- Consulting: Freelance

## Expertise Tag Coverage

The demo data covers all 19 AI tags in the platform:
- **Core AI/ML**: LLMs (10 users), Agents, Fine-tuning, Prompting
- **Infrastructure**: Vector DBs, Embeddings, Training (4 users), Inference
- **Governance**: Ethics (5 users), Safety, Benchmarks, Datasets (5 users), Tools (6 users)
- **Applications**: Computer Vision, NLP (4 users), Speech, Robotics, RL

## Data Safety

- All demo users use fake email addresses with `@example.com` domain
- Avatar URLs point to generic GitHub avatar examples
- Company and location data is realistic but anonymized
- The script detects existing users and skips duplicates
- Clean command safely removes only demo users by email pattern

## API Testing

With demo data loaded, you can test:

```bash
# Get user profile
curl http://localhost:4000/api/users/sarahchen

# Search users by expertise
curl "http://localhost:4000/api/users?expertise=LLMs,Ethics"

# Search users by text
curl "http://localhost:4000/api/users?q=researcher"

# Check username availability
curl -X POST http://localhost:4000/api/users/check-username \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser"}'
```

## Customization

To modify the demo data:

1. Edit the `SAMPLE_USERS` array in `seed_demo_data.py`
2. Ensure all `expertise_tags` are from the valid `AI_TAGS` list
3. Use unique email addresses with `@example.com` domain
4. Follow the existing data structure for consistency

## Troubleshooting

**Database Connection Error**: Ensure PostgreSQL is running and DATABASE_URL in `.env` is correct.

**Migration Error**: Run `uv run alembic upgrade head` before seeding data.

**Permission Error**: Ensure the user in DATABASE_URL has CREATE/INSERT permissions.

**Duplicate Users**: The script automatically skips existing users with the same email.