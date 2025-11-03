from pydub import AudioSegment
import Audio_Stream.utils.processing as processing
import Audio_Stream.utils.model as model

def get_audio_json(input_path: str):
    all_feature_cols = [
        [
            "F0semitoneFrom27.5Hz_sma3nz_stddevNorm",
            "loudness_sma3_amean",
            "HNRdBACF_sma3nz_amean",
            "jitterLocal_sma3nz_amean",
            "shimmerLocaldB_sma3nz_amean",
            "F0semitoneFrom27.5Hz_sma3nz_amean"
        ],
        [
            "F0semitoneFrom27.5Hz_sma3nz_amean",
            "F0semitoneFrom27.5Hz_sma3nz_stddevNorm",
            "loudness_sma3_amean",
            "HNRdBACF_sma3nz_amean",
            "jitterLocal_sma3nz_amean",
            "shimmerLocaldB_sma3nz_amean",
            "alphaRatioV_sma3nz_amean",
            "logRelF0-H1-H2_sma3nz_amean",
            "mfcc1_sma3_amean",
            "mfcc2_sma3_amean",
            "mfcc3_sma3_amean",
            "mfcc4_sma3_amean",
            "spectralFlux_sma3_amean",
            "slopeV0-500_sma3nz_amean"
        ],
        [
            "F0semitoneFrom27.5Hz_sma3nz_amean",
            "HNRdBACF_sma3nz_amean",
            "jitterLocal_sma3nz_amean",
            "shimmerLocaldB_sma3nz_amean",
            "loudness_sma3_amean",
            "mfcc1_sma3_amean",
            "mfcc2_sma3_amean",
            "mfcc3_sma3_amean"
        ]
    ]

    all_cluster_labels = [
        {
            0: "Low Confidence (Tense)",
            1: "High Confidence (Expressive)",
            2: "Very Low Confidence (Flat, Pause)",
            3: "Moderate Confidence",
            4: "High Confidence (Calm)"
        },
        {
            0: "Tense (low confidence)",
            1: "Neutral",
            2: "Nervous",
            3: "Energetic and Assertive",
            4: "Enthusiastic",
            5: "Expressive and Engaged"
        },
        ["Focused", "Authentic", "NotAwkward", "EngagingTone"]
    ]

    models = ["confidence", "emotion", "delivery"]

    all_dfs = []

    # RUNNING MODELS
    try:
        # REPLACE WITH THE CORRECT INTERVIEW AUDIO FILE PATH
        audio = AudioSegment.from_file(input_path)
        for i, feature_cols in enumerate(all_feature_cols):
            # Segment the file based on the current feature columns corresponding to the appropriate model
            segments = processing.segment_audio(audio, feature_cols=feature_cols)

            # Upload the correct models
            scaler, predictor = model.load_model(models[i])

            # Run the interview through the current model
            df = model.run_model(scaler, predictor, feature_cols=feature_cols, cluster_labels=all_cluster_labels[i], segments=segments, label = models[i])

            # Creating a list of dataframes to merge after
            all_dfs.append(df)

            # Debugging print statement
            #print(df)
    except Exception as e:
        raise RuntimeError(f"Error: {e}.\n Was not able to extract features or run the models using test interview.") from e
    print("ALL OUR DATAFRAMES LOL: ", all_dfs)
    # COMBINING OUTPUTS
    try: 
        # If target column labels match the model names exactly we can get rid of this list and use the models list instead
        target_columns = ["emotion", "confidence", "delivery"]
        results = processing.merge_on_timestamp(all_dfs, target_columns)
        output_path = processing.create_json_output(results, target_columns)
        print(output_path)
    except Exception as e: 
        raise RuntimeError(f"Error: {e}.\n Was not able to merge and convert outputs to a list of dicts.") from e
    
    return output_path

get_audio_json(input_path=r"/Users/jeslyn/Desktop/projects/Capstone-2T6/backend/IMG_4027 2.MOV")