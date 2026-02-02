"""
HuggingFace Datasets API Client for MoltBattle

Fetches logical reasoning questions from HuggingFace datasets:
- ProofWriter (tasksource/proofwriter): Rule-based logical deduction
- RuleTaker (tasksource/ruletaker): Facts + rules → hypothesis truth
- ReClor (voidful/ReClor): Exam-style logical reasoning MCQ
"""

import hashlib
import random
import time
from dataclasses import dataclass
from typing import Optional
import httpx
from functools import lru_cache

# HuggingFace Dataset Viewer API base URL
HF_API_BASE = "https://datasets-server.huggingface.co"

# Dataset configurations
DATASETS = {
    "proofwriter": {
        "name": "tasksource/proofwriter",
        "config": "default",
        "split": "validation",
        "type": "true_false_unknown",
    },
    "ruletaker": {
        "name": "tasksource/ruletaker",
        "config": "default", 
        "split": "dev",  # ruletaker uses 'dev' not 'validation'
        "type": "true_false_unknown",
    },
    "reclor": {
        "name": "metaeval/reclor",  # voidful/ReClor is broken, use metaeval mirror
        "config": "default",
        "split": "validation",
        "type": "mcq",
    },
}

# Server-side salt for answer hashing (should be in env vars in production)
ANSWER_SALT = "moltbattle_2024_secret_salt_xK9mP2nQ"


@dataclass
class NormalizedQuestion:
    """Normalized question format for all datasets."""
    prompt: str
    choices: list[str]
    correct_answer: str  # The correct choice value
    dataset: str
    config: str
    split: str
    row_offset: int
    raw_data: dict  # Original row data for debugging


