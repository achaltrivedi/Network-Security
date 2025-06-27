import os
import sys
from urllib.parse import urlparse

from networksecurity.exception.exception import NetworkSecurityException 
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.main_utils.utils import save_object, load_object, load_numpy_array_data, evaluate_models
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)

import mlflow
import mlflow.sklearn
import dagshub

# ✅ Configure DagsHub MLflow tracking
dagshub.init(repo_owner='achaltrivedi1325', repo_name='Network-Security', mlflow=True)

# ✅ Securely use environment variables for MLflow login (recommended to store in .env or set externally)
os.environ["MLFLOW_TRACKING_USERNAME"] = "achaltrivedi1325"
os.environ["MLFLOW_TRACKING_PASSWORD"] = "d34ba065f6fbc73a0d4465fa516d74d5340705d7"

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(self, best_model, classification_metric, model_name="BestModel"):
        mlflow.set_tracking_uri("https://dagshub.com/achaltrivedi1325/Network-Security.mlflow")
        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        with mlflow.start_run():
            # Log metrics
            mlflow.log_metric("f1_score", classification_metric.f1_score)
            mlflow.log_metric("precision_score", classification_metric.precision_score)
            mlflow.log_metric("recall_score", classification_metric.recall_score)

            # Log model
            if tracking_url_type_store != "file":
                mlflow.sklearn.log_model(sk_model=best_model, artifact_path="model", registered_model_name=model_name)
            else:
                mlflow.sklearn.log_model(sk_model=best_model, artifact_path="model")

    def train_model(self, X_train, y_train, X_test, y_test):
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1, max_iter=1000),
            "AdaBoost": AdaBoostClassifier(),
        }

        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy', 'log_loss'],
            },
            "Random Forest": {
                'n_estimators': [8, 16, 32, 64, 128],
            },
            "Gradient Boosting": {
                'learning_rate': [0.1, 0.01, 0.05],
                'subsample': [0.6, 0.7, 0.8],
                'n_estimators': [32, 64, 128],
            },
            "Logistic Regression": {},
            "AdaBoost": {
                'learning_rate': [0.1, 0.01],
                'n_estimators': [32, 64, 128],
            }
        }

        model_report = evaluate_models(X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test, models=models, param=params)
        best_model_score = max(model_report.values())
        best_model_name = list(model_report.keys())[list(model_report.values()).index(best_model_score)]
        best_model = models[best_model_name]

        # Training and evaluation
        y_train_pred = best_model.predict(X_train)
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)

        y_test_pred = best_model.predict(X_test)
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        # Log to MLflow
        self.track_mlflow(best_model, classification_train_metric, model_name=best_model_name)
        self.track_mlflow(best_model, classification_test_metric, model_name=f"{best_model_name}_test")

        # Save model with preprocessor
        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path, obj=network_model)

        # Also save the raw model (optional)
        save_object("final_model/model.pkl", best_model)

        # Create model trainer artifact
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            trained_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric,
        )
        logging.info(f"Model trainer artifact created: {model_trainer_artifact}")
        return model_trainer_artifact

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            X_train, y_train = train_arr[:, :-1], train_arr[:, -1]
            X_test, y_test = test_arr[:, :-1], test_arr[:, -1]

            return self.train_model(X_train, y_train, X_test, y_test)

        except Exception as e:
            raise NetworkSecurityException(e, sys)
