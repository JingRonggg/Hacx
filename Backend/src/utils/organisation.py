#This Script creates a new subfolder full of training information each time Logistic Regression Model is trained

import os
from datetime import datetime

def create_training_subdirectory(base_dir='utils/training_info'):
    # Get the current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    # Create the new directory path
    new_dir_path = os.path.join(base_dir, current_date)
    # Create the directory if it doesn't exist
    if not os.path.exists(new_dir_path):
        os.makedirs(new_dir_path)
    return new_dir_path
