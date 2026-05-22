"""
Stack CDK principal pour FitCoach AI.
Déploie : API Gateway, Lambda functions, DynamoDB, S3 + CloudFront (frontend).
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
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class FitCoachStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ===== DynamoDB =====
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

        # ===== Lambda - Analyse de posture (Bedrock Vision) =====
        pose_lambda = _lambda.Function(
            self, "PoseAnalysisLambda",
            function_name="fitcoach-pose-analysis",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../backend/pose_analysis"),
            timeout=Duration.seconds(60),
            memory_size=256,
        )

        # Permission Bedrock pour l'analyse de posture (Claude Vision)
        pose_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],
            )
        )

        # Permission Rekognition (fallback)
        pose_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["rekognition:DetectFaces", "rekognition:DetectLabels"],
                resources=["*"],
            )
        )

        sessions_table.grant_read_write_data(pose_lambda)

        # ===== Lambda - Planning (Bedrock) =====
        planning_lambda = _lambda.Function(
            self, "PlanningLambda",
            function_name="fitcoach-planning",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../backend/planning"),
            timeout=Duration.seconds(60),
            memory_size=256,
        )

        planning_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],
            )
        )

        planning_table.grant_read_write_data(planning_lambda)

        # ===== Lambda - Conseils (Bedrock) =====
        advice_lambda = _lambda.Function(
            self, "AdviceLambda",
            function_name="fitcoach-advice",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../backend/advice"),
            timeout=Duration.seconds(60),
            memory_size=256,
        )

        advice_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],
            )
        )

        # ===== API Gateway =====
        api = apigw.RestApi(
            self, "FitCoachAPI",
            rest_api_name="FitCoach AI API",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
            binary_media_types=["*/*"],
        )

        # Routes
        analyze = api.root.add_resource("analyze-pose")
        analyze.add_method("POST", apigw.LambdaIntegration(pose_lambda))

        planning = api.root.add_resource("generate-planning")
        planning.add_method("POST", apigw.LambdaIntegration(planning_lambda))

        advice = api.root.add_resource("get-advice")
        advice.add_method("POST", apigw.LambdaIntegration(advice_lambda))

        # ===== S3 Bucket pour le frontend =====
        frontend_bucket = s3.Bucket(
            self, "FrontendBucket",
            bucket_name=f"fitcoach-ai-frontend-{self.account}",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # ===== CloudFront Distribution =====
        oai = cloudfront.OriginAccessIdentity(
            self, "OAI",
            comment="FitCoach AI Frontend",
        )
        frontend_bucket.grant_read(oai)

        distribution = cloudfront.Distribution(
            self, "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    frontend_bucket,
                    origin_access_identity=oai,
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
            ],
        )

        # Déployer le frontend buildé dans S3
        s3deploy.BucketDeployment(
            self, "DeployFrontend",
            sources=[s3deploy.Source.asset("../frontend/dist")],
            destination_bucket=frontend_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        # ===== Outputs =====
        CfnOutput(self, "ApiUrl",
                  value=api.url,
                  description="URL de l'API Gateway")
        CfnOutput(self, "FrontendUrl",
                  value=f"https://{distribution.distribution_domain_name}",
                  description="URL du frontend (CloudFront)")
        CfnOutput(self, "FrontendBucketName",
                  value=frontend_bucket.bucket_name,
                  description="Nom du bucket S3 frontend")