class HFDatasetsClient:
    """Client for fetching questions from HuggingFace Dataset Viewer API."""
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self._splits_cache: dict[str, dict] = {}
        self._splits_cache_time: dict[str, float] = {}
        self._cache_ttl = 3600  # 1 hour
    
    def _get_cached_splits(self, dataset: str) -> Optional[dict]:
        """Get cached splits info if still valid."""
        if dataset in self._splits_cache:
            if time.time() - self._splits_cache_time[dataset] < self._cache_ttl:
                return self._splits_cache[dataset]
        return None
    
    def get_splits(self, dataset: str) -> dict:
        """
        Get available configs and splits for a dataset.
        
        GET https://datasets-server.huggingface.co/splits?dataset=<DATASET>
        """
        cached = self._get_cached_splits(dataset)
        if cached:
            return cached
        
        url = f"{HF_API_BASE}/splits"
        params = {"dataset": dataset}
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        self._splits_cache[dataset] = data
        self._splits_cache_time[dataset] = time.time()
        return data
    
    def get_row(self, dataset: str, config: str, split: str, offset: int) -> dict:
        """
        Fetch a single row from a dataset.
        
        GET https://datasets-server.huggingface.co/rows?dataset=<DATASET>&config=<CONFIG>&split=<SPLIT>&offset=<N>&length=1
        """
        url = f"{HF_API_BASE}/rows"
        params = {
            "dataset": dataset,
            "config": config,
            "split": split,
            "offset": offset,
            "length": 1,
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        if not data.get("rows"):
            raise ValueError(f"No row found at offset {offset}")
        
        return data["rows"][0]["row"]
    
    def get_rows_batch(self, dataset: str, config: str, split: str, offset: int, length: int = 100) -> list[dict]:
        """
        Fetch multiple rows from a dataset in a single request.
        
        GET https://datasets-server.huggingface.co/rows?dataset=<DATASET>&config=<CONFIG>&split=<SPLIT>&offset=<N>&length=<L>
        """
        url = f"{HF_API_BASE}/rows"
        params = {
            "dataset": dataset,
            "config": config,
            "split": split,
            "offset": offset,
            "length": length,
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        return [row_data["row"] for row_data in data.get("rows", [])]
    
    def get_split_size(self, dataset: str, config: str, split: str) -> int:
        """Get the number of rows in a split using the /size endpoint."""
        url = f"{HF_API_BASE}/size"
        params = {"dataset": dataset}
        
        with httpx.Client(timeout=self.timeout) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        # Look through the splits array in the size response
        for split_info in data.get("size", {}).get("splits", []):
            if split_info.get("config") == config and split_info.get("split") == split:
                return split_info.get("num_rows", 0)
        
        return 0


def normalize_proofwriter(row: dict, dataset: str, config: str, split: str, offset: int) -> NormalizedQuestion:
    """
    Normalize ProofWriter row to standard format.
    
    ProofWriter schema typically has:
    - theory: facts and rules
    - question: the query to answer
    - label: True/False/Unknown
    """
    theory = row.get("theory", row.get("context", ""))
    question = row.get("question", row.get("query", ""))
    
    # Label can be various formats
    label = row.get("label", row.get("answer", ""))
    if isinstance(label, bool):
        correct = "TRUE" if label else "FALSE"
    elif isinstance(label, int):
        label_map = {0: "FALSE", 1: "TRUE", 2: "UNKNOWN"}
        correct = label_map.get(label, "UNKNOWN")
    else:
        label_str = str(label).upper().strip()
        if label_str in ["TRUE", "FALSE", "UNKNOWN"]:
            correct = label_str
        elif label_str in ["T", "F", "U"]:
            correct = {"T": "TRUE", "F": "FALSE", "U": "UNKNOWN"}[label_str]
        else:
            correct = "UNKNOWN"
    
    prompt = f"""**Context (Facts and Rules):**
{theory}

**Question:**
{question}

Is the statement TRUE, FALSE, or UNKNOWN based on the given facts and rules?"""
    
    return NormalizedQuestion(
        prompt=prompt,
        choices=["TRUE", "FALSE", "UNKNOWN"],
        correct_answer=correct,
        dataset=dataset,
        config=config,
        split=split,
        row_offset=offset,
        raw_data=row,
    )


def normalize_ruletaker(row: dict, dataset: str, config: str, split: str, offset: int) -> NormalizedQuestion:
    """
    Normalize RuleTaker row to standard format.
    
    RuleTaker schema typically has:
    - context: facts and rules
    - question/hypothesis: the statement to verify
    - label: truth value
    """
    context = row.get("context", row.get("facts", ""))
    hypothesis = row.get("question", row.get("hypothesis", row.get("query", "")))
    
    label = row.get("label", row.get("answer", ""))
    if isinstance(label, bool):
        correct = "TRUE" if label else "FALSE"
    elif isinstance(label, int):
        label_map = {0: "FALSE", 1: "TRUE", 2: "UNKNOWN"}
        correct = label_map.get(label, "UNKNOWN")
    else:
        label_str = str(label).upper().strip()
        if label_str in ["TRUE", "FALSE", "UNKNOWN"]:
            correct = label_str
        else:
            correct = "UNKNOWN"
    
    prompt = f"""**Given Facts and Rules:**
{context}

**Hypothesis:**
{hypothesis}

Based on the facts and rules provided, is the hypothesis TRUE, FALSE, or UNKNOWN?"""
    
    return NormalizedQuestion(
        prompt=prompt,
        choices=["TRUE", "FALSE", "UNKNOWN"],
        correct_answer=correct,
        dataset=dataset,
        config=config,
        split=split,
        row_offset=offset,
        raw_data=row,
    )


def normalize_reclor(row: dict, dataset: str, config: str, split: str, offset: int) -> NormalizedQuestion:
    """
    Normalize ReClor row to standard format.
    
    ReClor schema has:
    - context/passage: the reading passage
    - question: the logical reasoning question
    - answers: list of 4 answer options
    - label: correct answer index (0-3)
    """
    passage = row.get("context", row.get("passage", ""))
    question = row.get("question", "")
    answers = row.get("answers", row.get("options", []))
    label = row.get("label", row.get("answer", 0))
    
    # Ensure we have 4 answers
    while len(answers) < 4:
        answers.append("N/A")
    
    # Map label to A/B/C/D
    if isinstance(label, int):
        correct = ["A", "B", "C", "D"][label]
    else:
        correct = str(label).upper()
    
    # Shuffle options for anti-cheat (and track the mapping)
    options_with_idx = list(enumerate(answers[:4]))
    random.shuffle(options_with_idx)
    
    # Find where the correct answer ended up after shuffle
    new_correct_idx = next(i for i, (orig_idx, _) in enumerate(options_with_idx) if orig_idx == label)
    correct = ["A", "B", "C", "D"][new_correct_idx]
    
    # Format shuffled options
    shuffled_answers = [opt for _, opt in options_with_idx]
    options_text = "\n".join([
        f"A) {shuffled_answers[0]}",
        f"B) {shuffled_answers[1]}",
        f"C) {shuffled_answers[2]}",
        f"D) {shuffled_answers[3]}",
    ])
    
    prompt = f"""**Passage:**
{passage}

**Question:**
{question}

**Answer Options:**
{options_text}

Select the best answer: A, B, C, or D"""
    
    return NormalizedQuestion(
        prompt=prompt,
        choices=["A", "B", "C", "D"],
        correct_answer=correct,
        dataset=dataset,
        config=config,
        split=split,
        row_offset=offset,
        raw_data=row,
    )


# Normalizer registry
NORMALIZERS = {
    "tasksource/proofwriter": normalize_proofwriter,
    "tasksource/ruletaker": normalize_ruletaker,
    "metaeval/reclor": normalize_reclor,
}


def hash_answer(answer: str, combat_id: int) -> str:
    """Create a salted hash of the correct answer for secure storage."""
    to_hash = f"{ANSWER_SALT}:{combat_id}:{answer.upper().strip()}"
    return hashlib.sha256(to_hash.encode()).hexdigest()


def verify_answer(submitted: str, stored_hash: str, combat_id: int) -> bool:
    """Verify a submitted answer against the stored hash."""
    submitted_hash = hash_answer(submitted, combat_id)
    return submitted_hash == stored_hash


class QuestionService:
    """Service for fetching and managing combat questions."""
    
    def __init__(self):
        self.client = HFDatasetsClient()
        self._size_cache: dict[str, int] = {}
    
    def get_random_question(
        self,
        combat_id: int,
        mode: str = "formal_logic",
        exclude_offsets: Optional[dict[str, list[int]]] = None
    ) -> NormalizedQuestion:
        """
        Fetch a random question from HuggingFace datasets.
        
        Args:
            combat_id: The combat ID (used for answer hashing)
            mode: "formal_logic" (ProofWriter/RuleTaker) or "argument_logic" (ReClor)
            exclude_offsets: Dict of {dataset: [offsets]} to avoid repeats
        
        Returns:
            NormalizedQuestion with all fields populated
        """
        exclude_offsets = exclude_offsets or {}
        
        # Select dataset based on mode
        if mode == "argument_logic":
            dataset_keys = ["reclor"]
        else:  # formal_logic (default)
            dataset_keys = ["proofwriter", "ruletaker"]
        
        # Pick a random dataset from the mode
        dataset_key = random.choice(dataset_keys)
        dataset_config = DATASETS[dataset_key]
        
        dataset_name = dataset_config["name"]
        config = dataset_config["config"]
        split = dataset_config["split"]
        
        # Get split size (cached)
        cache_key = f"{dataset_name}:{config}:{split}"
        if cache_key not in self._size_cache:
            self._size_cache[cache_key] = self.client.get_split_size(dataset_name, config, split)
        
        split_size = self._size_cache[cache_key]
        if split_size == 0:
            raise ValueError(f"Dataset {dataset_name} has no rows in {config}/{split}")
        
        # Pick random offset, avoiding excluded ones
        excluded = set(exclude_offsets.get(dataset_name, []))
        available = [i for i in range(split_size) if i not in excluded]
        
        if not available:
            # If all excluded, just pick any (shouldn't happen in practice)
            offset = random.randint(0, split_size - 1)
        else:
            offset = random.choice(available)
        
        # Fetch the row
        row = self.client.get_row(dataset_name, config, split, offset)
        
        # Normalize based on dataset type
        normalizer = NORMALIZERS.get(dataset_name)
        if not normalizer:
            raise ValueError(f"No normalizer for dataset: {dataset_name}")
        
        return normalizer(row, dataset_name, config, split, offset)
    
    def create_combat_question(
        self,
        combat_id: int,
        mode: str = "formal_logic"
    ) -> tuple[NormalizedQuestion, str]:
        """
        Create a question for a combat and return the answer hash.
        
        Returns:
            Tuple of (NormalizedQuestion, answer_key_hash)
        """
        question = self.get_random_question(combat_id, mode)
        answer_hash = hash_answer(question.correct_answer, combat_id)
        return question, answer_hash


# Global instance
question_service = QuestionService()
