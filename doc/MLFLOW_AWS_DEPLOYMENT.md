# ☁️ MLflow em Produção na AWS

## Visão Geral: Local vs AWS

```mermaid
graph TB
    subgraph LocalDev["LOCAL (Desenvolvimento)"]
        NB["📓 Notebook<br/>mlflow.start_run()"]
        MLLocal["🎛️ MLflow Server<br/>localhost:5000"]
        SQLite["💾 SQLite<br/>mlflow.db"]
        FSArtifacts["📦 Artifacts<br/>./mlruns/"]
        APILocal["🚀 API<br/>localhost:8000"]
    end
    
    subgraph AWS["AWS PRODUCTION (us-east-2)"]
        ALB["⚖️ Application<br/>Load Balancer<br/>:80, :5000"]
        
        subgraph ECS["🐳 ECS Fargate"]
            APIEcs["🚀 API FastAPI<br/>(container)"]
            MLEcs["🎛️ MLflow Server<br/>(container)"]
        end
        
        RDS["🐘 RDS PostgreSQL<br/>backend_store"]
        S3["🪣 S3 Bucket<br/>artifact_store"]
        DynamoDB["🗄️ DynamoDB<br/>bandit state"]
        Secrets["🔐 Secrets Manager<br/>credentials"]
        CW["📊 CloudWatch<br/>logs & metrics"]
    end
    
    NB -->|mesmo código!| MLLocal
    MLLocal --> SQLite
    MLLocal --> FSArtifacts
    APILocal --> MLLocal
    
    ALB --> APIEcs
    ALB --> MLEcs
    APIEcs --> DynamoDB
    APIEcs --> MLEcs
    MLEcs --> RDS
    MLEcs --> S3
    MLEcs -.-> Secrets
    APIEcs -.-> CW
    
    style LocalDev fill:#fff9c4
    style AWS fill:#c8e6c9
    style ECS fill:#b3e5fc
    style RDS fill:#f8bbd0
    style S3 fill:#d1c4e9
