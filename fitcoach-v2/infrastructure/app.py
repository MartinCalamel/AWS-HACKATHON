#!/usr/bin/env python3
"""CDK App entry point for FitCoach AI V2."""
import aws_cdk as cdk
from stacks.fitcoach_stack import FitCoachV2Stack

app = cdk.App()

env = app.node.try_get_context("env") or "dev"

FitCoachV2Stack(
    app,
    f"FitCoachV2-{env}",
    env=cdk.Environment(region="us-east-1"),
    stage=env,
)

app.synth()
