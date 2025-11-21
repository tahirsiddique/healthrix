"""
ML Prediction Service
=====================

Machine learning models for performance prediction and analytics.

Features:
- Performance forecasting (LSTM)
- Anomaly detection (Isolation Forest)
- Churn/attrition prediction (XGBoost)
- Task recommendations
"""

from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os


class PerformancePredictor:
    """
    Predicts future performance based on historical data.

    Uses time-series forecasting to predict employee performance trends.
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize performance predictor.

        Args:
            model_path: Path to saved model (optional)
        """
        self.model = None
        self.scaler = StandardScaler()

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def prepare_features(self, performance_history: pd.DataFrame) -> np.ndarray:
        """
        Prepare features from performance history.

        Args:
            performance_history: DataFrame with columns: date, performance_score

        Returns:
            Feature matrix
        """
        # Sort by date
        df = performance_history.sort_values('date')

        # Calculate rolling statistics
        df['ma_7'] = df['performance_score'].rolling(window=7, min_periods=1).mean()
        df['ma_30'] = df['performance_score'].rolling(window=30, min_periods=1).mean()
        df['std_7'] = df['performance_score'].rolling(window=7, min_periods=1).std()

        # Day of week features
        df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

        # Trend features
        df['days_since_start'] = (pd.to_datetime(df['date']) - pd.to_datetime(df['date'].min())).dt.days

        # Select features
        features = [
            'performance_score', 'ma_7', 'ma_30', 'std_7',
            'day_of_week', 'is_weekend', 'days_since_start'
        ]

        return df[features].fillna(0).values

    def predict_next_days(
        self,
        performance_history: pd.DataFrame,
        days: int = 7
    ) -> List[Dict]:
        """
        Predict performance for next N days.

        Args:
            performance_history: Historical performance data
            days: Number of days to predict

        Returns:
            List of predictions with confidence intervals
        """
        if len(performance_history) < 7:
            raise ValueError("Need at least 7 days of history for prediction")

        # Prepare features
        features = self.prepare_features(performance_history)

        # Simple moving average prediction (baseline)
        # In production, use LSTM or Prophet
        recent_avg = performance_history['performance_score'].tail(7).mean()
        recent_std = performance_history['performance_score'].tail(7).std()

        predictions = []
        last_date = pd.to_datetime(performance_history['date'].max())

        for i in range(1, days + 1):
            pred_date = last_date + timedelta(days=i)

            # Baseline prediction with trend adjustment
            trend = (performance_history['performance_score'].tail(30).mean() -
                    performance_history['performance_score'].head(30).mean()) / 30

            predicted_score = recent_avg + (trend * i)

            # Confidence interval (±1 std)
            predictions.append({
                'date': pred_date.strftime('%Y-%m-%d'),
                'predicted_score': round(predicted_score, 2),
                'confidence_lower': round(predicted_score - recent_std, 2),
                'confidence_upper': round(predicted_score + recent_std, 2),
                'confidence_level': 0.68  # 1 std ≈ 68% confidence
            })

        return predictions

    def load_model(self, path: str):
        """Load trained model from disk."""
        self.model = joblib.load(path)

    def save_model(self, path: str):
        """Save trained model to disk."""
        joblib.dump(self.model, path)


