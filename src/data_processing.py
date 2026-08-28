"""
Funções para exploração, limpeza e preparação de dados.

Esse módulo fornece funções reutilizáveis para:
- Análise de valores faltantes e outliers
- Transformação de variáveis
- Normalização e encoding
- Detecção de vazamento temporal
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
from typing import Dict, List, Tuple, Optional


def analyze_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Retorna relatório detalhado de valores faltantes.

    Args:
        df: DataFrame para análise

    Returns:
        DataFrame com colunas: missing_count, missing_pct
    """
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100

    return pd.DataFrame({
        'column': df.columns,
        'missing_count': missing.values,
        'missing_pct': missing_pct.values
    }).sort_values('missing_pct', ascending=False)


def detect_outliers_iqr(data: pd.DataFrame, column: str, k: float = 1.5) -> pd.DataFrame:
    """
    Detecta outliers usando método IQR (Interquartile Range).

    Args:
        data: DataFrame
        column: Nome da coluna para detectar outliers
        k: Multiplicador IQR (padrão 1.5)

    Returns:
        Subset de data contendo apenas outliers
    """
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - k * IQR
    upper = Q3 + k * IQR

    return data[(data[column] < lower) | (data[column] > upper)]


def find_temporal_leakage(df: pd.DataFrame, common_leakage_cols: Optional[List[str]] = None) -> Dict[str, str]:
    """
    Identifica colunas com possível vazamento temporal.

    Args:
        df: DataFrame
        common_leakage_cols: Lista de colunas suspeitas (padrão: duration)

    Returns:
        Dicionário com colunas e recomendação (remove ou mantém)
    """
    if common_leakage_cols is None:
        common_leakage_cols = ['duration']

    leakage_found = {}
    for col in common_leakage_cols:
        if col in df.columns:
            if col == 'duration':
                leakage_found[col] = 'REMOVER (tempo da chamada - conhecida após decisão)'

    return leakage_found


