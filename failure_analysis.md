## Pipeline Failure Analysis
(Mock response — add API credits for live Claude analysis)

### Root Cause
Terraform state lock conflict — a previous pipeline run was cancelled mid-apply, leaving a lock in the state backend.

### How to Fix
1. Find the lock ID in the error message
2. Run: terraform force-unlock <LOCK_ID>
3. Verify no other pipeline is running
4. Re-run the pipeline

### How to Prevent
Add lock_timeout = '5m' to your backend config. Use pipeline concurrency controls to prevent parallel runs.
