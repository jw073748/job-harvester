from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
os.makedirs('data', exist_ok=True)

# ================== CONFIGURATION ==================
SEARCH_TERMS = [
    "Network Engineer",
    "VoIP Engineer",
    "Voice Engineer",
    "Network Operations",
    "Service Assurance",
    "NOC Engineer",
    "Telecom Engineer",
    "SIP Engineer"
]

LOCATION = "Saint Louis, MO"
RESULTS_WANTED = 20
HOURS_OLD = 72
# ===================================================

def scrape(term, location, remote_only=False):
    """Scrape jobs for a term/location combo, return DataFrame or None."""
    label = "Remote" if remote_only else location
    print(f"  Searching: '{term}' | {label} ...")
    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=term,
            location=location,
            results_wanted=RESULTS_WANTED,
            hours_old=HOURS_OLD,
            country_indeed='USA',
            is_remote=remote_only,
        )
        if jobs is not None and len(jobs) > 0:
            print(f"    → {len(jobs)} jobs found")
            return jobs
        else:
            print(f"    → 0 jobs found")
            return None
    except Exception as e:
        print(f"    → ERROR: {e}")
        return None


def main():
    print("🚀 Starting Targeted Job Harvester for Network/VoIP Roles...\n")

    jobs_list = []

    for term in SEARCH_TERMS:
        # Local search
        local = scrape(term, LOCATION, remote_only=False)
        if local is not None:
            jobs_list.append(local)

        # Remote search (is_remote=True filters for remote listings)
        remote = scrape(term, LOCATION, remote_only=True)
        if remote is not None:
            jobs_list.append(remote)

    if not jobs_list:
        print("\n❌ No jobs found across all searches.")
        return

    # Combine & deduplicate
    df = pd.concat(jobs_list, ignore_index=True)
    df = df.drop_duplicates(subset=['job_url'], keep='first')

    # Select available columns
    columns = ['title', 'company', 'location', 'job_url', 'description',
               'date_posted', 'job_type', 'is_remote']

    for col in ['min_amount', 'max_amount', 'interval']:
        if col in df.columns:
            columns.append(col)

    df = df[[col for col in columns if col in df.columns]]
    df = df.rename(columns={'min_amount': 'salary_min', 'max_amount': 'salary_max'})

    # Save
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"data/jobs_network_{timestamp}.csv"
    df.to_csv(filename, index=False)

    print("\n" + "="*70)
    print(f"✅ SUCCESS: Found {len(df)} unique jobs!")
    print(f"📁 Saved to: {filename}")
    print("="*70)

    print("\nTop 10 Jobs:")
    display_cols = ['title', 'company', 'location', 'is_remote']
    if 'salary_min' in df.columns:
        display_cols.append('salary_min')
    print(df[display_cols].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
