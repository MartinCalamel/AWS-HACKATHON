"""
Stack CDK principal pour FitCoach AI.
Suit exactement l'architecture.drawio :

- Amazon Cognito (User Pool fitcoach-users)
- API Gateway REST (CORS enabled)
  - POST /analyze-pose → fitcoach-pose-analysis (512MB, 30s, MediaPipe)
  - POST /generate-planning → fitcoach-planning (256MB, 30s, Bedrock)
  - POST /get-advice → fitcoach-advice (256MB, 30s, Bedrock)
- DynamoDB
  - fitcoach-plannings (PK: userId, SK: createdAt)
  - fitcoach-sessions (PK: userId, SK: sessionId)
- Amazon Bedrock (Claude 3 Haiku)
- IAM Roles (bedrock:InvokeModel, dynamodb:Read/Write)
"""
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_cognito as cognito,
)
from constructs import Construct
import os


class FitCoachStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ===== Amazon Cognito - User Pool fitcoach-users =====
        user_pool = cognito.UserPool(
            self, "FitCoachUserPool",
            user_pool_name="fitcoach-users",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        user_pool_client = cognito.UserPoolClient(
            self, "FitCoachClient",
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
        )

        # ===== Amazon DynamoDB =====
        # Table fitcoach-plannings (PK: userId, SK: createdAt) PAY_PER_REQUEST
        planning_table = dynamodb.Table(
            self, "PlanningTable",
            table_name="fitcoach-plannings",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="createdAt", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Table fitcoach-sessions (PK: userId, SK: sessionId) PAY_PER_REQUEST
        sessions_table = dynamodb.Table(
            self, "SessionsTable",
            table_name="fitcoach-sessions",
            partition_key=dynamodb.Attribute(
                name="userId", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sessionId", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # ===== Lambda - fitcoach-pose-analysis =====
        # 512 MB | 30s timeout | MediaPipe Pose
        # Uses Docker container to include MediaPipe native dependencies
        pose_lambda = _lambda.DockerImageFunction(
            self, "PoseAnalysisLambda",
            function_name="fitcoach-pose-analysis",
            code=_lambda.DockerImageCode.from_image_asset(
                os.path.join(os.path.dirname(__file__), "..", "..", "backend", "pose_analysis")
            ),
            timeout=Duration.seconds(30),
            memory_size=512,
        )

        # fitcoach-pose-analysis writes to fitcoach-sessions
        sessions_table.grant_read_write_data(pose_lambda)

        # ===== Lambda - fitcoach-planning =====
        # 256 MB | 30s timeout | Bedrock Claude
        planning_lambda = _lambda.Function(
            self, "PlanningLambda",
            function_name="fitcoach-planning",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "..", "..", "backend", "planning")
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
        )

        # fitcoach-planning: bedrock:InvokeModel + dynamodb Read/Write
        planning_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],
            )
        )
        planning_table.grant_read_write_data(planning_lambda)

        # ===== Lambda - fitcoach-advice =====
        # 256 MB | 30s timeout | Bedrock Claude
        advice_lambda = _lambda.Function(
            self, "AdviceLambda",
            function_name="fitcoach-advice",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "..", "..", "backend", "advice")
            ),
            timeout=Duration.seconds(30),
            memory_size=256,
        )

        # fitcoach-advice: bedrock:InvokeModel
        advice_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],
            )
        )

        # ===== Amazon API Gateway - REST API, CORS enabled =====
        api = apigw.RestApi(
            self, "FitCoachAPI",
            rest_api_name="FitCoach AI API",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # POST /analyze-pose → fitcoach-pose-analysis
        analyze_resource = api.root.add_resource("analyze-pose")
        analyze_resource.add_method(
            "POST",
            apigw.LambdaIntegration(pose_lambda),
        )

        # POST /generate-planning → fitcoach-planning
        planning_resource = api.root.add_resource("generate-planning")
        planning_resource.add_method(
            "POST",
            apigw.LambdaIntegration(planning_lambda),
        )

        # POST /get-advice → fitcoach-advice
        advice_resource = api.root.add_resource("get-advice")
        advice_resource.add_method(
            "POST",
            apigw.LambdaIntegration(advice_lambda),
        )

        # ===== Outputs =====
        CfnOutput(self, "ApiUrl",
                  value=api.url,
                  description="URL de l'API Gateway")
        CfnOutput(self, "UserPoolId",
                  value=user_pool.user_pool_id,
                  description="Cognito User Pool ID")
        CfnOutput(self, "UserPoolClientId",
                  value=user_pool_client.user_pool_client_id,
                  description="Cognito User Pool Client ID")
