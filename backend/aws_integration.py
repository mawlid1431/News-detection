import os
import boto3
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class AWSIntegration:
    """AWS services integration for Trustify AI"""
    
    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.s3_bucket = os.getenv('S3_BUCKET_NAME', 'trustify-ai-data')
        self.cloudwatch_log_group = os.getenv('CLOUDWATCH_LOG_GROUP', '/aws/trustify-ai')
        
        # Initialize AWS clients
        self.s3_client = None
        self.cloudwatch_client = None
        self.sagemaker_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AWS service clients"""
        try:
            # S3 for data storage
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            # CloudWatch for logging
            self.cloudwatch_client = boto3.client(
                'logs',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            # SageMaker for ML model deployment
            self.sagemaker_client = boto3.client(
                'sagemaker-runtime',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            logger.info("AWS clients initialized successfully")
            
        except Exception as e:
            logger.warning(f"AWS client initialization failed: {e}")
    
    def log_verification(self, query: str, result: Dict[str, Any]):
        """Log verification to CloudWatch"""
        if not self.cloudwatch_client:
            return
        
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'query': query[:200],  # Truncate for privacy
                'status': result.get('status'),
                'credibility_score': result.get('credibility_score'),
                'processing_time_ms': result.get('processing_time_ms'),
                'sources_count': len(result.get('official_links', []))
            }
            
            self.cloudwatch_client.put_log_events(
                logGroupName=self.cloudwatch_log_group,
                logStreamName=f"verifications-{datetime.utcnow().strftime('%Y-%m-%d')}",
                logEvents=[{
                    'timestamp': int(datetime.utcnow().timestamp() * 1000),
                    'message': json.dumps(log_entry)
                }]
            )
            
        except Exception as e:
            logger.warning(f"CloudWatch logging failed: {e}")
    
    def store_verification_data(self, query: str, result: Dict[str, Any]) -> Optional[str]:
        """Store verification data in S3"""
        if not self.s3_client:
            return None
        
        try:
            # Create unique key
            timestamp = datetime.utcnow().strftime('%Y/%m/%d/%H')
            key = f"verifications/{timestamp}/{hash(query) % 10000}.json"
            
            # Prepare data
            data = {
                'query': query,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            
            return f"s3://{self.s3_bucket}/{key}"
            
        except Exception as e:
            logger.warning(f"S3 storage failed: {e}")
            return None
    
    def invoke_sagemaker_model(self, text: str, model_endpoint: str) -> Optional[Dict]:
        """Invoke SageMaker model for enhanced ML predictions"""
        if not self.sagemaker_client:
            return None
        
        try:
            response = self.sagemaker_client.invoke_endpoint(
                EndpointName=model_endpoint,
                ContentType='application/json',
                Body=json.dumps({'text': text})
            )
            
            result = json.loads(response['Body'].read().decode())
            return result
            
        except Exception as e:
            logger.warning(f"SageMaker invocation failed: {e}")
            return None
    
    def get_model_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics from CloudWatch"""
        if not self.cloudwatch_client:
            return {}
        
        try:
            # Get verification accuracy metrics
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='Trustify/AI',
                MetricName='VerificationAccuracy',
                Dimensions=[],
                StartTime=datetime.utcnow().replace(hour=0, minute=0, second=0),
                EndTime=datetime.utcnow(),
                Period=3600,
                Statistics=['Average']
            )
            
            return {
                'accuracy_metrics': response.get('Datapoints', []),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"CloudWatch metrics retrieval failed: {e}")
            return {}
    
    def deploy_model_to_sagemaker(self, model_path: str, model_name: str) -> Optional[str]:
        """Deploy trained model to SageMaker endpoint"""
        if not self.sagemaker_client:
            return None
        
        try:
            # This would typically involve:
            # 1. Creating a SageMaker model
            # 2. Creating an endpoint configuration
            # 3. Creating an endpoint
            
            # Simplified example - in practice, this would be more complex
            endpoint_name = f"trustify-{model_name}-{int(datetime.utcnow().timestamp())}"
            
            logger.info(f"Model deployment initiated: {endpoint_name}")
            return endpoint_name
            
        except Exception as e:
            logger.error(f"SageMaker deployment failed: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get AWS integration status"""
        return {
            'region': self.region,
            's3_available': self.s3_client is not None,
            'cloudwatch_available': self.cloudwatch_client is not None,
            'sagemaker_available': self.sagemaker_client is not None,
            'bucket_name': self.s3_bucket,
            'log_group': self.cloudwatch_log_group
        }
    
    def create_deployment_package(self) -> Dict[str, str]:
        """Create deployment configuration for AWS"""
        return {
            'cloudformation_template': self._generate_cloudformation_template(),
            'docker_file': self._generate_dockerfile(),
            'requirements': self._generate_requirements(),
            'deployment_script': self._generate_deployment_script()
        }
    
    def _generate_cloudformation_template(self) -> str:
        """Generate CloudFormation template for AWS deployment"""
        return '''
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Trustify AI - Full Stack Deployment'

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]

Resources:
  # VPC and Networking
  TrustifyVPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub 'trustify-vpc-${Environment}'

  # RDS PostgreSQL Database
  TrustifyDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub 'trustify-db-${Environment}'
      DBInstanceClass: db.t3.micro
      Engine: postgres
      EngineVersion: '13.7'
      AllocatedStorage: 20
      StorageType: gp2
      DBName: trustify_ai
      MasterUsername: postgres
      MasterUserPassword: !Ref DatabasePassword
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      BackupRetentionPeriod: 7
      MultiAZ: false
      PubliclyAccessible: false

  # Elastic Beanstalk Application
  TrustifyApplication:
    Type: AWS::ElasticBeanstalk::Application
    Properties:
      ApplicationName: !Sub 'trustify-ai-${Environment}'
      Description: 'Trustify AI Fake News Detection System'

  # S3 Bucket for Static Assets
  TrustifyS3Bucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub 'trustify-ai-assets-${Environment}'
      PublicReadPolicy: true
      WebsiteConfiguration:
        IndexDocument: index.html
        ErrorDocument: error.html

  # CloudFront Distribution
  TrustifyCloudFront:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Origins:
          - DomainName: !GetAtt TrustifyS3Bucket.DomainName
            Id: S3Origin
            S3OriginConfig:
              OriginAccessIdentity: ''
        Enabled: true
        DefaultRootObject: index.html
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          Compress: true
          CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad

Parameters:
  DatabasePassword:
    Type: String
    NoEcho: true
    Description: 'Password for RDS PostgreSQL database'
    MinLength: 8

Outputs:
  DatabaseEndpoint:
    Description: 'RDS PostgreSQL endpoint'
    Value: !GetAtt TrustifyDatabase.Endpoint.Address
    Export:
      Name: !Sub '${AWS::StackName}-DatabaseEndpoint'
      
  S3BucketName:
    Description: 'S3 bucket for static assets'
    Value: !Ref TrustifyS3Bucket
    Export:
      Name: !Sub '${AWS::StackName}-S3Bucket'
      
  CloudFrontURL:
    Description: 'CloudFront distribution URL'
    Value: !GetAtt TrustifyCloudFront.DomainName
    Export:
      Name: !Sub '${AWS::StackName}-CloudFrontURL'
        '''
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile for containerized deployment"""
        return '''
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/api/health || exit 1

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "enhanced_app:app"]
        '''
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt for deployment"""
        return '''
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
requests==2.31.0
beautifulsoup4==4.12.2
scikit-learn==1.3.0
nltk==3.8.1
transformers==4.33.2
torch==2.0.1
fuzzywuzzy==0.18.0
python-Levenshtein==0.21.1
feedparser==6.0.10
psycopg2-binary==2.9.7
boto3==1.28.57
gunicorn==21.2.0
        '''
    
    def _generate_deployment_script(self) -> str:
        """Generate deployment script"""
        return '''#!/bin/bash

# Trustify AI Deployment Script

set -e

echo "🚀 Starting Trustify AI deployment..."

# Set variables
STACK_NAME="trustify-ai-production"
REGION="us-east-1"
S3_BUCKET="trustify-ai-deployment-$(date +%s)"

# Create S3 bucket for deployment artifacts
echo "📦 Creating deployment bucket..."
aws s3 mb s3://$S3_BUCKET --region $REGION

# Package and upload CloudFormation template
echo "☁️ Deploying CloudFormation stack..."
aws cloudformation deploy \\
    --template-file cloudformation.yaml \\
    --stack-name $STACK_NAME \\
    --parameter-overrides Environment=production \\
    --capabilities CAPABILITY_IAM \\
    --region $REGION

# Build and push Docker image
echo "🐳 Building Docker image..."
docker build -t trustify-ai:latest .

# Deploy to Elastic Beanstalk
echo "🚀 Deploying to Elastic Beanstalk..."
eb init trustify-ai --region $REGION --platform "Docker"
eb create production --instance-type t3.medium

# Upload static assets to S3
echo "📁 Uploading static assets..."
aws s3 sync frontend/static/ s3://$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' --output text)/ --delete

echo "✅ Deployment completed successfully!"
echo "🌐 Application URL: $(eb status | grep CNAME | awk '{print $2}')"
        '''