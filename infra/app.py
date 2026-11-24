import aws_cdk as cdk

from story_stack import StoryStack

app = cdk.App()
StoryStack(app, "StoryGeneratorStack")
app.synth()
