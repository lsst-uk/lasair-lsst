class FeatureInterface:
  """Interface used by feature processors"""

  def get_info(self) -> str:
    """Get a string with information about the schema"""
    return(__doc__)

  def get_schema(self) -> dict:
    """Get the schema for the feature output"""
    pass

  def run(self, alert) -> dict:
    """Generate the feature for the given alert"""
    pass

