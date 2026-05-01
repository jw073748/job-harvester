from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import os

# Create data folder if it doesn't exist
os.makedirs('data', exist_ok=True)

def main():
    print("Starting job search...\n")
    
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin"],
        search_term="Python developer",     
        location="Saint Charles, MO",       
        results_wanted=20,
        hours_old=48,
        country_indeed='USA'
    )
    
    if jobs is None or len(jobs) == 0:
        print("No jobs found.")
        return
    
    df = pd.DataFrame(jobs)
    
    # Safer column selection
    available_columns = ['title', 'company', 'location', 'job_url', 
                        'description', 'date_posted', 'job_type', 'is_remote']
    
    # Add salary columns only if they exist
    salary_cols = ['min_amount', 'max_amount', 'interval']
    for col in salary_cols:
        if col in df.columns:
            available_columns.append(col)
    
    # Keep only columns that exist
    df = df[[col for col in available_columns if col in df.columns]]
    
    # Rename salary columns for readability
    df = df.rename(columns={
        'min_amount': 'salary_min',
        'max_amount': 'salary_max'
    })
    
    # Save to CSV with timestamp
    filename = f"data/jobs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    
    print(f"✅ Successfully found {len(df)} jobs!")
    print(f"📁 Saved to: {filename}\n")
    
    print("First 5 jobs:")
    display_cols = ['title', 'company', 'location']
    if 'salary_min' in df.columns:
        display_cols.append('salary_min')
    print(df[display_cols].head().to_string(index=False))

if __name__ == "__main__":
    main()
