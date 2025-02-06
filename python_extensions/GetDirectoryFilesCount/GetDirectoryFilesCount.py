import os
import re
from nifiapi.flowfiletransform import FlowFileTransform, FlowFileTransformResult
from nifiapi.properties import PropertyDescriptor, StandardValidators, ExpressionLanguageScope
from nifiapi.relationship import Relationship


class DirectoryFileCountError(Exception):
    """Raised when there is an error counting files in the directory."""
    pass


class GetDirectoryFilesCount(FlowFileTransform):
    class Java:
        implements = ['org.apache.nifi.python.processor.FlowFileTransform']

    class ProcessorDetails:
        version = '2.1.0'
        dependencies = []
        description = """A processor that counts the files in a given directory and stores the count in a specified attribute."""
        tags = ["file count", "directory", "file filter"]

    DIRECTORY_PATH = PropertyDescriptor(
        name="Directory Path",
        description="The path to the directory to count files in.",
        required=True,
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        expression_language_scope=ExpressionLanguageScope.NONE
    )

    FILE_FILTER = PropertyDescriptor(
        name="File Filter",
        description="Regular expression to filter files to count. Leave blank to count all files.",
        required=True, 
        validators=[StandardValidators.NON_EMPTY_VALIDATOR],
        expression_language_scope=ExpressionLanguageScope.NONE,
        default_value=r"[^\.].*"
    )

    property_descriptors = [
        DIRECTORY_PATH,
        FILE_FILTER
    ]

    REL_SUCCESS = Relationship(name="success", description="FlowFiles that were successfully processed")
    REL_FAILURE = Relationship(name="failure", description="FlowFiles that failed to be processed")
    REL_FOUND = Relationship(name="not.found", description="FlowFiles that not found")
    REL_EXISTS = Relationship(name="not.exists", description="FlowFiles that not exists")


    def __init__(self, **kwargs):
        super().__init__()

    def getPropertyDescriptors(self):
        return self.property_descriptors

    def getRelationships(self):
        return [self.REL_SUCCESS, self.REL_FAILURE, self.REL_FOUND, self.REL_EXISTS]

    def transform(self, context, flowfile):
        directory_path = context.getProperty(self.DIRECTORY_PATH).evaluateAttributeExpressions(flowfile).getValue()
        file_filter_regex = context.getProperty(self.FILE_FILTER).evaluateAttributeExpressions(flowfile).getValue()

        if not os.path.isdir(directory_path):
            return FlowFileTransformResult(relationship='not.exists')

        try:
            regex = re.compile(file_filter_regex)
            files = [entry for entry in os.listdir(directory_path) 
                     if os.path.isfile(os.path.join(directory_path, entry)) and regex.match(entry)]
            file_count = len(files)

        except Exception as e:
            raise DirectoryFileCountError(f"An error occurred while counting files in '{directory_path}': {str(e)}")

        if file_count == 0:
            return FlowFileTransformResult(relationship='not.found', attributes={'files.count': "0"})
        
        return FlowFileTransformResult(relationship='success', attributes={'files.count': str(file_count)})