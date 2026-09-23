import pandas as pd
import numpy as np

# 1. Load the dataset from your Documents folder
file_path = 'C:/Users/user/Documents/wellahealth_mock_claims.csv'
df = pd.read_csv(file_path)

print(f"📊 Loaded {len(df)} pharmacy claims for analysis.\n")

# ==============================================================================
# 🎯 DETECTION 1: SYSTEM DUPLICATES (Double-Billing)
# Rule: Flag claims from the same pharmacy, for the same diagnosis/amount, 
# submitted within minutes of each other.
# ==============================================================================
df['Claim_Timestamp'] = pd.to_datetime(df['Claim_Timestamp'])

# Sort by pharmacy and time to check consecutive records
df = df.sort_values(by=['Pharmacy_ID', 'Claim_Timestamp'])

# Check if current claim matches the previous claim's Pharmacy, Diagnosis, and Amount
duplicate_mask = (
    (df['Pharmacy_ID'] == df['Pharmacy_ID'].shift(1)) &
    (df['Diagnosis'] == df['Diagnosis'].shift(1)) &
    (df['Claim_Amount_NGN'] == df['Claim_Amount_NGN'].shift(1)) &
    ((df['Claim_Timestamp'] - df['Claim_Timestamp'].shift(1)).dt.total_seconds() < 300) # under 5 mins
)

duplicates_df = df[duplicate_mask]


# ==============================================================================
# 🎯 DETECTION 2: SEVERE OVERPRICING (Price Gouging)
# Rule: Calculate the median cost for each drug across the entire network. 
# Flag any claim that is more than 3 times the baseline average market price.
# ==============================================================================
# Calculate baseline market price for each medication
baseline_prices = df.groupby('Medication_Dispensed')['Claim_Amount_NGN'].transform('median')

# Flag claims 3x higher than network baseline
overpriced_mask = df['Claim_Amount_NGN'] > (baseline_prices * 3)
overpriced_df = df[overpriced_mask]


# ==============================================================================
# 🎯 DETECTION 3: MEDICATION MISMATCH (Suspicious Upselling)
# Rule: Wellahealth basic plans cover specific drugs for specific illnesses.
# Flag cases where a cheap diagnosis (Malaria) is used to bill for expensive drugs.
# ==============================================================================
mismatch_mask = (df['Diagnosis'] == 'Malaria') & (df['Medication_Dispensed'] == 'Omeprazole + Antacids')
mismatch_df = df[mismatch_mask]


# ==============================================================================
# 📈 CONSULTANT REPORT SUMMARY
# ==============================================================================
print("==================================================")
print("       WELLAHEALTH ANOMALY DETECTION REPORT       ")
print("==================================================")
print(f"🚨 [FLAGGED] Potential Duplicate Claims: {len(duplicates_df)}")
print(f"💰 [FLAGGED] Severe Price Gouging Incidents: {len(overpriced_df)}")
print(f"💊 [FLAGGED] Medication Mismatches (Fraud Risk): {len(mismatch_df)}")
print("--------------------------------------------------")

# Let's see which pharmacies are the top offenders for overpricing
if len(overpriced_df) > 0:
    print("\n🏪 Top 5 Pharmacies with Highest Overpricing Incidents:")
    print(overpriced_df['Pharmacy_ID'].value_counts().head(5))

# Save flagged anomalies to a file for management review
anomalies_combined = pd.concat([duplicates_df, overpriced_df, mismatch_df]).drop_duplicates()
anomalies_combined.to_csv('C:/Users/user/Documents/wellahealth_flagged_anomalies.csv', index=False)
print("\n✅ Saved compiled audit report to 'wellahealth_flagged_anomalies.csv'")
