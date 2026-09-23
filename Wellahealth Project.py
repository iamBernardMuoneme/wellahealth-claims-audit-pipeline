import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Configuration for data size
NUM_RECORDS = 10000

# 1. Base Data pools
pharmacy_states = ['Lagos', 'Oyo', 'Kano', 'FCT', 'Rivers', 'Anambra', 'Kaduna']
pharmacies = [f"PHARM_{str(i).zfill(4)}" for i in range(1, 201)] # 200 pharmacies
pharmacy_mapping = {ph: random.choice(pharmacy_states) for ph in pharmacies}

diagnoses = ['Malaria', 'Typhoid', 'Acute Cough/Cold', 'Peptic Ulcer']

# Realistic standard costs for Wellahealth network (Standard, Min, Max)
medication_rules = {
    'Malaria': {'med': 'ACT (Artemether-Lumefantrine)', 'base_cost': 1500, 'min': 1200, 'max': 1800},
    'Typhoid': {'med': 'Ciprofloxacin + Paracetamol', 'base_cost': 3500, 'min': 2800, 'max': 4200},
    'Acute Cough/Cold': {'med': 'Expectorant Cough Syrup', 'base_cost': 1200, 'min': 900, 'max': 1600},
    'Peptic Ulcer': {'med': 'Omeprazole + Antacids', 'base_cost': 4500, 'min': 3800, 'max': 5500}
}

# 2. Generate Base Realistic Data
data = []
start_date = datetime(2026, 1, 1)

for i in range(NUM_RECORDS):
    claim_id = f"CLM-{2026}-{str(i+1).zfill(6)}"
    pharmacy_id = random.choice(pharmacies)
    state = pharmacy_mapping[pharmacy_id]
    
    # 85% chance of normal behavior, 15% chance of anomalous behavior
    behavior_roll = random.random()
    
    if behavior_roll > 0.15:
        # ---- NORMAL CLAIM ----
        diagnosis = random.choice(diagnoses)
        medication = medication_rules[diagnosis]['med']
        # Cost fluctuates normally within expected market ranges
        cost = round(random.uniform(medication_rules[diagnosis]['min'], medication_rules[diagnosis]['max']), -1)
        anomaly_flag = 0
        anomaly_type = "Normal"
    else:
        # ---- ANOMALOUS CLAIM (Fraud/Error simulation) ----
        anomaly_flag = 1
        anomaly_choice = random.choice(['Overpricing', 'Wrong Med Mismatch', 'Duplicate Claim'])
        
        if anomaly_choice == 'Overpricing':
            diagnosis = random.choice(diagnoses)
            medication = medication_rules[diagnosis]['med']
            # Price is inflated by 3x to 6x the maximum allowed budget
            cost = round(medication_rules[diagnosis]['max'] * random.uniform(3.0, 6.0), -1)
            anomaly_type = "Severe Overpricing"
            
        elif anomaly_choice == 'Wrong Med Mismatch':
            diagnosis = 'Malaria' # Cheap diagnosis
            medication = 'Omeprazole + Antacids' # Dispensing expensive ulcer drugs instead
            cost = round(medication_rules['Peptic Ulcer']['max'] * random.uniform(1.0, 1.3), -1)
            anomaly_type = "Medication Mismatch"
            
        elif anomaly_choice == 'Duplicate Claim':
            # Simulates billing twice for the exact same thing within a short window
            diagnosis = random.choice(diagnoses)
            medication = medication_rules[diagnosis]['med']
            cost = round(medication_rules[diagnosis]['base_cost'], -1)
            anomaly_type = "System Duplicate"

    # Date generation over the last 9 months
    date_offset = random.randint(0, 260)
    claim_date = start_date + timedelta(days=date_offset, hours=random.randint(8, 20))
    
    data.append([claim_id, claim_date, pharmacy_id, state, diagnosis, medication, cost, anomaly_flag, anomaly_type])

# 3. Create DataFrame
df = pd.DataFrame(data, columns=[
    'Claim_ID', 'Claim_Timestamp', 'Pharmacy_ID', 'State', 
    'Diagnosis', 'Medication_Dispensed', 'Claim_Amount_NGN', 
    'Is_Anomaly_Ground_Truth', 'Anomaly_Type'
])

# Force exact duplicates for the 'Duplicate Claim' logic to make it queryable
duplicate_indices = df[df['Anomaly_Type'] == 'System Duplicate'].index
for idx in duplicate_indices[:150]: # Make 150 exact twins
    if idx + 1 < len(df):
        df.iloc[idx + 1] = df.iloc[idx].copy()
        df.at[idx + 1, 'Claim_ID'] = f"{df.at[idx, 'Claim_ID']}-DUP"
        df.at[idx + 1, 'Claim_Timestamp'] = df.at[idx, 'Claim_Timestamp'] + timedelta(minutes=random.randint(1, 4))

# Save to CSV# New line (forces it into your Documents folder)
df.to_csv('C:/Users/user/Documents/wellahealth_mock_claims.csv', index=False)
print(f"✅ Dataset successfully generated! Saved 10,000 rows to 'wellahealth_mock_claims.csv'")
print(df['Anomaly_Type'].value_counts())