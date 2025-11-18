"""
Base Extractor Class for Agentic Pattern Extraction
Provides common functionality for all framework-specific extractors
"""
import json
import yaml
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class BaseExtractor(ABC):
    """Abstract base class for framework-specific extractors"""

    def __init__(self, framework_name: str):
        self.framework_name = framework_name

    def make_id(self, prefix: str = "pat") -> str:
        """Generate unique ID for entities"""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def get_readable_filename(self, source_file: Path) -> str:
        """Generate readable filename: framework_sourcename"""
        source_stem = source_file.stem  # e.g., "research_team"
        return f"{self.framework_name}_{source_stem}"

    def now_iso(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.utcnow().isoformat() + "Z"

    def load_file(self, file_path: Path) -> Any:
        """Load file based on extension"""
        if file_path.suffix.lower() == '.json':
            return self._load_json(file_path)
        elif file_path.suffix.lower() in ['.yaml', '.yml']:
            return self._load_yaml(file_path)
        elif file_path.suffix.lower() == '.py':
            return self._load_python(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def _load_json(self, file_path: Path) -> Dict:
        """Load JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_yaml(self, file_path: Path) -> Dict:
        """Load YAML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _load_python(self, file_path: Path) -> str:
        """Load Python file as text"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @abstractmethod
    def extract(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract agentic pattern from file
        Must be implemented by framework-specific extractors

        Returns:
            Dictionary with extracted pattern data
        """
        pass

    def normalize(self, raw_data: Dict[str, Any], source_file: Path) -> Dict[str, Any]:
        """
        Normalize extracted data to standard format

        Returns standardized pattern structure:
        {
            "id": str,
            "framework": str,
            "source_file": str,
            "title": str,
            "description": str,
            "objective": str,
            "created_at": str (ISO timestamp),
            "agents": [
                {
                    "id": str,
                    "name": str,
                    "role": str,
                    "description": str,
                    "goal": str,
                    "backstory": str,
                    "tasks": [str],  # task IDs
                    "tools": [str],  # tool IDs
                    "language_model": str,
                    "memory": bool
                }
            ],
            "tasks": [
                {
                    "id": str,
                    "title": str,
                    "description": str,
                    "expected_output": str,
                    "assigned_agent": str  # agent ID
                }
            ],
            "tools": [
                {
                    "id": str,
                    "name": str,
                    "description": str,
                    "type": str,
                    "resource": str  # resource ID if applicable
                }
            ],
            "resources": [
                {
                    "id": str,
                    "name": str,
                    "type": str,  # e.g., "database", "api", "search_engine"
                    "description": str
                }
            ],
            "workflow_pattern": {
                "type": str,  # "Sequential", "Parallel", "Nested"
                "steps": [
                    {
                        "id": str,
                        "order": int,
                        "task_id": str,
                        "agent_id": str,
                        "next_step": str  # next step ID, null if last
                    }
                ]
            },
            "team": {
                "name": str,
                "process": str  # e.g., "sequential", "hierarchical"
            },
            "provenance": {
                "extracted_from": str,
                "extraction_date": str,
                "extractor_version": str
            }
        }
        """
        pattern_id = self.make_id("pattern")

        normalized = {
            "id": pattern_id,
            "readable_name": self.get_readable_filename(source_file),
            "framework": self.framework_name,
            "source_file": str(source_file),
            "title": raw_data.get("title", f"{self.framework_name} pattern {pattern_id}"),
            "description": raw_data.get("description", ""),
            "objective": raw_data.get("objective", ""),
            "created_at": self.now_iso(),
            "agents": self._normalize_agents(raw_data.get("agents", [])),
            "tasks": self._normalize_tasks(raw_data.get("tasks", [])),
            "tools": self._normalize_tools(raw_data.get("tools", [])),
            "resources": self._normalize_resources(raw_data.get("resources", [])),
            "workflow_pattern": self._normalize_workflow(raw_data.get("workflow", {})),
            "team": self._normalize_team(raw_data.get("team", {})),
            "provenance": {
                "extracted_from": str(source_file),
                "extraction_date": self.now_iso(),
                "extractor_version": "1.0.0"
            }
        }

        # Link agents to tasks
        normalized = self._link_agent_tasks(normalized)

        return normalized

    def _normalize_agents(self, agents: List[Dict]) -> List[Dict]:
        """Normalize agent data"""
        normalized_agents = []
        for agent in agents:
            agent_id = self.make_id("agent")
            normalized_agents.append({
                "id": agent_id,
                "name": agent.get("name", agent.get("role", "Agent")),
                "role": agent.get("role", ""),
                "description": agent.get("description", ""),
                "goal": agent.get("goal", ""),
                "backstory": agent.get("backstory", ""),
                "tasks": agent.get("tasks", []),  # Will be populated later
                "tools": agent.get("tools", []),
                "language_model": agent.get("llm", agent.get("model", agent.get("language_model"))),
                "memory": agent.get("memory", False),
                "humanInputMode": agent.get("humanInputMode")
            })
        return normalized_agents

    def _normalize_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Normalize task data"""
        normalized_tasks = []
        for task in tasks:
            task_id = self.make_id("task")
            normalized_tasks.append({
                "id": task_id,
                "title": task.get("title", task.get("description", "Task")[:50]),
                "description": task.get("description", ""),
                "expected_output": task.get("expected_output", ""),
                "assigned_agent": task.get("agent", "")  # Will be linked later
            })
        return normalized_tasks

    def _normalize_tools(self, tools: List[Dict]) -> List[Dict]:
        """Normalize tool data"""
        normalized_tools = []
        for tool in tools:
            tool_id = self.make_id("tool")
            normalized_tools.append({
                "id": tool_id,
                "name": tool.get("name", "Tool"),
                "description": tool.get("description", ""),
                "type": tool.get("type", ""),
                "resource": tool.get("resource", "")
            })
        return normalized_tools

    def _normalize_resources(self, resources: List[Dict]) -> List[Dict]:
        """Normalize resource data"""
        normalized_resources = []
        for resource in resources:
            resource_id = self.make_id("resource")
            normalized_resources.append({
                "id": resource_id,
                "name": resource.get("name", "Resource"),
                "type": resource.get("type", ""),
                "description": resource.get("description", "")
            })
        return normalized_resources

    def _normalize_workflow(self, workflow: Dict) -> Dict:
        """Normalize workflow pattern data"""
        return {
            "type": workflow.get("type", "Sequential"),
            "steps": workflow.get("steps", [])
        }

    def _normalize_team(self, team: Dict) -> Dict:
        """Normalize team configuration"""
        return {
            "name": team.get("name", ""),
            "process": team.get("process", "sequential")
        }

    def _link_agent_tasks(self, pattern: Dict) -> Dict:
        """Link agents to their tasks and establish relationships"""
        # This is a basic implementation
        # Framework-specific extractors should override with better logic
        return pattern

    def validate(self, pattern: Dict) -> bool:
        """
        Validate extracted pattern against schema
        Returns True if valid, raises ValueError if invalid
        """
        required_fields = ["id", "framework", "agents", "tasks", "workflow_pattern"]

        for field in required_fields:
            if field not in pattern:
                raise ValueError(f"Missing required field: {field}")

        if not pattern["agents"]:
            raise ValueError("Pattern must have at least one agent")

        return True

    def process_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Complete pipeline: extract, normalize, validate
        Returns normalized pattern or None if error
        """
        try:
            # Extract raw data
            raw_data = self.extract(file_path)

            # Normalize to standard format
            normalized = self.normalize(raw_data, file_path)

            # Validate
            self.validate(normalized)

            return normalized

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
