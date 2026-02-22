# Task Tracker
**URL**: `https://roadmap.sh/projects/task-tracker`

## Usage
1. Clone the repo
2. python3 task_tracker.py [action]
3. **action**: add, mark-in-progress, mark-done, delete 
3. examples: 
- python3 task_tracker add call-mama
- python3 task_tracker *ID* mark-done
- python3 task_tracker delete *ID*

## Roadmap
- use postgres
- implement circuit breaker while connecting to db
- implement graceful degradation, read-only should work even if db is not working
- add authentication
- user can add/delete/update/get tasks
