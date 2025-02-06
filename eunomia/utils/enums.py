from enum import Enum


class RetrievalStage(Enum):
    """
    Defines when an instrument should be executed in the retrieval pipeline.
    It can be either before or after the retrieval step.
    """

    PRE = "pre"
    POST = "post"
