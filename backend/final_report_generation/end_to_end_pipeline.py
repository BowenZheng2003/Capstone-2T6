from presentation_analyzer.utils.au_flags import end_to_end_video
from backend.whisper_functions import transcribe_audio_chunks
from Audio_Stream.utils import audio_extraction, combined_pipeline
from backend.final_report_generation.contatenation import concatenate_streams
from backend.final_report_generation.LLM_prompting import call_deepseek
import json

def generate_full_report(input_video: str):
    print("HERE")
    audio_file = audio_extraction.extract_mp3(input_file=input_video) #get the audio from the video file

    print(audio_file)
    

    text_json = transcribe_audio_chunks(file_path=audio_file, chunk_seconds=5) #get the transcript json
    audio_json = combined_pipeline.get_audio_json(input_path=audio_file)
    video_json = end_to_end_video(video_path=input_video)
    

    # Load the full JSON
    with open(video_json, "r") as f:  # replace with your file path
        data = json.load(f)

    # Suppose `data` is your full JSON object
    segments_only = data.get("segments", [])

    # Save to a new JSON file
    with open("video_segments.json", "w") as f:
        json.dump(segments_only, f, indent=4)


    print(audio_json, text_json, "video_segments.json")

    #concatenate all json files into one merged json
    merged_json = concatenate_streams(audio=audio_json, video="video_segments.json", text=text_json)
    #print("HERE TOO")
    print(merged_json)
    report = call_deepseek(merged_json=merged_json, context="coke rant") #for now this prints out deepseek's evaluation

    return report