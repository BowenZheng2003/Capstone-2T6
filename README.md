# Team running app instructions

1. export your huggingface token in your environment
2. Activate your virtual environment (ex: source .venv_x86/bin/activate)
3. cd into frontend and run 'npm start' (run 'npm install' if you need)
4. in a new terminal, in the Capstone-2T6 directory run 'uvicorn backend.app:app --reload' to start the backend (now backend and frontend are both running and should be connected)
5. go to localhost:3000 to access frontend UI for utilization
