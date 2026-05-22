#!/usr/bin/env python3
"""CDK App entry point pour FitCoach AI."""
import aws_cdk as cdk
from stacks.fitcoach_stack import FitCoachStack

app = cdk.App()
FitCoachStack(
    app,
    "FitCoachAIStack",
    env=cdk.Environment(region="us-east-1"),
)
app.synth()
