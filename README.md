# Wellahealth Claims Audit & Leakage Detection Pipeline

### Project Overview
As a Data Analytics Consultant, I designed a simulated end-to-end data pipeline modeled after Wellahealth's micro-insurance operational architecture in Nigeria. The goal was to build automated logic capable of auditing large-scale pharmacy insurance claims to plug financial leakage, identify partner fraud, and protect underwriting margins.

###  Methodology & Dataset
I generated a synthetic dataset simulating **10,000 historical pharmacy claims** across 200 network pharmacies in Nigeria, embedding real-world operational anomalies (system errors, price gouging, and medication upselling). 

###  Key Audit Findings
Running the detection engine across the 10,000 active records successfully isolated **1,185 critical anomalies**:
*   **148 System Duplicates:** Caught double-billing submissions (same patient, pharmacy, and amount submitted under a 5-minute window).
*   **553 Severe Price Gouging Incidents:** Isolated pharmacies charging **>3x the network median baseline** for standard medications. (e.g., *PHARM_0073* was flagged as the highest risk offender with 9 severe overpricing events).
*   **484 Medication Mismatches:** Detected high-risk claim anomalies where basic Malaria diagnoses were paired with expensive Peptic Ulcer treatments (Omeprazole) to exploit payouts.

### Tech Stack
*   **Python / Pandas:** Data modeling, chronological window functions, and baseline grouping.
*   **Data Architecture:** Automated median network baseline indexing (dynamic thresholding vs. static hardcoding).
