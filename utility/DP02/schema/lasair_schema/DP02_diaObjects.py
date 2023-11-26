schema = {
  "name": "DP02_DiaObjects",
  "fields": [
    {
      "name": "decl",
      "type": "double",
      "doc": "Mean Declination of DIASources in the diaObject"
    },
    {
      "name": "diaObjectId",
      "type": "long",
      "doc": "Unique id."
    },
    {
      "name": "gPSFluxChi2",
      "type": "double",
      "doc": "Chi^2 statistic for the scatter of gPSFlux around gPSFluxMean"
    },
    {
      "name": "gPSFluxErrMean",
      "type": "double",
      "doc": "Mean of the diaSource PSF flux errors"
    },
    {
      "name": "gPSFluxLinearIntercept",
      "type": "double",
      "doc": "y-intercept of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "gPSFluxLinearSlope",
      "type": "double",
      "doc": "Slope of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "gPSFluxMAD",
      "type": "double",
      "doc": "Median absolute deviation of diaSource PSF flux. Does not include scale factor for comparison to sigma"
    },
    {
      "name": "gPSFluxMax",
      "type": "double",
      "doc": "Maximum diaSource PSF flux"
    },
    {
      "name": "gPSFluxMaxSlope",
      "type": "double",
      "doc": "Maximum ratio of time ordered deltaFlux / deltaTime"
    },
    {
      "name": "gPSFluxMean",
      "type": "double",
      "doc": "Weighted mean of diaSource PSF flux"
    },
    {
      "name": "gPSFluxMeanErr",
      "type": "double",
      "doc": "Standard error on the weighted mean of diaSource PSF flux"
    },
    {
      "name": "gPSFluxMin",
      "type": "double",
      "doc": "Minimum diaSource PSF flux"
    },
    {
      "name": "gPSFluxNdata",
      "type": "double",
      "doc": "The number of data points used to compute gPSFluxChi2"
    },
    {
      "name": "gPSFluxPercentile05",
      "type": "double",
      "doc": "5th percentile diaSource PSF flux"
    },
    {
      "name": "gPSFluxPercentile25",
      "type": "double",
      "doc": "10th percentile diaSource PSF flux"
    },
    {
      "name": "gPSFluxPercentile50",
      "type": "double",
      "doc": "Median diaSource PSF flux"
    },
    {
      "name": "gPSFluxPercentile75",
      "type": "double",
      "doc": "75th percentile diaSource PSF flux"
    },
    {
      "name": "gPSFluxPercentile95",
      "type": "double",
      "doc": "95th percentile diaSource PSF flux"
    },
    {
      "name": "gPSFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the distribution of gPSFlux"
    },
    {
      "name": "gPSFluxSkew",
      "type": "double",
      "doc": "Skew of diaSource PSF flux"
    },
    {
      "name": "gPSFluxStetsonJ",
      "type": "double",
      "doc": "StetsonJ statistic of diaSource PSF flux"
    },
    {
      "name": "gTOTFluxMean",
      "type": "double",
      "doc": "Weighted mean of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "gTOTFluxMeanErr",
      "type": "double",
      "doc": "Standard error on gTOTFluxMean"
    },
    {
      "name": "gTOTFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "iPSFluxChi2",
      "type": "double",
      "doc": "Chi^2 statistic for the scatter of iPSFlux around iPSFluxMean"
    },
    {
      "name": "iPSFluxErrMean",
      "type": "double",
      "doc": "Mean of the diaSource PSF flux errors"
    },
    {
      "name": "iPSFluxLinearIntercept",
      "type": "double",
      "doc": "y-intercept of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "iPSFluxLinearSlope",
      "type": "double",
      "doc": "Slope of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "iPSFluxMAD",
      "type": "double",
      "doc": "Median absolute deviation of diaSource PSF flux. Does not include scale factor for comparison to sigma"
    },
    {
      "name": "iPSFluxMax",
      "type": "double",
      "doc": "Maximum diaSource PSF flux"
    },
    {
      "name": "iPSFluxMaxSlope",
      "type": "double",
      "doc": "Maximum ratio of time ordered deltaFlux / deltaTime"
    },
    {
      "name": "iPSFluxMean",
      "type": "double",
      "doc": "Weighted mean of diaSource PSF flux"
    },
    {
      "name": "iPSFluxMeanErr",
      "type": "double",
      "doc": "Standard error on the weighted mean of diaSource PSF flux"
    },
    {
      "name": "iPSFluxMin",
      "type": "double",
      "doc": "Minimum diaSource PSF flux"
    },
    {
      "name": "iPSFluxNdata",
      "type": "double",
      "doc": "The number of data points used to compute iPSFluxChi2"
    },
    {
      "name": "iPSFluxPercentile05",
      "type": "double",
      "doc": "5th percentile diaSource PSF flux"
    },
    {
      "name": "iPSFluxPercentile25",
      "type": "double",
      "doc": "10th percentile diaSource PSF flux"
    },
    {
      "name": "iPSFluxPercentile50",
      "type": "double",
      "doc": "Median diaSource PSF flux"
    },
    {
      "name": "iPSFluxPercentile75",
      "type": "double",
      "doc": "75th percentile diaSource PSF flux"
    },
    {
      "name": "iPSFluxPercentile95",
      "type": "double",
      "doc": "95th percentile diaSource PSF flux"
    },
    {
      "name": "iPSFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the distribution of iPSFlux"
    },
    {
      "name": "iPSFluxSkew",
      "type": "double",
      "doc": "Skew of diaSource PSF flux"
    },
    {
      "name": "iPSFluxStetsonJ",
      "type": "double",
      "doc": "StetsonJ statistic of diaSource PSF flux"
    },
    {
      "name": "iTOTFluxMean",
      "type": "double",
      "doc": "Weighted mean of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "iTOTFluxMeanErr",
      "type": "double",
      "doc": "Standard error on iTOTFluxMean"
    },
    {
      "name": "iTOTFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "nDiaSources",
      "type": "long",
      "doc": "Number of diaSources associated with this diaObject"
    },
    {
      "name": "pixelId",
      "type": "double",
      "doc": "HtmIndex20 of ra, decl coordinate"
    },
    {
      "name": "rPSFluxChi2",
      "type": "double",
      "doc": "Chi^2 statistic for the scatter of rPSFlux around rPSFluxMean"
    },
    {
      "name": "rPSFluxErrMean",
      "type": "double",
      "doc": "Mean of the diaSource PSF flux errors"
    },
    {
      "name": "rPSFluxLinearIntercept",
      "type": "double",
      "doc": "y-intercept of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "rPSFluxLinearSlope",
      "type": "double",
      "doc": "Slope of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "rPSFluxMAD",
      "type": "double",
      "doc": "Median absolute deviation of diaSource PSF flux. Does not include scale factor for comparison to sigma"
    },
    {
      "name": "rPSFluxMax",
      "type": "double",
      "doc": "Maximum diaSource PSF flux"
    },
    {
      "name": "rPSFluxMaxSlope",
      "type": "double",
      "doc": "Maximum ratio of time ordered deltaFlux / deltaTime"
    },
    {
      "name": "rPSFluxMean",
      "type": "double",
      "doc": "Weighted mean of diaSource PSF flux"
    },
    {
      "name": "rPSFluxMeanErr",
      "type": "double",
      "doc": "Standard error on the weighted mean of diaSource PSF flux"
    },
    {
      "name": "rPSFluxMin",
      "type": "double",
      "doc": "Minimum diaSource PSF flux"
    },
    {
      "name": "rPSFluxNdata",
      "type": "double",
      "doc": "The number of data points used to compute rPSFluxChi2"
    },
    {
      "name": "rPSFluxPercentile05",
      "type": "double",
      "doc": "5th percentile diaSource PSF flux"
    },
    {
      "name": "rPSFluxPercentile25",
      "type": "double",
      "doc": "10th percentile diaSource PSF flux"
    },
    {
      "name": "rPSFluxPercentile50",
      "type": "double",
      "doc": "Median diaSource PSF flux"
    },
    {
      "name": "rPSFluxPercentile75",
      "type": "double",
      "doc": "75th percentile diaSource PSF flux"
    },
    {
      "name": "rPSFluxPercentile95",
      "type": "double",
      "doc": "95th percentile diaSource PSF flux"
    },
    {
      "name": "rPSFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the distribution of rPSFlux"
    },
    {
      "name": "rPSFluxSkew",
      "type": "double",
      "doc": "Skew of diaSource PSF flux"
    },
    {
      "name": "rPSFluxStetsonJ",
      "type": "double",
      "doc": "StetsonJ statistic of diaSource PSF flux"
    },
    {
      "name": "rTOTFluxMean",
      "type": "double",
      "doc": "Weighted mean of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "rTOTFluxMeanErr",
      "type": "double",
      "doc": "Standard error on rTOTFluxMean"
    },
    {
      "name": "rTOTFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "ra",
      "type": "double",
      "doc": "Mean Right Ascension of DIASources in the diaObject"
    },
    {
      "name": "radecTai",
      "type": "double",
      "doc": "Not used in DP0.2"
    },
    {
      "name": "uPSFluxChi2",
      "type": "double",
      "doc": "Chi^2 statistic for the scatter of uPSFlux around uPSFluxMean"
    },
    {
      "name": "uPSFluxErrMean",
      "type": "double",
      "doc": "Mean of the diaSource PSF flux errors"
    },
    {
      "name": "uPSFluxLinearIntercept",
      "type": "double",
      "doc": "y-intercept of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "uPSFluxLinearSlope",
      "type": "double",
      "doc": "Slope of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "uPSFluxMAD",
      "type": "double",
      "doc": "Median absolute deviation of diaSource PSF flux. Does not include scale factor for comparison to sigma"
    },
    {
      "name": "uPSFluxMax",
      "type": "double",
      "doc": "Maximum diaSource PSF flux"
    },
    {
      "name": "uPSFluxMaxSlope",
      "type": "double",
      "doc": "Maximum ratio of time ordered deltaFlux / deltaTime"
    },
    {
      "name": "uPSFluxMean",
      "type": "double",
      "doc": "Weighted mean of diaSource PSF flux"
    },
    {
      "name": "uPSFluxMeanErr",
      "type": "double",
      "doc": "Standard error on the weighted mean of diaSource PSF flux"
    },
    {
      "name": "uPSFluxMin",
      "type": "double",
      "doc": "Minimum diaSource PSF flux"
    },
    {
      "name": "uPSFluxNdata",
      "type": "double",
      "doc": "The number of data points used to compute uPSFluxChi2"
    },
    {
      "name": "uPSFluxPercentile05",
      "type": "double",
      "doc": "5th percentile diaSource PSF flux"
    },
    {
      "name": "uPSFluxPercentile25",
      "type": "double",
      "doc": "10th percentile diaSource PSF flux"
    },
    {
      "name": "uPSFluxPercentile50",
      "type": "double",
      "doc": "Median diaSource PSF flux"
    },
    {
      "name": "uPSFluxPercentile75",
      "type": "double",
      "doc": "75th percentile diaSource PSF flux"
    },
    {
      "name": "uPSFluxPercentile95",
      "type": "double",
      "doc": "95th percentile diaSource PSF flux"
    },
    {
      "name": "uPSFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the distribution of uPSFlux"
    },
    {
      "name": "uPSFluxSkew",
      "type": "double",
      "doc": "Skew of diaSource PSF flux"
    },
    {
      "name": "uPSFluxStetsonJ",
      "type": "double",
      "doc": "StetsonJ statistic of diaSource PSF flux"
    },
    {
      "name": "uTOTFluxMean",
      "type": "double",
      "doc": "Weighted mean of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "uTOTFluxMeanErr",
      "type": "double",
      "doc": "Standard error on uTOTFluxMean"
    },
    {
      "name": "uTOTFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "yPSFluxChi2",
      "type": "double",
      "doc": "Chi^2 statistic for the scatter of yPSFlux around yPSFluxMean"
    },
    {
      "name": "yPSFluxErrMean",
      "type": "double",
      "doc": "Mean of the diaSource PSF flux errors"
    },
    {
      "name": "yPSFluxLinearIntercept",
      "type": "double",
      "doc": "y-intercept of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "yPSFluxLinearSlope",
      "type": "double",
      "doc": "Slope of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "yPSFluxMAD",
      "type": "double",
      "doc": "Median absolute deviation of diaSource PSF flux. Does not include scale factor for comparison to sigma"
    },
    {
      "name": "yPSFluxMax",
      "type": "double",
      "doc": "Maximum diaSource PSF flux"
    },
    {
      "name": "yPSFluxMaxSlope",
      "type": "double",
      "doc": "Maximum ratio of time ordered deltaFlux / deltaTime"
    },
    {
      "name": "yPSFluxMean",
      "type": "double",
      "doc": "Weighted mean of diaSource PSF flux"
    },
    {
      "name": "yPSFluxMeanErr",
      "type": "double",
      "doc": "Standard error on the weighted mean of diaSource PSF flux"
    },
    {
      "name": "yPSFluxMin",
      "type": "double",
      "doc": "Minimum diaSource PSF flux"
    },
    {
      "name": "yPSFluxNdata",
      "type": "double",
      "doc": "The number of data points used to compute yPSFluxChi2"
    },
    {
      "name": "yPSFluxPercentile05",
      "type": "double",
      "doc": "5th percentile diaSource PSF flux"
    },
    {
      "name": "yPSFluxPercentile25",
      "type": "double",
      "doc": "10th percentile diaSource PSF flux"
    },
    {
      "name": "yPSFluxPercentile50",
      "type": "double",
      "doc": "Median diaSource PSF flux"
    },
    {
      "name": "yPSFluxPercentile75",
      "type": "double",
      "doc": "75th percentile diaSource PSF flux"
    },
    {
      "name": "yPSFluxPercentile95",
      "type": "double",
      "doc": "95th percentile diaSource PSF flux"
    },
    {
      "name": "yPSFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the distribution of yPSFlux"
    },
    {
      "name": "yPSFluxSkew",
      "type": "double",
      "doc": "Skew of diaSource PSF flux"
    },
    {
      "name": "yPSFluxStetsonJ",
      "type": "double",
      "doc": "StetsonJ statistic of diaSource PSF flux"
    },
    {
      "name": "yTOTFluxMean",
      "type": "double",
      "doc": "Weighted mean of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "yTOTFluxMeanErr",
      "type": "double",
      "doc": "Standard error on yTOTFluxMean"
    },
    {
      "name": "yTOTFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "zPSFluxChi2",
      "type": "double",
      "doc": "Chi^2 statistic for the scatter of zPSFlux around zPSFluxMean"
    },
    {
      "name": "zPSFluxErrMean",
      "type": "double",
      "doc": "Mean of the diaSource PSF flux errors"
    },
    {
      "name": "zPSFluxLinearIntercept",
      "type": "double",
      "doc": "y-intercept of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "zPSFluxLinearSlope",
      "type": "double",
      "doc": "Slope of a linear model fit to diaSource PSF flux vs time"
    },
    {
      "name": "zPSFluxMAD",
      "type": "double",
      "doc": "Median absolute deviation of diaSource PSF flux. Does not include scale factor for comparison to sigma"
    },
    {
      "name": "zPSFluxMax",
      "type": "double",
      "doc": "Maximum diaSource PSF flux"
    },
    {
      "name": "zPSFluxMaxSlope",
      "type": "double",
      "doc": "Maximum ratio of time ordered deltaFlux / deltaTime"
    },
    {
      "name": "zPSFluxMean",
      "type": "double",
      "doc": "Weighted mean of diaSource PSF flux"
    },
    {
      "name": "zPSFluxMeanErr",
      "type": "double",
      "doc": "Standard error on the weighted mean of diaSource PSF flux"
    },
    {
      "name": "zPSFluxMin",
      "type": "double",
      "doc": "Minimum diaSource PSF flux"
    },
    {
      "name": "zPSFluxNdata",
      "type": "double",
      "doc": "The number of data points used to compute zPSFluxChi2"
    },
    {
      "name": "zPSFluxPercentile05",
      "type": "double",
      "doc": "5th percentile diaSource PSF flux"
    },
    {
      "name": "zPSFluxPercentile25",
      "type": "double",
      "doc": "10th percentile diaSource PSF flux"
    },
    {
      "name": "zPSFluxPercentile50",
      "type": "double",
      "doc": "Median diaSource PSF flux"
    },
    {
      "name": "zPSFluxPercentile75",
      "type": "double",
      "doc": "75th percentile diaSource PSF flux"
    },
    {
      "name": "zPSFluxPercentile95",
      "type": "double",
      "doc": "95th percentile diaSource PSF flux"
    },
    {
      "name": "zPSFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the distribution of zPSFlux"
    },
    {
      "name": "zPSFluxSkew",
      "type": "double",
      "doc": "Skew of diaSource PSF flux"
    },
    {
      "name": "zPSFluxStetsonJ",
      "type": "double",
      "doc": "StetsonJ statistic of diaSource PSF flux"
    },
    {
      "name": "zTOTFluxMean",
      "type": "double",
      "doc": "Weighted mean of the PSF flux forced photometered at the diaSource position on the calibrated image"
    },
    {
      "name": "zTOTFluxMeanErr",
      "type": "double",
      "doc": "Standard error on zTOTFluxMean"
    },
    {
      "name": "zTOTFluxSigma",
      "type": "double",
      "doc": "Standard deviation of the PSF flux forced photometered at the diaSource position on the calibrated image"
    }
  ],
  "indexes": []
}