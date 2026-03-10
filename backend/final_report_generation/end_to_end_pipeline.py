from presentation_analyzer.utils.au_flags import end_to_end_video
from backend.whisper_functions import transcribe_audio_chunks
from Audio_Stream.utils import audio_extraction, combined_pipeline
from backend.final_report_generation.contatenation import concatenate_streams
from backend.final_report_generation.LLM_prompting import call_deepseek
import json

def generate_full_report(input_video: str, on_progress=None, context: str = "General presentation"):
    def emit(step, progress, message):
        if on_progress:
            on_progress({"step": step, "progress": progress, "message": message})

    emit("start", 0, "Extracting audio…")
    audio_file = audio_extraction.extract_mp3(input_file=input_video)
    print(audio_file)

    emit("transcribing", 10, "Transcribing speech…")
    text_json = transcribe_audio_chunks(file_path=audio_file, chunk_seconds=5)

    emit("audio_features", 25, "Analyzing audio features…")
    audio_json = combined_pipeline.get_audio_json(input_path=audio_file)

    emit("video_features", 45, "Analyzing video features…")
    video_json = end_to_end_video(video_path=input_video)

    emit("merging", 80, "Merging data streams…")
    with open(video_json, "r") as f:
        data = json.load(f)
    segments_only = data.get("segments", [])
    with open("video_segments.json", "w") as f:
        json.dump(segments_only, f, indent=4)

    merged_json = concatenate_streams(audio=audio_json, video="video_segments.json", text=text_json)
    print(audio_json, text_json, "video_segments.json")
    print(merged_json)

    emit("llm", 85, "Generating your report…")
    report = call_deepseek(merged_json=merged_json, context=context)

    return report
