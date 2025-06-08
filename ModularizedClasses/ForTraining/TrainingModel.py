import pandas as pd
import numpy as np
import tensorflow as tf
import random
import os

from keras.models import Model
from keras.layers import Dense, Input, Dropout
from keras.callbacks import EarlyStopping
from keras.regularizers import l2
from BehaviourAnalysis import load_datasets

import matplotlib.pyplot as plt

ModelPath = "ModularizedClasses/ForTraining/"
DataPath = "ModularizedClasses/ForTraining/behaviours/"

# Build Autoencoder
def set_seed(seed=42):
    np.random.seed(seed)
    tf.random.set_seed(seed)
    random.seed(seed)

def build_encoder(input_dim):
    set_seed(42)
    input_dim = input_dim

    input_layer = Input(shape=(input_dim,))
    encoded = Dense(16, activation='relu',  activity_regularizer=l2(1e-4))(input_layer)
    encoded = Dropout(0.2)(encoded)
    encoded = Dense(8, activation='relu')(encoded)

    decoded = Dense(16, activation='relu')  (encoded)
    output_layer = Dense(input_dim,     activation='linear')(decoded)

    autoencod = Model(input_layer, output_layer)
    
    return autoencod
    

def TrainModel(model_path, data_path):

    os.makedirs(model_path, exist_ok=True)

    # Get datasets as tuple (train, cv, test)
    datasets = load_datasets(data_path)
    if datasets is None:
        raise ValueError("❌ Datasets could not be loaded. Check the path or file format.")
    
    # Unpack the tuple
    train, cv, test = datasets
    
    X_train = train.drop(columns=["source"])
    X_cv = cv.drop(columns=["source"])
    X_test = test.drop(columns=["source"])
    
    # Early stopping
    early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    # Build the model
    model = build_encoder(X_train.shape[1])
    model.compile(optimizer='adam', loss='mse')
    
    history = model.fit(
        X_train, X_train,
        epochs=100,
        batch_size=32,
        validation_data=(X_cv, X_cv),
        callbacks=[early_stop]
    )
    
    # Save the model
    model.save(model_path + "autoencoder_model.keras")
    
    return model, history

def plot_training_history(history):    
    plt.figure(figsize=(8, 5))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training and Validation Loss Curve')
    plt.legend()
    plt.grid(True)
    plt.show()