import warnings
# Ignore the UserWarning about feature names
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
import os
import pandas as pd
import talib
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
import warnings


class PredictionClass:

    def __init__(self, crypto):
        try:
            # Load your data from the CSV file
            self.data = pd.read_csv(f'E:/QuantumTrading/QT-Cryptobot/Data/{crypto}.csv', parse_dates=['timestamp'], index_col='timestamp')
            self.data = self.data[~self.data.index.duplicated(keep='first')]
            self.data = self.data.resample('T').ffill()
            self.data = self.data.drop(columns=['trade_count', 'vwap'])
            self.data = self.data.tail(500)
            self.crypto = crypto
            self.scaler = StandardScaler()
        except Exception as e:
            print(f"An error occurred during initialization: {e}")
            self.data = None

    def predict(self):
        try:
            if self.data is not None and self.scaler is not None:
                # Calculate MACD using TA-Lib
                self.data['macd'], _, _ = talib.MACD(self.data['close'])

                # Calculate RSI using TA-Lib
                self.data['rsi'] = talib.RSI(self.data['close'])

                self.data = self.data.dropna()

                # Assuming you want to predict price increase (1) or decrease (0)
                self.data['target'] = (self.data['close'].shift(-1) > self.data['close']).astype(int)

                # Features (X) and target (y)
                X = self.data[['close', 'macd', 'rsi']]
                y = self.data['target']

                # Data Splitting
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                # Feature Scaling using fitted scaler
                X_train_scaled = self.scaler.fit_transform(X_train)
                X_test_scaled = self.scaler.transform(X_test)

                # Assign column names after scaling
                X_train_scaled = pd.DataFrame(X_train_scaled, columns=X.columns)
                X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)

                # Train SVM classifier
                svm_classifier = SVC(kernel='linear', C=1.0)
                svm_classifier.fit(X_train_scaled.values, y_train)

                # Make predictions on the test set
                y_pred = svm_classifier.predict(X_test_scaled.values)

                # Evaluate the model
                accuracy_test = accuracy_score(y_test, y_pred)

                # Predict for the next minute after the last data point
                last_data_point = X.iloc[-1].values.reshape(1, -1)
                last_data_point_scaled = self.scaler.transform(last_data_point.reshape(1, -1))
                prediction_for_next_minute = svm_classifier.predict(last_data_point_scaled) 

                # Perform k-fold cross-validation
                n_folds = 5
                stratified_kfold = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
                cross_val_results = cross_val_score(svm_classifier, self.scaler.transform(X), y, cv=stratified_kfold, scoring='accuracy')
                cross_val_mean = cross_val_results.mean()
                cross_val_std = cross_val_results.std()

                return prediction_for_next_minute, accuracy_test, cross_val_mean, cross_val_std
            else:
                print("Data is not loaded successfully or scaler is not initialized.")
                return None, None, None, None
        except Exception as e:
            print(f"An error occurred during analysis: {e}")
            return None, None, None, None


    def update_csv(self):
        try:
            prediction, accuracy_test, cross_val_mean, cross_val_std = self.predict()
            if prediction is not None:
                # Create or read the prediction.csv file
                csv_file_path = 'E:/QuantumTrading/QT-API/predictionData/prediction.csv'
                if not os.path.isfile(csv_file_path):
                    prediction_df = pd.DataFrame(columns=['symbol', 'prediction', 'accuracy_test', 'kv_accuracy'])
                else:
                    prediction_df = pd.read_csv(csv_file_path)

                # Filter the DataFrame based on the symbol
                symbol_filter = prediction_df['symbol'] == self.crypto
                prediction_df.loc[symbol_filter, 'symbol'] = self.crypto
                prediction_df.loc[symbol_filter, 'prediction'] = int(prediction[0])
                prediction_df.loc[symbol_filter, 'accuracy_test'] = accuracy_test
                prediction_df.loc[symbol_filter, 'kv_accuracy'] = f"{cross_val_mean:.4f} +/- {cross_val_std:.4f}"

                # Save the DataFrame back to the prediction.csv file
                prediction_df.to_csv(csv_file_path, index=False)
                print("CSV Updated Successfully.")
            else:
                print("Prediction is not available.")
        except Exception as e:
            print(f"An error occurred during CSV update: {e}")
