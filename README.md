# Debt Portfolio Efficiency Analysis

## Background
This project analyzes two portfolios of defaulted personal installment loans, containing customer-level records of loans that have entered a default state due to missed or prolonged non-payment.
Each portfolio represents a distinct collection of defaulted loans managed independently, with associated repayment activity, outstanding balances, and customer attributes.
The objective of the analysis is to evaluate and compare the efficiency and risk characteristics of the two portfolios based on their observed repayment behavior and debt dynamics.

## Analysis Approach
The analysis begins with an exploration of demographic and geographic characteristics to identify structural differences between the portfolios.
This is followed by a comparison of core quantitative repayment and balance-related metrics across the two portfolios.
These insights are then consolidated into a set of portfolio-level financial indicators, enabling a structured and consistent comparison of performance.

## Results Summary
The results indicate that portfolio number 2 demonstrates superior collection efficiency and more favorable outstanding balance characteristics across multiple comparison dimensions, suggesting a more attractive efficiency–risk profile relative to the alternative portfolio.

## Project Structure
The Jupyter notebook presents the complete analytical workflow, including the full reasoning process, visualizations, and insights derived at each stage of the portfolio comparison.
The Python script contains the cleaned, reusable data processing and KPI computation logic used throughout the analysis.

## Dataset Overview
The dataset contains customer-level loan records for defaulted loans only. All identifiers (e.g., country, city) are anonymized and mapped to generic IDs with no real-world linkage.

Key quantitative fields include:
- **Original Sum** – Original loan amount issued to the customer  
- **Due Date** – Date on which the loan entered default  
- **Current Debt** – Outstanding balance including principal, accrued interest, and fees  
- **Principal** – Remaining principal balance  
- **Interest** – Accrued interest amount  
- **Fee 1–4** – Additional fees associated with the loan  
- **APR** – Annual percentage rate of the loan  
- **Total Paid** – Cumulative payments made by the customer to date
