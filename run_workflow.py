from backend.workflows.spac_workflow import app, State

if __name__ == "__main__":
    print("🚀 Starting SPAC Monitoring Workflow...")
    
    # Initialize with correct structure
    initial_state = State({
        "tickers": [],
        "anomalies": []
    })
    
    # Run workflow
    result = app.invoke(initial_state)
    
    print("✅ Workflow finished:", result)

