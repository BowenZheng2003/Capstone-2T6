import joblib


def load_model(type: str):
    if type == 'emotion':
        # REPLACE PATHS WHEN RUNNING FOR YOURSELF
        scaler = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\emotion_scaler.pkl')
        predictor = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\emotion_kmeans_model.pkl')
    
    elif type == 'confidence':
        # REPLACE PATHS WHEN RUNNING FOR YOURSELF
        scaler = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\confidence_scaler.pkl')
        predictor = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\kmeans_model.pkl')

    elif type == 'delivery':
        # REPLACE PATHS WHEN RUNNING FOR YOURSELF
        scaler = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\delivery_scaler.pkl')
        predictor = joblib.load(r'C:\Users\Jeslyn\OneDrive\Desktop\capstone\Capstone-2T6\Audio_Stream\tmp\rf_model.pkl')

    return scaler, predictor


try:
    scaler, predictor = load_model('delivery')
    print("success")
except Exception as e:
    print("boohoo: ", e)