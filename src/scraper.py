from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import os

# Create data folder if it doesn't exist
os.makedirs('data', exist_ok=True)

def main():
    print("Starting job search...\n")
    
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin"],   # You can add "glassdoor", "zip_recruiter", etc.
        search_term="VoIP Engineer",     # ← Change this to what you want
        location="St Louis, MO",       # ← Change this to your location
        results_wanted=20,
        hours_old=48,                       # Only recent jobs (last 2 days)
        country_indeed='USA'
    )
    
    if jobs.empty:
        print("No jobs found.")
        return
    
    # Basic cleaning
    df = pd.DataFrame(jobs)
    
    # Select useful columns
    columns_to_keep = ['title', 'company', 'location', 'job_url', 'description', 
                      'date_posted', 'salary_min', 'salary_max']
    df = df[columns_to_keep]
    
    # Save to CSV with today's date
    filename = f"data/jobs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(filename, index=False)
    
    print(f"✅ Successfully found {len(df)} jobs!")
    print(f"📁 Saved to: {filename}")
    print("\nFirst 5 jobs:")
    print(df[['title', 'company', 'location']].head())

if __name__ == "__main__":
    main()
