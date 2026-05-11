from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
import os
import warnings
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

warnings.simplefilter(action='ignore', category=FutureWarning)
os.makedirs('data', exist_ok=True)

console = Console()

# ================== CONFIGURATION ==================
CLEARANCE_KEYWORDS = ["clearance", "ts/sci", "secret clearance", "top secret", 
                     "security clearance", "dod clearance", "polygraph"]
# ===================================================

def contains_clearance(text):
    if not text:
        return False
    text_lower = str(text).lower()
    return any(keyword in text_lower for keyword in CLEARANCE_KEYWORDS)

def main():
    console.print(Panel.fit("[bold cyan]🚀 Job Harvester - Interactive Mode[/bold cyan]", 
                           subtitle="Network / VoIP / Telecom Focus", box=box.ROUNDED))
    
    # User Inputs
    search_term = console.input("[bold]Enter job title / search term[/bold] (e.g. Network Engineer): ").strip()
    if not search_term:
        search_term = "Network Engineer"
    
    location = console.input("[bold]Enter location[/bold] (e.g. Saint Louis, MO or press Enter for nationwide): ").strip()
    
    try:
        min_salary = int(console.input("[bold]Minimum salary[/bold] (e.g. 80000, Enter to skip): ") or 0)
    except:
        min_salary = 0
    
    try:
        max_salary = int(console.input("[bold]Maximum salary[/bold] (e.g. 160000, Enter to skip): ") or 999999)
    except:
        max_salary = 999999

    console.print(f"\n[bold green]Searching for:[/bold green] '{search_term}' | Location: {location or 'Anywhere'} | Salary: ${min_salary:,} - ${max_salary:,}\n")

    try:
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin"],
            search_term=search_term,
            location=location,
            results_wanted=30,
            hours_old=72,
            country_indeed='USA',
        )
        
        if jobs is None or len(jobs) == 0:
            console.print("[bold red]❌ No jobs found.[/bold red]")
            return
            
        df = pd.DataFrame(jobs)
        df = df.drop_duplicates(subset=['job_url'], keep='first')
        
        # Filter clearance jobs
        before = len(df)
        df = df[~df.apply(lambda row: contains_clearance(row.get('title')) or 
                                     contains_clearance(row.get('description')), axis=1)]
        
        if before - len(df) > 0:
            console.print(f"[yellow]Excluded {before - len(df)} security clearance jobs[/yellow]")

        # Salary filter
        if min_salary > 0 or max_salary < 999999:
            if 'min_amount' in df.columns:
                df = df[(df['min_amount'].fillna(0) >= min_salary) & 
                       (df['min_amount'].fillna(999999) <= max_salary)]

        # Column selection
        columns = ['title', 'company', 'location', 'job_url', 'description', 
                   'date_posted', 'job_type', 'is_remote']
        for col in ['min_amount', 'max_amount', 'interval']:
            if col in df.columns:
                columns.append(col)
        
        df = df[[col for col in columns if col in df.columns]]
        df = df.rename(columns={'min_amount': 'salary_min', 'max_amount': 'salary_max'})

        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"data/jobs_{timestamp}.csv"
        df.to_csv(filename, index=False)

        # === Fancy Display ===
        console.print(f"\n[bold green]✅ SUCCESS: Found {len(df)} matching jobs![/bold green]")
        console.print(f"[dim]Saved to: {filename}[/dim]\n")

        # Rich Table
        table = Table(title="Top Matching Jobs", box=box.HEAVY_HEAD, show_lines=True)
        table.add_column("Title", style="bold cyan", width=45)
        table.add_column("Company", style="magenta", width=25)
        table.add_column("Location", style="yellow", width=25)
        table.add_column("Remote?", style="green")
        table.add_column("Salary", style="green", justify="right")

        for _, row in df.head(12).iterrows():
            remote = "🌐 Yes" if row.get('is_remote') else "📍 No"
            salary = f"${int(row.get('salary_min', 0)):,}" if pd.notna(row.get('salary_min')) else "-"
            table.add_row(
                row.get('title', ''),
                row.get('company', ''),
                row.get('location', ''),
                remote,
                salary
            )

        console.print(table)

        if len(df) > 12:
            console.print(f"[dim]... and {len(df)-12} more jobs in the CSV file[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    main()
