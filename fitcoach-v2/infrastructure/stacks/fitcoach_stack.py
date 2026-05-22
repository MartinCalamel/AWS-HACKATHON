"""
FitCoach AI V2 — CDK Stack complet.
Déploie : DynamoDB (7 tables), Cognito, Lambda (agents + pose), API Gateway, S3, CloudFront.
"""
from aws_cdk import (
    Stack, Duration, RemovalPolicy, CfnOutput,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class FitCoachV2Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, stage: str = "dev", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        prefix = f"fitcoach-{stage}"

        # ===== DynamoDB Tables =====
        tables = {}
        table_configs = [
            ("users", "userId", "PROFILE", None),
            ("programs", "userId", "programId", None),
            ("sessions", "userId", "sessionId", None),
            ("performance", "userId", "exerciseDate", None),
            ("calendar", "userId", "date", None),
            ("achievements", "userId", "badgeId", None),
            ("leaderboard", "weekKey", "score", dynamodb.AttributeType.NUMBER),
        ]

        for name, pk, sk, sk_type in table_configs:
            tables[name] = dynamodb.Table(
                self, f"{name.capitalize()}Table",
                table_name=f"{prefix}-{name}",
                partition_key=dynamodb.Attribute(
                    name=pk, type=dynamodb.AttributeType.STRING
                ),
                sort_key=dynamodb.Attribute(
                    name=sk,
                    type=sk_type if sk_type else dynamodb.AttributeType.STRING,
                ),
                billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                removal_policy=RemovalPolicy.DESTROY,
            )

        # ===== Cognito =====
        user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name=f"{prefix}-users",
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
            self, "UserPoolClient",
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(user_password=True, user_srp=True),
        )

        # ===== Lambda Environment =====
        lambda_env = {
            "STAGE": stage,
            "USERS_TABLE": tables["users"].table_name,
            "PROGRAMS_TABLE": tables["programs"].table_name,
            "SESSIONS_TABLE": tables["sessions"].table_name,
            "PERFORMANCE_TABLE": tables["performance"].table_name,
            "CALENDAR_TABLE": tables["calendar"].table_name,
            "ACHIEVEMENTS_TABLE": tables["achievements"].table_name,
            "LEADERBOARD_TABLE": tables["leaderboard"].table_name,
            "BEDROCK_MODEL_ID": "anthropic.claude-3-haiku-20240307-v1:0",
        }

        # ===== Lambda — Master Agent =====
        master_lambda = _lambda.Function(
            self, "MasterAgentLambda",
            function_name=f"{prefix}-master-agent",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="agents.master_agent.handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment=lambda_env,
        )

        # ===== Lambda — Pose Analysis =====
        pose_lambda = _lambda.Function(
            self, "PoseAnalysisLambda",
            function_name=f"{prefix}-pose-analysis",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="pose_analysis.handler.handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment=lambda_env,
        )

        # ===== IAM Permissions =====
        bedrock_policy = iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["arn:aws:bedrock:us-east-1::foundation-model/*"],
        )
        master_lambda.add_to_role_policy(bedrock_policy)

        for table in tables.values():
            table.grant_read_write_data(master_lambda)
            table.grant_read_write_data(pose_lambda)

        # ===== API Gateway =====
        api = apigw.RestApi(
            self, "FitCoachAPI",
            rest_api_name=f"FitCoach AI V2 ({stage})",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
        )

        # Cognito Authorizer
        authorizer = apigw.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
        )

        # Routes
        agent_resource = api.root.add_resource("agent")
        agent_ask = agent_resource.add_resource("ask")
        agent_ask.add_method("POST", apigw.LambdaIntegration(master_lambda))

        pose_resource = api.root.add_resource("pose")
        pose_analyze = pose_resource.add_resource("analyze")
        pose_analyze.add_method("POST", apigw.LambdaIntegration(pose_lambda))

        # Program routes
        program_resource = api.root.add_resource("program")
        program_resource.add_method("POST", apigw.LambdaIntegration(master_lambda))
        program_resource.add_method("GET", apigw.LambdaIntegration(master_lambda))

        # Calendar routes
        calendar_resource = api.root.add_resource("calendar")
        calendar_resource.add_method("GET", apigw.LambdaIntegration(master_lambda))
        calendar_resource.add_method("PUT", apigw.LambdaIntegration(master_lambda))

        # Performance routes
        performance_resource = api.root.add_resource("performance")
        performance_resource.add_method("GET", apigw.LambdaIntegration(master_lambda))
        performance_resource.add_method("POST", apigw.LambdaIntegration(master_lambda))

        # Achievements routes
        achievements_resource = api.root.add_resource("achievements")
        achievements_resource.add_method("GET", apigw.LambdaIntegration(master_lambda))

        # Leaderboard
        leaderboard_resource = api.root.add_resource("leaderboard")
        leaderboard_resource.add_method("GET", apigw.LambdaIntegration(master_lambda))

        # Rest
        rest_resource = api.root.add_resource("rest")
        rest_resource.add_method("GET", apigw.LambdaIntegration(master_lambda))

        # ===== S3 + CloudFront (Frontend) =====
        frontend_bucket = s3.Bucket(
            self, "FrontendBucket",
            bucket_name=f"{prefix}-frontend",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        distribution = cloudfront.Distribution(
            self, "FrontendCDN",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(frontend_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_page_path="/index.html",
                    response_http_status=200,
                ),
            ],
        )

        # ===== Outputs =====
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
        CfnOutput(self, "FrontendBucket", value=frontend_bucket.bucket_name)
        CfnOutput(self, "CloudFrontUrl", value=f"https://{distribution.distribution_domain_name}")
