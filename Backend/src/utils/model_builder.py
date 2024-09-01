# Adapted from NishitP

import DataPrep
import FeatureSelection
import organisation as org
import os
import numpy as np
import pickle
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, GridSearchCV, learning_curve
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

# Create the subdirectory for this training session
save_dir = org.create_training_subdirectory()

# Use the save_dir in all functions that generate statistics or plots
DataPrep.create_distribution(DataPrep.train_news, save_dir)
DataPrep.create_distribution(DataPrep.test_news, save_dir)
DataPrep.create_distribution(DataPrep.valid_news, save_dir)

# Logistic Regression Pipeline with TF-IDF
logR_pipeline_ngram = Pipeline([
    ('LogR_tfidf', FeatureSelection.tfidf_ngram),
    ('LogR_clf', LogisticRegression(penalty="l2", C=1, max_iter=1000))
])

# Define the path for the output file
performance_report_file = os.path.join(save_dir, 'model_performance_report.txt')

# Open the file in write mode
with open(performance_report_file, 'w') as f:

    # Training and Evaluating Logistic Regression
    logR_pipeline_ngram.fit(DataPrep.train_news['Statement'], DataPrep.train_news['Label'])
    predicted_LogR_ngram = logR_pipeline_ngram.predict(DataPrep.test_news['Statement'])
    
    # Capture the performance report for Logistic Regression
    logR_report = classification_report(DataPrep.test_news['Label'], predicted_LogR_ngram)    
    f.write("Logistic Regression Performance:\n")
    f.write(logR_report)
    f.write("\n\n")  # Add spacing between reports
    
# Grid-Search for Logistic Regression
parameters_lr = {
    'LogR_tfidf__ngram_range': [(1, 1), (1, 2), (1, 3)],
    'LogR_tfidf__use_idf': [True, False],
    'LogR_tfidf__smooth_idf': [True, False]
}

gs_logR = GridSearchCV(logR_pipeline_ngram, parameters_lr, n_jobs=1, scoring="f1")
gs_logR.fit(DataPrep.train_news['Statement'], DataPrep.train_news['Label'])
print("Best Logistic Regression Parameters:", gs_logR.best_params_)

# Saving the Logistic Regression
model_file = 'final_model.sav'
pickle.dump(gs_logR.best_estimator_, open(model_file, 'wb'))

# Plotting Learning Curve
def plot_learning_curve(pipeline, title):
    cv = KFold(n_splits=5, shuffle=True)
    X = DataPrep.train_news["Statement"]
    y = DataPrep.train_news["Label"]
    
    train_sizes, train_scores, test_scores = learning_curve(
        pipeline, X, y, n_jobs=-1, cv=cv, train_sizes=np.linspace(.1, 1.0, 5)
    )
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.figure()
    plt.title(title)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation score")
    plt.legend(loc="best")
    plt.ylim(-.1, 1.1)
    plt.savefig(os.path.join(save_dir, f'{title}_learning_curve.png'))
    plt.clf()

# Showing Most Informative Features for Logistic Regression
def show_most_informative_features(model, vect, clf, n=20, save_dir=None):
    vectorizer = model.named_steps[vect]
    classifier = model.named_steps[clf]
    feature_names = vectorizer.get_feature_names_out()
    
    coefs = sorted(zip(classifier.coef_[0], feature_names), reverse=True)

    # Handle case where the list might not have enough elements
    top_positive_coefs = coefs[:n]
    top_negative_coefs = coefs[-n:]

    # Open the file to write the coefficients
    with open(os.path.join(save_dir, 'most_informative_features.txt'), 'w') as f:
        # Write header
        f.write(f"{'Top Positive Coefficients':^40} | {'Top Negative Coefficients':^40}\n")
        f.write("-" * 81 + "\n")
        
        # Write each coefficient pair
        for (cp, fnp), (cn, fnn) in zip(top_positive_coefs, top_negative_coefs):
            f.write(f"{cp:0.4f} {fnp: >30}    {cn:0.4f} {fnn: >30}\n")


plot_learning_curve(gs_logR.best_estimator_, "Logistic Regression Classifier")
show_most_informative_features(gs_logR.best_estimator_, 'LogR_tfidf', 'LogR_clf')