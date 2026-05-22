"""
Stack CDK principal pour FitCoach AI.
Déploie : API Gateway, Lambda functions, DynamoDB, Cognito.
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


class FitCoachStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ===== DynamoDB =====
        # Table pour stocker les plannings utilisateurs
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

        # Table pour l'historique des sessions
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

        # ===== Cognito =====
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

        # ===== Lambda - Analyse de posture =====
        pose_lambda = _lambda.Function(
            self, "PoseAnalysisLambda",
            function_name="fitcoach-pose-analysis",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../backend/pose_analysis"),
            timeout=Duration.seconds(30),
            memory_size=512,
        )

        # ===== Lambda - Planning =====
        planning_lambda = _lambda.Function(
            self, "PlanningLambda",
            function_name="fitcoach-planning",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../backend/planning"),
            timeout=Duration.seconds(30),
            memory_size=256,
        )

        # Permissions Bedrock pour le planning
        planning_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"],
            )
        )

        # Permissions DynamoDB
        planning_table.grant_read_write_data(planning_lambda)
        sessions_table.grant_read_write_data(pose_lambda)

        # ===== Lambda - Conseils =====
        advice_lambda = _lambda.Function(
            self, "AdviceLambda",
            function_name="fitcoach-advice",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../backend/advice"),
            timeout=Duration.seconds(30),
            memory_size=256,
        )

        advice_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"],
            )
        )

        # ===== API Gateway =====
        api = apigw.RestApi(
            self, "FitCoachAPI",
            rest_api_name="FitCoach AI API",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
        )

        # Routes
        analyze = api.root.add_resource("analyze-pose")
        analyze.add_method("POST", apigw.LambdaIntegration(pose_lambda))

        planning = api.root.add_resource("generate-planning")
        planning.add_method("POST", apigw.LambdaIntegration(planning_lambda))

        advice = api.root.add_resource("get-advice")
        advice.add_method("POST", apigw.LambdaIntegration(advice_lambda))

        # ===== Outputs =====
        CfnOutput(self, "ApiUrl", value=api.url, description="URL de l'API")
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