def treat_missing_values(
    df: pd.DataFrame,
    strategy: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Trata valores faltantes conforme estratégia.

    Args:
        df: DataFrame
        strategy: Dicionário {coluna: estratégia}
                 Estratégias: 'mean', 'median', 'mode', 'drop', ou valor específico

    Returns:
        DataFrame com valores faltantes tratados
    """
    df_treated = df.copy()

    # Estratégia padrão: mediana para numéricas, moda para categóricas
    if strategy is None:
        strategy = {}
        for col in df_treated.columns:
            if df_treated[col].isnull().sum() == 0:
                continue

            if df_treated[col].dtype in ['int64', 'float64']:
                strategy[col] = 'median'
            else:
                strategy[col] = 'mode'

    # Aplicar estratégias
    for col, strat in strategy.items():
        if col not in df_treated.columns:
            continue

        if strat == 'drop':
            df_treated = df_treated.dropna(subset=[col])
        elif strat == 'mean':
            df_treated[col].fillna(df_treated[col].mean(), inplace=True)
        elif strat == 'median':
            df_treated[col].fillna(df_treated[col].median(), inplace=True)
        elif strat == 'mode':
            mode_val = df_treated[col].mode()
            if len(mode_val) > 0:
                df_treated[col].fillna(mode_val[0], inplace=True)
        else:
            # Usar valor específico
            df_treated[col].fillna(strat, inplace=True)

    return df_treated


def encode_categorical(
    df: pd.DataFrame,
    target_col: Optional[str] = None,
    method: str = 'label'
) -> Tuple[pd.DataFrame, Dict]:
    """
    Codifica variáveis categóricas.

    Args:
        df: DataFrame
        target_col: Coluna target (não será codificada como categória normal)
        method: 'label' (0,1,2...) ou 'onehot' (dummy variables)

    Returns:
        Tuple: (df_encoded, encoders_dict)
    """
    df_encoded = df.copy()
    encoders = {}

    # Converter target (yes/no) para binário (1/0)
    if target_col and target_col in df_encoded.columns:
        if df_encoded[target_col].dtype == 'object':
            # Assumir yes/no ou similar
            unique_vals = df_encoded[target_col].unique()
            if 'yes' in unique_vals or 'no' in unique_vals:
                df_encoded[target_col] = (df_encoded[target_col] == 'yes').astype(int)
            else:
                # Label encode normalmente
                le = LabelEncoder()
                df_encoded[target_col] = le.fit_transform(df_encoded[target_col])
                encoders[target_col] = le

    # Encontrar colunas categóricas (excluindo target)
    categorical_cols = [
        col for col in df_encoded.select_dtypes(include=['object']).columns
        if col != target_col
    ]

    if method == 'label':
        for col in categorical_cols:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
            encoders[col] = le

    return df_encoded, encoders


def normalize_features(
    X_train: pd.DataFrame,
    X_test: Optional[pd.DataFrame] = None,
    scaler: Optional[StandardScaler] = None
) -> Tuple[np.ndarray, Optional[np.ndarray], StandardScaler]:
    """
    Normaliza features usando StandardScaler.

    Args:
        X_train: Features de treino
        X_test: Features de teste (opcional)
        scaler: StandardScaler pré-treinado (opcional, cria novo se None)

    Returns:
        Tuple: (X_train_scaled, X_test_scaled ou None, scaler)
    """
    if scaler is None:
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
    else:
        X_train_scaled = scaler.transform(X_train)

    if X_test is not None:
        X_test_scaled = scaler.transform(X_test)
    else:
        X_test_scaled = None

    return X_train_scaled, X_test_scaled, scaler


def save_processed_data(
    df: pd.DataFrame,
    X: pd.DataFrame,
    y: pd.Series,
    scaler: StandardScaler,
    encoders: Dict,
    output_dir: str = 'data/processed/'
) -> None:
    """
    Salva dados processados, scaler e encoders.

    Args:
        df: DataFrame completo processado
        X: Features
        y: Target
        scaler: StandardScaler treinado
        encoders: Dicionário de encoders
        output_dir: Diretório de saída
    """
    # Garantir que diretório existe
    import os
    os.makedirs(output_dir, exist_ok=True)

    # Salvar dados
    df.to_csv(f'{output_dir}data_processed.csv', index=False)
    df.to_parquet(f'{output_dir}data_processed.parquet', index=False)
    X.to_csv(f'{output_dir}X_features.csv', index=False)
    y.to_csv(f'{output_dir}y_target.csv', index=False, header=['y'])

    # Salvar modelos
    joblib.dump(scaler, f'models/scaler.pkl')
    joblib.dump(encoders, f'models/label_encoders.pkl')

    print(f"✅ Dados salvos em {output_dir}")
    print(f"✅ Scaler e encoders salvos em models/")


def prepare_data_pipeline(
    df: pd.DataFrame,
    target_col: str = 'y',
    cols_to_drop: Optional[List[str]] = None,
    strategy_missing: Optional[Dict[str, str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, StandardScaler, Dict]:
    """
    Pipeline completo de preparação de dados.

    Realiza na sequência:
    1. Remover colunas com vazamento temporal
    2. Tratar valores faltantes
    3. Codificar variáveis categóricas
    4. Separar features e target
    5. Normalizar features

    Args:
        df: DataFrame bruto
        target_col: Nome da coluna target
        cols_to_drop: Colunas a remover (vazamento temporal)
        strategy_missing: Estratégia de valores faltantes

    Returns:
        Tuple: (df_processed, X_scaled, y, scaler, encoders)
    """
    # 1. Remover colunas
    df_processed = df.copy()
    if cols_to_drop:
        cols_to_drop = [c for c in cols_to_drop if c in df_processed.columns]
        df_processed = df_processed.drop(columns=cols_to_drop)
        print(f"✅ Removidas colunas: {cols_to_drop}")

    # 2. Tratar missings
    df_processed = treat_missing_values(df_processed, strategy_missing)
    print(f"✅ Valores faltantes tratados")

    # 3. Codificar categóricas
    df_processed, encoders = encode_categorical(df_processed, target_col)
    print(f"✅ Variáveis categóricas codificadas")

    # 4. Separar X e y
    X = df_processed.drop(target_col, axis=1)
    y = df_processed[target_col]

    # 5. Normalizar
    X_scaled, _, scaler = normalize_features(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    print(f"✅ Features normalizadas")

    return df_processed, X_scaled, y, scaler, encoders


if __name__ == '__main__':
    # Exemplo de uso
    print("Módulo de processamento de dados importado com sucesso!")
