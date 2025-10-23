import pandas as pd

def load_dataset(path: str) -> pd.DataFrame:
    """
    Memuat dan membersihkan dataset gym_exercise_dataset.csv
    - Gunakan kolom 'Main_muscle' sebagai otot utama (nama umum)
    - Gabungkan Preparation + Execution jadi 'instructions'
    """
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower()

    # Hapus kolom tidak diperlukan
    drop_cols = [
        'variation', 'utility', 'mechanics', 'force',
        'stabilizer_muscles', 'antagonist_muscles',
        'dynamic_stabilizer_muscles', 'difficulty (1-5)',
        'secondary muscles', 'parent_id'
    ]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')

    # Rename kolom utama biar konsisten
    rename_map = {
        'exercise name': 'exercise_name',
        'equipment': 'equipment',
        'main_muscle': 'main_muscle',
        'target_muscles': 'target_muscle',
        'synergist_muscles': 'synergist_muscle',
        'preparation': 'preparation',
        'execution': 'execution'
    }
    df = df.rename(columns=rename_map)

    # Gabungkan preparation + execution jadi satu kolom
    if 'preparation' in df.columns and 'execution' in df.columns:
        df['instructions'] = df['preparation'].fillna('') + " " + df['execution'].fillna('')

    # Normalisasi teks (biar konsisten)
    for col in ['exercise_name', 'main_muscle', 'target_muscle', 'synergist_muscle', 'equipment']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.title()

    print(f"✅ Dataset loaded: {len(df)} rows with {len(df.columns)} columns")
    return df


def recommend_exercises(df: pd.DataFrame, muscle_query: str, limit: int = 10) -> pd.DataFrame:
    """
    Mengembalikan rekomendasi latihan berdasarkan 'Main_muscle' (nama umum)
    atau 'Target_Muscles' (nama ilmiah)
    """
    muscle_query = muscle_query.strip().title()

    mask = (
        df['main_muscle'].str.contains(muscle_query, case=False, na=False) |
        df['target_muscle'].str.contains(muscle_query, case=False, na=False) |
        df['synergist_muscle'].str.contains(muscle_query, case=False, na=False)
    )

    result = df[mask].copy()
    keep_cols = ['exercise_name', 'main_muscle', 'target_muscle', 'synergist_muscle', 'equipment', 'instructions']
    result = result[[c for c in keep_cols if c in result.columns]]

    return result.head(limit)
