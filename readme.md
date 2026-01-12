# Problem Solver 

**The problem**: People tend to go along with what's going on. They don't want to stick their heads up or seem at odds with management, or the social order of the workplace. The result is that problems fester and grow, with people coming up with complex costly mechanisms to work around the problem (whether social or technical), with the result of those problems ultimately becoming a part of the company culture. 

The intention of this tool is to provide a way to socially surface problems and provide remediation. Someone, somewhere within your company is attentive and knows how to fix it - if you want to. 

This is a Flask-based web application for collective, quasi-anonymous workplace problem-solving.

## Purpose

The Problem Solver Platform helps organizations address workplace challenges through:
- **Problem Submission**: Employees can propose problems with potential solutions
- **Collective Intelligence**: Peers can contribute additional solutions
- **Structured Evaluation**: Multi-criteria evaluation of problems and solutions
- **Quasi-Anonymity**: Pseudonymous participation to encourage honesty
- **Progress Tracking**: Monitor problem resolution from open to implemented

## Features (Current vs. Planned)

### Current Features
- 🔐 Google OAuth authentication
- 📝 Survey-based problem response collection
- ⭐ Basic evaluation system
- 📊 Response tracking with aggregate scores

### Planned Features
- 🏷️ Full problem/solution submission with tags
- 🗳️ Solution voting and ranking system
- 📈 Multi-criteria evaluation (severity, impact, feasibility)
- 🔔 Notification system with email digests
- 👥 Admin moderation panel
- 🌐 REST API for integrations
- 📱 Mobile-responsive design
- 🐳 Docker deployment support

## Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud Console project (for OAuth)
- SQLite (development) or PostgreSQL (production)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/problem-solver.git
cd problem-solver

# Install dependencies
make install

# Configure the application
cp config.example.json configuration.json
# Edit configuration.json with your settings

# Initialize the database
make init-db

# Start the development server
make run
```

The application will be available at http://localhost:8000

### Using Docker

```bash
# Build and run with Docker
make docker-build
make docker-run
```

## Project Structure

```
problem-solver/
├── src/
│   ├── problemsolver.py           # Main Flask application
│   ├── configuration.json         # Application configuration
│   └── templates/                 # HTML templates (to be added)
├── docs/
│   ├── completion-specification.md  # Complete feature specification
│   ├── user-guide.md              # User documentation (to be added)
│   ├── api-documentation.md       # API reference (to be added)
│   └── deployment-guide.md        # Deployment instructions (to be added)
├── tests/                         # Test suite (to be added)
├── Makefile                       # Build and deployment targets
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker configuration
└── docker-compose.yml             # Docker orchestration
```

## Makefile Commands

| Command | Description |
|---------|-------------|
| `make install` | Create virtual environment and install dependencies |
| `make run` | Start development server |
| `make dev` | Start development server with auto-reload |
| `make test` | Run test suite |
| `make lint` | Run code linters |
| `make migrate` | Create database migrations |
| `make upgrade` | Apply database migrations |
| `make init-db` | Initialize database with seed data |
| `make reset-db` | Reset database (WARNING: destroys data) |
| `make docker-build` | Build Docker image |
| `make docker-run` | Run Docker container |
| `make clean` | Remove build artifacts |
| `make help` | Show all available commands |

## Configuration

Copy `config.example.json` to `configuration.json` and configure:

```json
{
    "DATABASE_URI": "sqlite:///problem_solver.db",
    "SECRET_KEY": "your-secret-key",
    "GOOGLE_CLIENT_ID": "your-google-client-id",
    "GOOGLE_CLIENT_SECRET": "your-google-client-secret"
}
```

## Documentation

- [Completion Specification](docs/completion-specification.md) - Complete feature and implementation plan
- [User Guide](docs/user-guide.md) - How to use the platform (coming soon)
- [API Documentation](docs/api-documentation.md) - REST API reference (coming soon)
- [Deployment Guide](docs/deployment-guide.md) - Production deployment (coming soon)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Roadmap

See [Completion Specification](docs/completion-specification.md) for detailed implementation plan.

### Phase 1: Foundation (Current)
- [x] Flask application framework
- [x] Google OAuth integration
- [x] Basic database models
- [ ] HTML templates
- [ ] Problem submission flow

### Phase 2: Core Features
- [ ] Solution submission and display
- [ ] Voting/ranking system
- [ ] Multi-criteria evaluation
- [ ] Dashboard with problem feed
- [ ] Search and filter

### Phase 3: Extended Features
- [ ] Quasi-anonymous features
- [ ] Notification system
- [ ] Admin panel
- [ ] REST API

### Phase 4: Polish
- [ ] Docker production deployment
- [ ] Comprehensive testing
- [ ] Full documentation
- [ ] Performance optimization
