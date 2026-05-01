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
    "Network Automation",
    "Python Network",
    "SIP Engineer"
]

LOCATION = "Saint Charles, MO"
RESULTS_WANTED = 20
HOURS_OLD = 72
# ===================================================

def main():
    print("🚀 Starting Targeted Job Harvester for Network/VoIP Roles...\n")
    
    jobs_list = []
    
    for term in SEARCH_TERMS:
        print(f"Searching for: {term} ...")
        
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=term,
            location=LOCATION,
            results_wanted=RESULTS_WANTED,
            hours_old=HOURS_OLD,
            country_indeed='USA'
        )
        
        if jobs is not None and len(jobs) > 0:
            jobs_list.append(jobs)
            print(f"   → Found {len(jobs)} jobs")
        else:
            print(f"   → No jobs found for '{term}'")
    
    if not jobs_list:
        print("No jobs found.")
        return
    
    # Combine results safely
    df = pd.concat(jobs_list, ignore_index=True)
    df = df.drop_duplicates(subset=['job_url'], keep='first')
    
    # Select available columns
    columns = ['title', 'company', 'location', 'job_url', 'description', 
               'date_posted', 'job_type', 'is_remote']
    
    salary_cols = ['min_amount', 'max_amount', 'interval']
    for col in salary_cols:
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
    display_cols = ['title', 'company', 'location']
    if 'salary_min' in df.columns:
        display_cols.append('salary_min')
    print(df[display_cols].head(10).to_string(index=False))

if __name__ == "__main__":
    main()
