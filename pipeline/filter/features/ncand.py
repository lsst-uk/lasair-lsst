from FeatureInterface import FeatureInterface
#from lasair.apps.object import mjd_now

class ncand(FeatureInterface):
  """Number of daiSource in light curve"""

  @classmethod
  def run(cls, alert) -> dict:
    # do something
    n = 1
    return {
      "ncand": n
    }

  def _get_schema(self) -> dict:
    schema = [{
      "name": "ncand",
      "type": "int"
    },{
      "name": "ncand_7",
      "type": "int"
    }]
    return schema

  def _run(self, alert) -> dict:
    taiList = [diaSource['midPointTai'] for diaSource in alert['diaSourceList']]
    taiNow = mjd_now()
    ncand_7 = 0
    for tai in taiList:
        if tai > taiNow -7:
            ncand_7 += 1
    return {
        "ncand": len(taiList), 
        "taimax": ncand_7,
    }
