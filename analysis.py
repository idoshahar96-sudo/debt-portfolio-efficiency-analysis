## Debt Portfolio Analysis - Case Study

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

### Data Processing
df = pd.read_csv(BASE_DIR / "data" / "book_data.csv")
#changing dates columns from string type to date type
#uniting all fees columns to one fee column
#adding customer_age column
df['Date_of_birth'] = pd.to_datetime(df['Date_of_birth'], dayfirst=True, errors='coerce')
df['duedate'] = pd.to_datetime(df['duedate'], dayfirst=True, errors='coerce')
fee_cols = ['fee 1', 'fee 2', 'fee 3', 'fee 4']
df['total_fees'] = df[fee_cols].sum(axis=1) # in the columns directory, there wasn't any mention of differences between the 4 fees, so I'm assuming there isn't any
today = pd.Timestamp.today()
df['Customer_age'] = (today - df['Date_of_birth']).dt.days // 365

### Demographics EDA
#indicators of borrower reliability
profile_stats = df.groupby('Portfolio #').agg(
    Mean_Age=('Customer_age', 'mean'),
    Median_Age=('Customer_age', 'median'),
    Male_Ratio=('Gender', lambda x: (x=='Male').mean()*100)
).round(2)


# top 5 cities and counties per portfolio
top_cities = (
    df.groupby(['Portfolio #', 'city'])
      .size()
      .reset_index(name='Count')
      .sort_values(['Portfolio #', 'Count'], ascending=[True, False])
)

top_cities['Percent_in_Portfolio'] = (
    top_cities['Count'] / top_cities.groupby('Portfolio #')['Count'].transform('sum') * 100
).round(2)

top_counties = (
    df.groupby(['Portfolio #', 'county'])
      .size()
      .reset_index(name='Count')
      .sort_values(['Portfolio #', 'Count'], ascending=[True, False])
)

top_counties['Percent_in_Portfolio'] = (
    top_counties['Count'] / top_counties.groupby('Portfolio #')['Count'].transform('sum') * 100
).round(2)


### Debts Structure Analysis

default_trend = (
    df
    .groupby([pd.Grouper(key='duedate', freq='MS'), 'Portfolio #'])['ID']
    .nunique()
    .reset_index(name='count')
)


# mean stats
mean_stats = (
    df.groupby('Portfolio #')[['original_sum', 'principal', 'interest']]
      .mean()
      .round(2)
)
mean_stats.columns = ['Average_Sum_Borrowed', 'Average_Principal', 'Average_Interest']

# median stats
median_stats = (
    df.groupby('Portfolio #')[['original_sum','principal', 'interest']]
      .median()
      .round(2)
)
median_stats.columns = ['Median_Sum_Borrowed','Median_Principal', 'Median_Interest']
combined_stats = pd.concat([mean_stats, median_stats], axis=1)

# calculate difference row
diff_percent = ((combined_stats / combined_stats.iloc[0]) - 1) * 100
diff_percent = diff_percent.round(2).astype(str) + '%'

# add difference row
combined_stats.loc['% Difference (vs 1st)'] = diff_percent.iloc[-1]


debt_stats = df.groupby('Portfolio #')[['current balance','total_paid']].agg(['mean','median']).round(2)
# computing differences
diff_percent = ((debt_stats.loc[1] - debt_stats.loc[2]) / debt_stats.loc[2] * 100).round(2)
#replacing 'N/A' for non-division calculations
diff_percent = diff_percent.replace([np.inf, -np.inf, np.nan], 'N/A') 
#adding % only to numeric values
diff_percent = diff_percent.apply(
    lambda x: [f"{v}%" if isinstance(v, (int, float, np.integer, np.floating)) else v for v in x]
    if isinstance(x, (pd.Series, list)) else
    (f"{x}%" if isinstance(x, (int, float, np.integer, np.floating)) else x)
)
debt_stats.loc['% Difference (vs 2nd)'] = diff_percent

fees_stats = (
    df.groupby('Portfolio #')[['total_fees']]
      .agg(['mean', 'median'])
      .round(2)
)

# Compute % difference of portfolio 1 vs 2
diff_percent = ((fees_stats.loc[1] - fees_stats.loc[2]) / fees_stats.loc[2] * 100).round(2)
diff_percent = diff_percent.astype(str) + '%'
fees_stats.loc['% Difference (vs 2nd)'] = diff_percent

# ## Financial KPIs Analysis

# computing main financial KPI's
# aggregate required columns
agg = df.groupby('Portfolio #').agg({
    'original_sum': 'sum',
    'total_paid': 'sum',
    'current balance': 'sum',
    'ID': 'nunique'  # count unique debtors to use later
}).reset_index()

# rename columns
agg.columns = ['Portfolio #', 'Original Sum', 'Total Paid', 'Current Balance', 'Unique Debtors']

# calculate KPIs
agg['Recovery Rate (%)'] = (agg['Total Paid'] / agg['Original Sum']) * 100                    # Recovery Rate
agg['CER (%)'] = (agg['Total Paid'] / (agg['Total Paid'] + agg['Current Balance'])) * 100     # Collection Efficiency Ratio
agg['DOR (%)'] = (agg['Current Balance'] / agg['Original Sum']) * 100                         # Debt-to-Original Ratio    
agg['Avg Payment per Debtor'] = agg['Total Paid'] / agg['Unique Debtors']                     # Average Payment per Debtor
kpi = agg[['Portfolio #', 'Recovery Rate (%)', 'CER (%)', 'DOR (%)', 'Avg Payment per Debtor']].round(2)

if __name__ == "__main__":
    pass
