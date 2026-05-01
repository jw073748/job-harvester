from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import os

# Configuration
os.makedirs('data', exist_ok=True)

def main():
    print("🚀 Starting Job Harvester...\n")
    
    # Customize these as needed
    search_terms = [
        "VoIP Support",
        "VoIP Engineer",
        "Telecommunications Engineer",
        "Network Engineer",
        "Telecom Support"
    ]
    
    jobs_list = []
    
    for term in search_terms:
        print(f"Searching for: {term} ...")
        
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=term,
            location="Saint Charles, MO",
            results_wanted=15,
            hours_old=72,                    # Last 3 days
            country_indeed='USA',
            is_remote=False                  # Set True if you want remote only
        )
        
        if jobs is not None and len(jobs) > 0:
            jobs_list.append(jobs)
            print(f"   → Found {len(jobs)} jobs for '{term}'")
    
    if not jobs_list:
        print("No jobs found across all searches.")
        return
    
    # Combine all results
    df = pd.concat(jobs_list, ignore_index=True)
    
    # Remove duplicate jobs based on job_url
    df = df.drop_duplicates(subset=['job_url'], keep='first')
    
    # Select and rename useful columns
    columns = ['title', 'company', 'location', 'job_url', 'description', 
               'date_posted', 'job_type', 'is_remote']
    
    salary_cols = ['min_amount', 'max_amount', 'interval']
    for col in salary_cols:
        if col in df.columns:
            columns.append(col)
    
    df = df[[col for col in columns if col in df.columns]]
    
    df = df.rename(columns={
        'min_amount': 'salary_min',
        'max_amount': 'salary_max'
    })
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    filename = f"data/jobs_{timestamp}.csv"
    df.to_csv(filename, index=False)
    
    print("\n" + "="*60)
    print(f"✅ SUCCESS: Found {len(df)} unique jobs!")
    print(f"📁 Saved to: {filename}")
    print("="*60)
    
    # Show summary
    print("\nTop 8 Jobs:")
    display_cols = ['title', 'company', 'location']
    if 'salary_min' in df.columns:
        display_cols += ['salary_min']
    print(df[display_cols].head(8).to_string(index=False))

if __name__ == "__main__":
    main()
