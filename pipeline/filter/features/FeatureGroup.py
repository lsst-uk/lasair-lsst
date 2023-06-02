import sys
from importlib import import_module
sys.path.append("../../../common/schema/lasair_schema")
from objects import schema as objectSchema
import features

class FeatureGroup:
    """FeatureGroups are collections of related features that are
         computed at the same time. This is an abstract class, feature
         groups should provide a list of features and implement the
         run method."""

    _features = []

    def __init__(self, alert):
        self.alert = alert

    def run(self) -> dict:
        """Run the alert processing to generate the features."""
        return {}     

    # The run_all utility method is probably how you usually want to
    # call this class, e.g.
    #
    # from features.FeatureGroup import FeatureGroup
    # output = FeatureGroup.run_all(alert)

    @classmethod
    def run_all(cls, alert):
        """Utility method to run all known feature groups on an alert and
             collate the output."""
        output = {}
        for group in features.__all__:
            import_module(f"features.{group}")
            groupModule = getattr(features, group)
            groupClass = getattr(groupModule, group)
            groupInst = groupClass(alert)
            output.update(groupInst.run())
        return output

    # The following are reasonable default implementations and probably
    # don't normally need to be overridden.

    @classmethod
    def get_features(cls) -> list:
        """Get a list of features implemented by this group."""
        return cls._features

    @classmethod
    def get_info(cls) -> dict:
        """Get a dict with descriptions for the features in this group."""
        # Default implementation builds a description from the schema.
        info = {}
        schema = cls.get_schema()
        for feature in cls.get_features():
            # use the "doc" entry from the schema if it exists, else empty string
            info[feature] = schema[feature].get("doc", "")
        return info

    @classmethod
    def get_schema(cls) -> dict:
        """Get the schema for this feature group"""
        # Default implementation builds our schema from the main schema.
        schema = {}
        our_features = cls.get_features()
        for feature in objectSchema['fields']:
            name = feature['name']
            if name in our_features:
                schema[name] = feature
                # replace any non-python types with equivalents
                if schema[name]['type'] == "double":
                    schema[name]['type'] = "float"
                elif schema[name]['type'] == "long":
                    schema[name]['type'] = "int"
        return schema

