# -*- coding: utf-8 -*-
"""PRODIGY_DS_04

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Kp7pzYKguNQG-5GByqIqG7V2GQWG1LNl
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import re
import nltk

# Ensure nltk resources are downloaded
nltk.download('vader_lexicon')

# Load data
train_data = pd.read_csv('/content/twitter_training.csv', encoding='utf-8', header=None)
validation_data = pd.read_csv('/content/twitter_validation.csv', encoding='utf-8', header=None)

# Define column names
columns = ['TweetID', 'UserID', 'Label', 'Tweet']
train_data.columns = columns
validation_data.columns = columns

# Display the first few rows of the training data
print("Training Data Sample:")
print(train_data.head())

# Display the first few rows of the validation data
print("\nValidation Data Sample:")
print(validation_data.head())

# Combine train and validation data for visualization and analysis
data = pd.concat([train_data, validation_data])

# Check for missing values
print("\nMissing Values:")
print(data.isnull().sum())

# Fill or drop missing values if necessary
data.dropna(subset=['Tweet'], inplace=True)

# Display label distribution
print("\nLabel Distribution:")
print(data['Label'].value_counts())

# Visualize label distribution
plt.figure(figsize=(8, 6))
sns.countplot(data['Label'])
plt.title('Label Distribution in Dataset')
plt.xlabel('Sentiment Label')
plt.ylabel('Count')
plt.show()

# Text Preprocessing
def preprocess_text(text):
    # Remove special characters, numbers, and emojis
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = text.lower()
    return text

data['Processed_Tweet'] = data['Tweet'].apply(preprocess_text)

# Check if preprocessing works correctly
print("\nSample Processed Tweets:")
print(data['Processed_Tweet'].head())

# Word Cloud for each sentiment
def plot_wordcloud(label):
    subset = data[data['Label'] == label]
    text = ' '.join(subset['Processed_Tweet'])
    wordcloud = WordCloud(width=800, height=400, max_font_size=100, collocations=False).generate(text)

    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Word Cloud for {label}')
    plt.show()

# Ensure that word clouds are generated only for labels that have sufficient words
for label in data['Label'].unique():
    try:
        plot_wordcloud(label)
    except ValueError as e:
        print(f"Skipping WordCloud for {label} due to insufficient data: {e}")

# Sentiment Analysis using NLTK's VADER
sia = SentimentIntensityAnalyzer()

# Calculate sentiment scores
data['Sentiment_Score'] = data['Processed_Tweet'].apply(lambda x: sia.polarity_scores(x)['compound'])

# Define a function to categorize sentiment
def categorize_sentiment(score):
    if score > 0.05:
        return 'positive'
    elif score < -0.05:
        return 'negative'
    else:
        return 'neutral'

data['Predicted_Label'] = data['Sentiment_Score'].apply(categorize_sentiment)

# Compare actual vs predicted labels
plt.figure(figsize=(12, 6))
sns.countplot(data['Label'], label='Actual')
sns.countplot(data['Predicted_Label'], label='Predicted', color='orange', alpha=0.5)
plt.title('Actual vs Predicted Sentiment Labels')
plt.xlabel('Sentiment Label')
plt.ylabel('Count')
plt.legend()
plt.show()

# Evaluate model performance
print("\nClassification Report:")
print(classification_report(data['Label'], data['Predicted_Label']))

# Confusion Matrix
cm = confusion_matrix(data['Label'], data['Predicted_Label'])
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['negative', 'neutral', 'positive'], yticklabels=['negative', 'neutral', 'positive'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('Actual Label')
plt.show()

# Optional: Train a Naive Bayes Classifier
X = data['Processed_Tweet']
y = data['Label']

# Split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorize the text
vectorizer = CountVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Train the Naive Bayes classifier
model = MultinomialNB()
model.fit(X_train_vectorized, y_train)

# Predict on the test set
y_pred = model.predict(X_test_vectorized)

# Evaluate the classifier
print("\nNaive Bayes Classification Report:")
print(classification_report(y_test, y_pred))

# Confusion Matrix for Naive Bayes
cm_nb = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm_nb, annot=True, fmt='d', cmap='Greens', xticklabels=['negative', 'neutral', 'positive'], yticklabels=['negative', 'neutral', 'positive'])
plt.title('Naive Bayes Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('Actual Label')
plt.show()