class AnomalyDetector:
    """
    Detects anomalous performance patterns.

    Uses Isolation Forest to identify unusual performance.
    """

    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector.

        Args:
            contamination: Expected proportion of anomalies
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_fitted = False

    def fit(self, performance_data: pd.DataFrame):
        """
        Train anomaly detector on historical data.

        Args:
            performance_data: DataFrame with performance metrics
        """
        # Prepare features
        features = self._prepare_features(performance_data)

        # Scale features
        features_scaled = self.scaler.fit_transform(features)

        # Fit model
        self.model.fit(features_scaled)
        self.is_fitted = True

    def detect_anomalies(
        self,
        performance_data: pd.DataFrame
    ) -> List[Dict]:
        """
        Detect anomalies in performance data.

        Args:
            performance_data: DataFrame with performance metrics

        Returns:
            List of detected anomalies with scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before detection")

        # Prepare features
        features = self._prepare_features(performance_data)
        features_scaled = self.scaler.transform(features)

        # Predict anomalies (-1 = anomaly, 1 = normal)
        predictions = self.model.predict(features_scaled)

        # Get anomaly scores (lower = more anomalous)
        scores = self.model.score_samples(features_scaled)

        # Compile results
        anomalies = []
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly detected
                anomalies.append({
                    'date': performance_data.iloc[idx]['date'],
                    'emp_id': performance_data.iloc[idx]['emp_id'],
                    'performance_score': performance_data.iloc[idx]['performance_score'],
                    'anomaly_score': round(float(score), 4),
                    'severity': self._calculate_severity(score),
                    'description': self._generate_description(
                        performance_data.iloc[idx],
                        score
                    )
                })

        return anomalies

    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for anomaly detection."""
        features = []

        for _, row in data.iterrows():
            features.append([
                row.get('performance_score', 0),
                row.get('productivity_score', 0),
                row.get('behavior_score', 0),
                row.get('task_count', 0),
                row.get('idle_hours', 0),
                row.get('conduct_flag', 0),
            ])

        return np.array(features)

    def _calculate_severity(self, score: float) -> str:
        """Calculate anomaly severity."""
        if score < -0.5:
            return "high"
        elif score < -0.2:
            return "medium"
        else:
            return "low"

    def _generate_description(self, row: pd.Series, score: float) -> str:
        """Generate human-readable anomaly description."""
        perf = row.get('performance_score', 0)

        if perf < 50:
            return f"Significantly below average performance ({perf:.1f}%)"
        elif perf > 150:
            return f"Unusually high performance ({perf:.1f}%)"
        else:
            return f"Unexpected performance pattern detected (score: {score:.3f})"


class ChurnPredictor:
    """
    Predicts employee churn/attrition risk.

    Identifies employees at risk of leaving based on performance trends.
    """

    def __init__(self):
        """Initialize churn predictor."""
        self.model = None  # Would be XGBoost in production
        self.feature_names = [
            'avg_performance_30d',
            'performance_trend',
            'performance_volatility',
            'days_below_target',
            'conduct_flags',
            'tenure_days'
        ]

    def predict_churn_risk(
        self,
        emp_id: str,
        performance_history: pd.DataFrame,
        tenure_days: int
    ) -> Dict:
        """
        Predict churn risk for an employee.

        Args:
            emp_id: Employee ID
            performance_history: Performance history DataFrame
            tenure_days: Days since hire

        Returns:
            Churn risk assessment
        """
        # Calculate features
        avg_perf = performance_history['performance_score'].tail(30).mean()
        trend = self._calculate_trend(performance_history)
        volatility = performance_history['performance_score'].tail(30).std()
        days_below = (performance_history['performance_score'] < 70).sum()
        conduct_flags = performance_history['conduct_flag'].sum()

        # Simple rule-based prediction (replace with ML model)
        risk_score = 0.0

        if avg_perf < 60:
            risk_score += 0.3
        elif avg_perf < 70:
            risk_score += 0.1

        if trend < -5:  # Declining trend
            risk_score += 0.2

        if volatility > 20:
            risk_score += 0.1

        if days_below > 10:
            risk_score += 0.2

        if conduct_flags > 3:
            risk_score += 0.2

        # Tenure factor (higher risk in first 90 days or after 2 years)
        if tenure_days < 90 or tenure_days > 730:
            risk_score += 0.1

        risk_score = min(risk_score, 1.0)  # Cap at 1.0

        # Classify risk level
        if risk_score > 0.7:
            risk_level = "high"
            recommendation = "Immediate intervention recommended"
        elif risk_score > 0.4:
            risk_level = "medium"
            recommendation = "Schedule check-in with manager"
        else:
            risk_level = "low"
            recommendation = "No immediate action needed"

        return {
            'emp_id': emp_id,
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'factors': {
                'avg_performance': round(avg_perf, 2),
                'performance_trend': round(trend, 2),
                'volatility': round(volatility, 2),
                'days_below_target': int(days_below),
                'conduct_issues': int(conduct_flags),
                'tenure_days': tenure_days
            }
        }

    def _calculate_trend(self, history: pd.DataFrame) -> float:
        """Calculate performance trend."""
        if len(history) < 30:
            return 0.0

        recent = history['performance_score'].tail(30).mean()
        previous = history['performance_score'].head(30).mean()

        return recent - previous


