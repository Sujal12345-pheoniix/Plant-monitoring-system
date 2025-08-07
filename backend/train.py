import os
from models.crop_model import train_crop_model
import numpy as np
import joblib
import json

# Create models directory if it doesn't exist
models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
os.makedirs(models_dir, exist_ok=True)

# Train the model
try:
    result = train_crop_model()
    
    # Save the model and encoders
    joblib.dump(result['model'], os.path.join(models_dir, 'crop_model.joblib'))
    joblib.dump(result['encoders'], os.path.join(models_dir, 'encoders.joblib'))
    
    # Save model info and unique crops
    with open(os.path.join(models_dir, 'model_info.json'), 'w') as f:
        json.dump({
            'train_accuracy': result['train_accuracy'],
            'test_accuracy': result['test_accuracy'],
            'train_mae': result['train_mae'],
            'test_mae': result['test_mae'],
            'cv_mean': result['cv_mean'],
            'cv_std': result['cv_std'],
            'cv_scores': result['cv_scores'],
            'feature_importance': result['feature_importance'],
            'crop_stats': result['crop_stats']
        }, f, indent=2)
    
    with open(os.path.join(models_dir, 'unique_crops.json'), 'w') as f:
        json.dump(result['unique_crops'], f, indent=2)
    
    print("\nModel Training Results:")
    print("=" * 50)
    print(f"Training R² Score: {result['train_accuracy']:.4f}")
    print(f"Testing R² Score: {result['test_accuracy']:.4f}")
    print(f"Training MAE: {result['train_mae']:.4f}")
    print(f"Testing MAE: {result['test_mae']:.4f}")
    
    print("\nCross-Validation Results:")
    print("=" * 50)
    print(f"Mean CV R² Score: {result['cv_mean']:.4f} (+/- {result['cv_std']*2:.4f})")
    print(f"CV Scores: {[f'{score:.4f}' for score in result['cv_scores']]}")
    
    print("\nFeature Importance:")
    print("=" * 50)
    for feature in result['feature_importance']:
        print(f"{feature['feature']:<20}: {feature['importance']:.4f}")
    
    print("\nCrop Water Requirement Statistics:")
    print("=" * 50)
    for crop, stats in result['crop_stats'].items():
        print(f"\n{crop}:")
        print(f"  Average: {stats['mean']:.2f}")
        print(f"  Min: {stats['min']:.2f}")
        print(f"  Max: {stats['max']:.2f}")
    
    print("\nModel Information:")
    print("=" * 50)
    print(f"Number of unique crops: {len(result['unique_crops'])}")
    print("\nUnique crops:")
    for crop in sorted(result['unique_crops']):
        print(f"- {crop}")
    
except Exception as e:
    print(f"Error training model: {str(e)}") 