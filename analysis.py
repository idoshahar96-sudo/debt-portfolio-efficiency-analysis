import pandas as pd
import numpy as np
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "book_data.csv"


def load_data(path):
    return pd.read_csv(path)


def preprocess_data(df):
    df = df.copy()

    df['Date_of_birth'] = pd.to_datetime(df['Date_of_birth'], dayfirst=True, errors='coerce')
    df['duedate'] = pd.to_datetime(df['duedate'], dayfirst=True, errors='coerce')

    fee_cols = ['fee 1', 'fee 2', 'fee 3', 'fee 4']
    df['total_fees'] = df[fee_cols].sum(axis=1)

    today = pd.Timestamp.today()
    df['Customer_age'] = (today - df['Date_of_birth']).dt.days // 365

    return df


def demographics_and_geography(df):
    demographics = (
        df.groupby('Portfolio #')
          .agg(
              Mean_Age=('Customer_age', 'mean'),
              Median_Age=('Customer_age', 'median'),
              Male_Ratio=('Gender', lambda x: (x == 'Male').mean() * 100)
          )
          .round(2)
    )

    cities = (
        df.groupby(['Portfolio #', 'city'])
          .size()
          .reset_index(name='Count')
          .sort_values(['Portfolio #', 'Count'], ascending=[True, False])
    )
    cities['Percent_in_Portfolio'] = (
        cities['Count']
        / cities.groupby('Portfolio #')['Count'].transform('sum')
        * 100
    ).round(2)

    counties = (
        df.groupby(['Portfolio #', 'county'])
          .size()
          .reset_index(name='Count')
          .sort_values(['Portfolio #', 'Count'], ascending=[True, False])
    )
    counties['Percent_in_Portfolio'] = (
        counties['Count']
        / counties.groupby('Portfolio #')['Count'].transform('sum')
        * 100
    ).round(2)

    return {
        "demographics": demographics,
        "top_cities": cities,
        "top_counties": counties
    }


def debt_size_stats(df):
    mean_stats = (
        df.groupby('Portfolio #')[['original_sum', 'principal', 'interest']]
          .mean()
          .round(2)
    )
    mean_stats.columns = [
        'Average_Sum_Borrowed',
        'Average_Principal',
        'Average_Interest'
    ]

    median_stats = (
        df.groupby('Portfolio #')[['original_sum', 'principal', 'interest']]
          .median()
          .round(2)
    )
    median_stats.columns = [
        'Median_Sum_Borrowed',
        'Median_Principal',
        'Median_Interest'
    ]

    combined = pd.concat([mean_stats, median_stats], axis=1)

    diff = ((combined / combined.iloc[0]) - 1) * 100
    combined.loc['% Difference (vs 1st)'] = diff.iloc[1].round(2).astype(str) + '%'

    return combined


def debt_balance_stats(df):
    stats = (
        df.groupby('Portfolio #')[['current balance', 'total_paid']]
          .agg(['mean', 'median'])
          .round(2)
    )

    diff = (stats.loc[1] - stats.loc[2]) / stats.loc[2] * 100
    diff = diff.round(2)

    # convert to string with %
    diff = diff.astype(str) + '%'

    # handle invalid divisions AFTER formatting
    diff = diff.replace(['inf%', '-inf%', 'nan%'], 'N/A')

    stats.loc['% Difference (vs 2nd)'] = diff

    return stats


def fee_stats(df):
    stats = (
        df.groupby('Portfolio #')[['total_fees']]
          .agg(['mean', 'median'])
          .round(2)
    )

    diff = ((stats.loc[1] - stats.loc[2]) / stats.loc[2] * 100).round(2)
    stats.loc['% Difference (vs 2nd)'] = diff.astype(str) + '%'

    return stats


def financial_kpis(df):
    agg = (
        df.groupby('Portfolio #')
          .agg(
              Original_Sum=('original_sum', 'sum'),
              Total_Paid=('total_paid', 'sum'),
              Current_Balance=('current balance', 'sum'),
              Unique_Debtors=('ID', 'nunique')
          )
          .reset_index()
    )

    agg['Recovery Rate (%)'] = agg['Total_Paid'] / agg['Original_Sum'] * 100
    agg['CER (%)'] = agg['Total_Paid'] / (agg['Total_Paid'] + agg['Current_Balance']) * 100
    agg['DOR (%)'] = agg['Current_Balance'] / agg['Original_Sum'] * 100
    agg['Avg Payment per Debtor'] = agg['Total_Paid'] / agg['Unique_Debtors']

    return agg[
        ['Portfolio #', 'Recovery Rate (%)', 'CER (%)', 'DOR (%)', 'Avg Payment per Debtor']
    ].round(2)


def main():
    df = load_data(DATA_PATH)
    df = preprocess_data(df)

    demo_geo = demographics_and_geography(df)

    demographics = demo_geo["demographics"]
    cities = demo_geo["top_cities"]
    counties = demo_geo["top_counties"]

    debt_sizes = debt_size_stats(df)
    balances = debt_balance_stats(df)
    fees = fee_stats(df)

    kpis = financial_kpis(df)
    print("\nStatistics of the Current Balance and Total Paid:\n")
    print(balances)
    print("\nFinancial KPIs:\n")
    print(kpis)


if __name__ == "__main__":
    main()