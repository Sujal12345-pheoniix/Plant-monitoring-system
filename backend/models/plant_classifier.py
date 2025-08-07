import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import os
from pathlib import Path

class PlantClassifier:
    def __init__(self, input_shape=(224, 224, 3), num_classes=10):
        self.model = self._build_model(input_shape, num_classes)
        self.input_shape = input_shape
        self.num_classes = num_classes

    def _build_model(self, input_shape, num_classes):
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=input_shape,
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze the base model
        base_model.trainable = False
        
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model

    def train(self, train_data, validation_data, epochs=10, batch_size=32):
        history = self.model.fit(
            train_data,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size
        )
        return history

    def predict(self, image):
        # Preprocess the image
        img = tf.keras.preprocessing.image.load_img(
            image, target_size=self.input_shape[:2]
        )
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        
        # Make prediction
        predictions = self.model.predict(img_array)
        return predictions[0]

    def save_model(self, path):
        self.model.save(path)

    @classmethod
    def load_model(cls, path):
        model = cls()
        model.model = tf.keras.models.load_model(path)
        return model

# Example usage:
if __name__ == "__main__":
    # Initialize the classifier
    classifier = PlantClassifier()
    
    # Example training data (replace with actual data)
    train_data = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True
    )
    
    # Train the model
    # classifier.train(train_data, validation_data)
    
    # Save the model
    # classifier.save_model('plant_classifier.h5') 