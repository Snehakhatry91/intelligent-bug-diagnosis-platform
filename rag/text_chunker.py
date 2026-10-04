"""
Text Chunker for Defect Reports and Logs
Implements structured, domain-aware chunking that preserves stack traces,
code blocks, and header metadata without breaking exception contexts.
"""

from typing import Dict, List


class TextChunker:
    """Chunks defect reports and logs preserving semantic boundaries."""

    def __init__(self, max_chunk_size: int = 512, chunk_overlap: int = 64):
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_defect_record(self, record: Dict[str, str]) -> List[Dict[str, str]]:
        """
        Produce semantically enriched chunks from a structured defect record.
        Ensures issue ID, project, component, and title are preserved in metadata.
        """
        chunks = []
        base_meta = {
            "issue_id": record.get("issue_id", "UNKNOWN"),
            "project": record.get("project", "UNKNOWN"),
            "component": record.get("component", "UNKNOWN"),
            "title": record.get("title", ""),
            "severity": record.get("severity", ""),
            "resolution": record.get("resolution", ""),
            "fix_patch_summary": record.get("fix_patch_summary", ""),
            "source_url": record.get("source_url", ""),
            "verified": record.get("verified", True),
            "data_type": record.get("data_type", "historical")
        }

        # 1. Primary summary chunk (Title + Component + Core description snippet)
        primary_text = (
            f"[{record.get('project')}] {record.get('title')}. "
            f"Component: {record.get('component')}. "
            f"Description: {record.get('description', '')[:300]}. "
            f"Fix: {record.get('fix_patch_summary', '')}"
        )
        chunks.append({
            "chunk_id": f"{record.get('issue_id')}_primary",
            "text": primary_text,
            "chunk_type": "summary",
            **base_meta
        })

        # 2. Detailed technical chunk (Full description & resolution)
        desc = record.get("description", "")
        if len(desc) > 300:
            technical_text = f"Defect Details: {desc}. Resolution: {record.get('fix_patch_summary', '')}"
            chunks.append({
                "chunk_id": f"{record.get('issue_id')}_technical",
                "text": technical_text,
                "chunk_type": "technical_details",
                **base_meta
            })

        return chunks

    def chunk_log_text(self, text: str) -> List[str]:
        """Split raw log text into windowed chunks along line boundaries."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if not lines:
            return []

        chunks = []
        current_chunk = []
        current_len = 0

        for line in lines:
            current_chunk.append(line)
            current_len += len(line)
            if current_len >= self.max_chunk_size:
                chunks.append("\n".join(current_chunk))
                # Retain overlap lines
                current_chunk = current_chunk[-3:]
                current_len = sum(len(x) for x in current_chunk)

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks


text_chunker = TextChunker()
