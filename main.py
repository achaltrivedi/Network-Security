from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.components.data_validation import DataValidation
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig,DataTransformationConfig,ModelTrainerConfig
from networksecurity.entity.config_entity import TrainingPipelineConfig
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

import sys

if __name__=="__main__":
    try:
        training_pipeline_config=TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion= DataIngestion(data_ingestion_config)
        logging.info("Initiating data ingestion component")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Ingestion completed successfully")
        data_validation_config=DataValidationConfig(training_pipeline_config)
        data_validation=DataValidation(data_ingestion_artifact, data_validation_config)
        logging.info("Initiating data validation component")
        data_validation_artifact=data_validation.initiate_data_validation()
        logging.info("Data Validation completed successfully")
        print(data_validation_artifact)
        data_transformation_config=DataTransformationConfig(training_pipeline_config)
        logging.info("Data Transformation Started")
        data_transformation=DataTransformation(data_validation_artifact,data_transformation_config)
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)
        logging.info("Data Transformation Completed")
        
        logging.info("Model Training Started")
        model_trainer_config=ModelTrainerConfig(training_pipeline_config)
        model_trainer=ModelTrainer(model_trainer_config,data_transformation_artifact)
        model_trainer_artifact=model_trainer.initiate_model_trainer()

    except Exception as e:
        raise NetworkSecurityException(e, sys)
    