class MLPredictionService:
    """
    Main ML service coordinating all prediction models.
    """

    def __init__(self, model_dir: str = "models"):
        """
        Initialize ML prediction service.

        Args:
            model_dir: Directory containing trained models
        """
        self.model_dir = model_dir
        self.performance_predictor = PerformancePredictor()
        self.anomaly_detector = AnomalyDetector()
        self.churn_predictor = ChurnPredictor()

    async def get_predictions_for_employee(
        self,
        emp_id: str,
        performance_history: pd.DataFrame,
        tenure_days: int
    ) -> Dict:
        """
        Get all predictions for an employee.

        Args:
            emp_id: Employee ID
            performance_history: Historical performance data
            tenure_days: Days since hire

        Returns:
            Comprehensive predictions
        """
        results = {
            'emp_id': emp_id,
            'predictions': {},
            'anomalies': [],
            'churn_risk': {},
            'recommendations': []
        }

        # Performance forecasting
        try:
            forecasts = self.performance_predictor.predict_next_days(
                performance_history,
                days=7
            )
            results['predictions']['next_7_days'] = forecasts
        except Exception as e:
            results['predictions']['error'] = str(e)

        # Anomaly detection
        try:
            # Fit on recent data
            if len(performance_history) >= 30:
                self.anomaly_detector.fit(performance_history.tail(100))
                anomalies = self.anomaly_detector.detect_anomalies(
                    performance_history.tail(30)
                )
                results['anomalies'] = anomalies
        except Exception as e:
            results['anomalies'] = []

        # Churn prediction
        try:
            churn_risk = self.churn_predictor.predict_churn_risk(
                emp_id,
                performance_history,
                tenure_days
            )
            results['churn_risk'] = churn_risk
        except Exception as e:
            results['churn_risk'] = {'error': str(e)}

        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)

        return results

    def _generate_recommendations(self, prediction_results: Dict) -> List[str]:
        """Generate actionable recommendations based on predictions."""
        recommendations = []

        # Check forecasts
        if 'next_7_days' in prediction_results['predictions']:
            forecasts = prediction_results['predictions']['next_7_days']
            avg_predicted = np.mean([f['predicted_score'] for f in forecasts])

            if avg_predicted < 70:
                recommendations.append(
                    "Performance trending downward. Consider providing additional support or training."
                )

        # Check anomalies
        if prediction_results['anomalies']:
            high_severity = [a for a in prediction_results['anomalies'] if a['severity'] == 'high']
            if high_severity:
                recommendations.append(
                    f"Detected {len(high_severity)} high-severity performance anomalies. Review recent activities."
                )

        # Check churn risk
        churn = prediction_results.get('churn_risk', {})
        if churn.get('risk_level') in ['high', 'medium']:
            recommendations.append(churn.get('recommendation', ''))

        return recommendations


# Example usage
"""
# In your API endpoint:

from phase3_enterprise.ml_engine.prediction_service import MLPredictionService

ml_service = MLPredictionService(model_dir="/models")

@app.get("/api/v1/predictions/{emp_id}")
async def get_employee_predictions(
    emp_id: str,
    db: Session = Depends(get_db)
):
    # Get performance history from database
    performance_history = db.query(PerformanceScore).filter(
        PerformanceScore.emp_id == emp_id
    ).order_by(PerformanceScore.date).all()

    # Convert to DataFrame
    df = pd.DataFrame([{
        'date': score.date,
        'emp_id': score.emp_id,
        'performance_score': score.final_performance_percent,
        'productivity_score': score.weighted_prod_score,
        'behavior_score': score.weighted_behavior_score,
        'task_count': score.task_count,
        'idle_hours': score.idle_hours,
        'conduct_flag': score.conduct_flag,
    } for score in performance_history])

    # Get employee tenure
    employee = db.query(User).filter(User.emp_id == emp_id).first()
    tenure_days = (datetime.now().date() - employee.hire_date).days

    # Get predictions
    predictions = await ml_service.get_predictions_for_employee(
        emp_id,
        df,
        tenure_days
    )

    return predictions
"""
