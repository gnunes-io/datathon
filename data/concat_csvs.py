import pandas as pd
import numpy as np
import re
import os

DATA = r'C:\Users\gabri\Datathon - FIAP_Chall\data'
OUT  = os.path.join(DATA, 'alunos_supabase.csv')


def to_float(series):
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors='coerce')
    return pd.to_numeric(
        series.astype(str).str.replace(',', '.', regex=False).str.strip(),
        errors='coerce'
    )


def parse_fase(val):
    if pd.isna(val):
        return None
    s = str(val).strip().upper()
    if 'ALFA' in s:
        return 0
    # '7E', '4M', 'FASE 3', '3' → extrai o número inicial
    s = re.sub(r'FASE\s*', '', s)
    m = re.match(r'(\d+)', s)
    return int(m.group(1)) if m else None


# ── 2022 ──────────────────────────────────────────────────────────────────
d22 = pd.read_csv(os.path.join(DATA, 'DATATHON - 2022.csv'), encoding='utf-8-sig')

df22 = pd.DataFrame({
    'ra':        d22['RA'],
    'nome':      d22['Nome'],
    'fase':      d22['Fase'].apply(parse_fase),
    'ano':       2022,
    'inde':      to_float(d22['INDE 22']),
    'pedra':     d22['Pedra 22'],
    'ian':       to_float(d22['IAN']),
    'ida':       to_float(d22['IDA']),
    'ieg':       to_float(d22['IEG']),
    'iaa':       to_float(d22['IAA']),
    'ips':       to_float(d22['IPS']),
    'ipp':       np.nan,           # ausente em 2022
    'ipv':       to_float(d22['IPV']),
    'defasagem': to_float(d22['Defas']),
})

# ── 2023 ──────────────────────────────────────────────────────────────────
d23 = pd.read_csv(os.path.join(DATA, 'DATATHON - 2023.csv'), encoding='utf-8-sig')

df23 = pd.DataFrame({
    'ra':        d23['RA'],
    'nome':      d23['Nome Anonimizado'],
    'fase':      d23['Fase'].apply(parse_fase),
    'ano':       2023,
    'inde':      to_float(d23['INDE 2023']),
    'pedra':     d23['Pedra 2023'],
    'ian':       to_float(d23['IAN']),
    'ida':       to_float(d23['IDA']),
    'ieg':       to_float(d23['IEG']),
    'iaa':       to_float(d23['IAA']),
    'ips':       to_float(d23['IPS']),
    'ipp':       to_float(d23['IPP']),
    'ipv':       to_float(d23['IPV']),
    'defasagem': to_float(d23['Defasagem']),
})

# ── 2024 ──────────────────────────────────────────────────────────────────
d24 = pd.read_csv(os.path.join(DATA, 'DATATHON - 2024.csv'), encoding='utf-8-sig')

df24 = pd.DataFrame({
    'ra':        d24['RA'],
    'nome':      d24['Nome Anonimizado'],
    'fase':      d24['Fase'].apply(parse_fase),
    'ano':       2024,
    'inde':      to_float(d24['INDE 2024']),
    'pedra':     d24['Pedra 2024'],
    'ian':       to_float(d24['IAN']),
    'ida':       to_float(d24['IDA']),
    'ieg':       to_float(d24['IEG']),
    'iaa':       to_float(d24['IAA']),
    'ips':       to_float(d24['IPS']),
    'ipp':       to_float(d24['IPP']),
    'ipv':       to_float(d24['IPV']),
    'defasagem': to_float(d24['Defasagem']),
})

# ── Concat ─────────────────────────────────────────────────────────────────
df = pd.concat([df22, df23, df24], ignore_index=True)

# Remove linhas sem RA
df = df[df['ra'].notna() & (df['ra'].astype(str).str.strip() != '')]

# Arredonda indicadores para 4 casas
num_cols = ['inde', 'ian', 'ida', 'ieg', 'iaa', 'ips', 'ipp', 'ipv', 'defasagem']
df[num_cols] = df[num_cols].round(4)

# ── Adiciona id sequencial ─────────────────────────────────────────────────
df.insert(0, 'id', range(1, len(df) + 1))

# ── Export (antes do relatório para garantir o arquivo) ───────────────────
df.to_csv(OUT, index=False, encoding='utf-8-sig')

# ── Relatório ──────────────────────────────────────────────────────────────
print(f"\nArquivo gerado : {OUT}")
print(f"Total de linhas: {len(df)}")
print(f"Por ano        : {df.groupby('ano').size().to_dict()}")
print(f"\nNulos por coluna:")
print(df.isnull().sum().to_string())
