"""
Módulos de Machine Learning para Datathon - Tech Challenge Fase 5

Pacotes:
- data_processing: Funções de EDA e preparação de dados
- baseline: Modelo baseline determinístico
- adaptive_model: Algoritmo Epsilon-Greedy
- api: API FastAPI para recomendações
- inference: Script de inferência
"""

from .data_processing import (
    analyze_missing_values,
    detect_outliers_iqr,
    find_temporal_leakage,
    treat_missing_values,
    encode_categorical,
    normalize_features,
    prepare_data_pipeline
)

__version__ = "0.1.0"
__all__ = [
    'analyze_missing_values',
    'detect_outliers_iqr',
    'find_temporal_leakage',
    'treat_missing_values',
    'encode_categorical',
    'normalize_features',
    'prepare_data_pipeline'
]
