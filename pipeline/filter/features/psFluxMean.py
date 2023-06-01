from features.FeatureGroup import FeatureGroup

class psFluxMean(FeatureGroup):
  """Mean flux in nJansky in all filters"""

  _features = [
    "uPSFluxMean",
    "gPSFluxMean",
    "rPSFluxMean",
    "iPSFluxMean",
    "zPSFluxMean",
    "yPSFluxMean",
  ]

  def run(self):
    """Return mean flux in nJansky in all filters"""

    # copy the values from the alert
    output = {}
    object = self.alert.get("diaObject")
    for f in self._features:
      output[f] = object.get(f)
    return output

