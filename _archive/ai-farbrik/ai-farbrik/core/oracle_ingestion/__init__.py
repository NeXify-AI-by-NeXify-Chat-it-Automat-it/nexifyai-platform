"""NeXifyAI Core: Oracle Ingestion — __init__"""
from .pipeline import OracleIngestionPipeline, IngestedDocument, PipelineStage, SourceType

__all__ = [
    "OracleIngestionPipeline",
    "IngestedDocument",
    "PipelineStage",
    "SourceType",
]
