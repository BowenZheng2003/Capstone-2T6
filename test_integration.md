# Testing the Frontend-Backend Integration

## Setup Instructions

### 1. Start the Backend Server

Open a terminal and navigate to the backend directory:

```bash
cd /Users/bellayang/Capstone-2T6/backend
uvicorn app:app --reload
```

The backend will be available at `http://localhost:8000`

### 2. Start the Frontend Development Server

Open another terminal and navigate to the project root:

```bash
cd /Users/bellayang/Capstone-2T6
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Testing the Integration

### 1. Basic Connection Test

1. Open `http://localhost:5173` in your browser
2. You should see the "Presentation Analysis Tool" interface
3. The interface should show a file upload area

### 2. Upload and Process a Video

1. Click "Choose Video File" to select a video file
2. Once selected, you'll see file information and an "Upload Video" button
3. Click "Upload Video" to upload the file to the backend
4. After successful upload, click "Start Analysis" to begin processing
5. The interface will show a loading spinner while processing
6. Once complete, you'll see the analysis results

### 3. API Endpoints Available

- `GET /` - Health check
- `GET /ping` - Simple ping test
- `POST /upload-video` - Upload video file
- `POST /process-video/{processing_id}` - Start processing
- `GET /status/{processing_id}` - Check processing status
- `GET /results/{processing_id}` - Get analysis results

## Expected Behavior

1. **File Selection**: Only video files should be accepted
2. **Upload**: File should upload successfully and return a processing ID
3. **Processing**: Status should update from "uploaded" → "processing" → "completed"
4. **Results**: Analysis results should be displayed in JSON format
5. **Reset**: "Reset" button should clear all state and allow new uploads

## Troubleshooting

### Backend Issues
- Make sure all Python dependencies are installed
- Check that the backend is running on port 8000
- Look for error messages in the backend terminal

### Frontend Issues
- Check browser console for JavaScript errors
- Ensure the frontend is running on port 5173
- Verify CORS settings if you see network errors

### Common Issues
- **CORS errors**: The backend is configured to allow requests from localhost:5173
- **File upload errors**: Make sure the file is a valid video format
- **Processing errors**: Check that all required Python packages are installed

## Next Steps

Once the basic integration is working, you can:

1. Enhance the results display with better formatting
2. Add progress indicators for each processing step
3. Implement error handling for specific failure cases
4. Add support for different video formats
5. Integrate with the actual analysis pipelines (audio, video, LLM)
