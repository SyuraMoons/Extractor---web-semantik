# Agentic Knowledge Graph Extractor

Extract agentic AI patterns from multiple frameworks and convert them to RDF knowledge graphs.

## Overview

This tool automatically extracts agent patterns from CrewAI, LangGraph, AutoGen, and MastraAI frameworks, normalizes them to JSON, and converts them to RDF/Turtle format using the AgentO ontology.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Extract Patterns to JSON

```bash
cd src/extractors
py main.py
```

This will extract 51 patterns from `data/raw/` and save them to `data/normalized/`.

### 3. Convert JSON to RDF

```bash
cd ../..
py scripts/json_to_rdf.py
```

This will convert all JSON patterns to RDF/Turtle format in `data/rdf/`.

## What You Get

After running both steps, you'll have:

- **51 JSON files** with readable names (e.g., `crewai_researcher_team.json`, `autogen_chess_game.json`)
- **51 RDF/Turtle files** (e.g., `langraph_supervisor.ttl`, `mastraai_code_review.ttl`)
- **1 merged RDF file** (`agentic-patterns.ttl`) with 1,539 triples
- **AgentO ontology** in `ontology/agento.ttl`

## Project Structure

```
agentic-kg-extractor/
├── data/
│   ├── raw/                    # 51 source files (4 frameworks)
│   ├── normalized/             # 51 JSON patterns (output)
│   └── rdf/                    # 51 TTL files + merged (output)
├── ontology/
│   ├── agento.ttl              # AgentO ontology (OWL/RDF)
│   └── README.md               # Ontology documentation
├── src/extractors/             # Framework-specific extractors
│   ├── main.py                 # Extraction pipeline
│   ├── base_extractor.py       # Base extractor class
│   ├── crewai_extractor.py     # CrewAI parser
│   ├── langraph_extractor.py   # LangGraph parser
│   ├── autogen_extractor.py    # AutoGen parser
│   └── mastraai_extractor.py   # MastraAI parser
├── scripts/
│   └── json_to_rdf.py          # JSON to RDF converter
└── README.md
```

## Output Examples

### JSON Output (data/normalized/)
```
autogen_chess_game.json
crewai_researcher_team.json
langraph_supervisor.json
mastraai_code_review.json
```

**Sample JSON Structure:**
```json
{
  "id": "pattern_abc123",
  "readable_name": "autogen_chess_game",
  "framework": "autogen",
  "source_file": "../../data/raw/autogen/chess_game.py",
  "agents": [
    {
      "id": "agent_xyz789",
      "name": "chess_game_assistant",
      "role": "AssistantAgent",
      "humanInputMode": "NEVER",
      ...
    }
  ],
  "tasks": [...],
  "workflow_pattern": {...}
}
```

### RDF Output (data/rdf/)
```
autogen_chess_game.ttl
crewai_researcher_team.ttl
langraph_supervisor.ttl
mastraai_code_review.ttl
agentic-patterns.ttl  (merged file)
```

**Sample RDF/Turtle:**
```turtle
@prefix agento: <http://www.w3id.org/agentic-ai/onto#> .
@prefix data: <http://www.w3id.org/agentic-ai/data/> .

data:pattern_abc123 a agento:Pattern ;
    agento:framework "autogen"^^xsd:string ;
    agento:hasAgentMember data:agent_xyz789 .

data:agent_xyz789 a agento:Agent ;
    agento:agentName "chess_game_assistant"^^xsd:string ;
    agento:humanInputMode "NEVER"^^xsd:string .
```

## Frameworks Supported

| Framework | Patterns | Input Format |
|-----------|----------|--------------|
| CrewAI    | 14       | `.py` files  |
| LangGraph | 13       | `.py` files  |
| AutoGen   | 12       | `.py` files  |
| MastraAI  | 12       | `.json/.yaml` files |
| **Total** | **51**   | |

## Statistics

- **Total Patterns**: 51
- **Total RDF Triples**: 1,539
- **Ontology Classes**: 13
- **Ontology Properties**: 48 (16 object + 32 datatype)
- **Extraction Success Rate**: 100%

## Adding New Patterns

1. Add your pattern files to `data/raw/{framework}/`
   - Use `.py` files for CrewAI, LangGraph, AutoGen
   - Use `.json` or `.yaml` files for MastraAI

2. Re-run the extraction:
   ```bash
   cd src/extractors
   py main.py
   ```

3. Re-run the RDF conversion:
   ```bash
   cd ../..
   py scripts/json_to_rdf.py
   ```

## Documentation

- **Ontology**: See `ontology/README.md` for AgentO ontology specification
- **Extractors**: See `src/extractors/README.md` for extractor implementation details
- **Schema**: See `scripts/agentic_pattern.schema.json` for JSON schema

## Requirements

- Python 3.8+
- PyYAML 6.0.3
- rdflib 7.4.0
- jsonschema 4.25.1

## License

MIT
