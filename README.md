# Astrololo

High-precision astrology interpretation engine with template-based and AI-powered analysis.

## Overview

Astrololo provides both traditional (template-based) and modern (AI-powered) astrology interpretation engines, optimized for accuracy and multilingual support (Vietnamese and English).

## Features

### Traditional Engine (Template-based)
- Planetary dignity (rulership, exaltation, triplicity, term, face)
- Essential dignities scoring (+5 to -5 per planet)
- House system support (7 systems: Placidus, Koch, Equal, Whole Sign, Regiomontanus, Campanus, Porphyry)
- Aspect patterns (Grand Trine, T-Square, Stellium, Grand Cross, Yod, Kite, Mystic Rectangle)
- Element and quality balance analysis
- Dispositor chains
- Multi-layer interpretation (planet-sign, planet-house, aspects, combinations)

### AI-Enhanced Engine
- Optional AI interpretation powered by OpenAI or local Ollama
- Template text provides base interpretation
- AI adds extended, nuanced analysis
- Graceful fallback when AI is unavailable

### Web Interface
- Tab-based navigation (Natal Chart / Transit / Synastry)
- Interactive D3.js chart wheel visualization
- Responsive design for desktop and mobile
- Real-time interpretation generation

## Architecture

### Backend (Python/FastAPI)
- Core astrological calculations using Swiss Ephemeris (with pure-Python fallback)
- Template-based interpretation engine with 8 rule modules
- Optional AI interpretation layer
- RESTful API with 7 endpoints

### Frontend (React/TypeScript/Vite)
- Component-based architecture
- Tab-based navigation for different chart types
- D3.js chart wheel visualization
- Bilingual support (Vietnamese primary, English fallback)

## Quick Start

### Backend

1. Clone the repository
2. Ensure Python 3.11+ is installed
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Start the server:
   ```bash
   python -m astrololo.api.main
   ```

### Frontend

1. Navigate to frontend directory
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start development server:
   ```bash
   npm run dev
   ```

### Docker (Recommended)

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

## API Endpoints

### Natal Chart
- **POST** `/api/v1/natal`
- Calculates birth chart from birth data
- Returns planetary positions, houses, aspects

### Interpretation
- **POST** `/api/v1/interpret`
- Generates template-based interpretation
- Returns structured analysis by category

### AI Interpretation
- **POST** `/api/v1/interpret/ai`
- Generates AI-powered interpretation
- Combines template with AI insights

### Transit
- **POST** `/api/v1/transit`
- Calculates transit planets for a specific date
- Returns transit-to-natal aspects

### Synastry
- **POST** `/api/v1/synastry`
- Compares two birth charts for compatibility
- Returns cross-aspects between partners

### Constants
- **GET** `/api/v1/constants`
- Returns astrological constants (planets, signs, aspects, etc.)

### Health Check
- **GET** `/api/v1/health`
- Returns system status and configuration

## Configuration

### AI Setup (Optional)
Set the following environment variables to enable AI interpretation:

```bash
# For OpenAI
ASTRO_AI_API_KEY=your-openai-api-key
ASTRO_AI_PROVIDER=openai
ASTRO_AI_MODEL=gpt-4o-mini

# For local Ollama
ASTRO_AI_PROVIDER=ollama
ASTRO_AI_MODEL=llama3.2
```

### Swiss Ephemeris Data
Swiss Ephemeris data files must be placed in the `ephe/` directory:
- `semo_18.se1` (Moon ephemeris)
- `sepl_18.se1` (Planetary ephemeris)
- `seas_18.se1` (Asteroid ephemeris)

## Testing

### Backend Tests
```bash
cd backend
python -m backend.tests.backtest
```

All 144 backtests pass.

### Frontend Tests
```bash
cd frontend
npm test
```

## Development

### Project Structure

Backend (`backend/astrololo/`):
- `core/` - Core astrological logic (ephemeris, aspects, houses)
- `analysis/` - Chart computation (natal, transit, synastry)
- `models/` - Pydantic data models
- `interpretation/` - Interpretation engine (template + AI)

Frontend (`frontend/src/`):
- `components/` - React components
- `api.ts` - API client

### Contribution Guidelines

1. Follow existing code style and conventions
2. Add tests for new features
3. Update documentation when making changes
4. Run linting and type checking before committing
5. Test thoroughly in all supported browsers

## License

This project is licensed under the MIT License.

## Contact

For support or questions, please reach out through the project's issue tracker.
