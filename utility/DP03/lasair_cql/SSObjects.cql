CREATE TABLE IF NOT EXISTS SSObjects(
ssObjectId bigint,
discoverySubmissionDate double,
firstObservationDate double,
arc float,
numObs int,
MOID float,
MOIDTrueAnomaly float,
MOIDEclipticLongitude float,
MOIDDeltaV float,
u_H float,
u_G12 float,
u_HErr float,
u_G12Err float,
u_H_uG12_Cov float,
u_Chi2 float,
u_Ndata int,
g_H float,
g_G12 float,
g_HErr float,
g_G12Err float,
g_H_gG12_Cov float,
g_Chi2 float,
g_Ndata int,
r_H float,
r_G12 float,
r_HErr float,
r_G12Err float,
r_H_rG12_Cov float,
r_Chi2 float,
r_Ndata int,
i_H float,
i_G12 float,
i_HErr float,
i_G12Err float,
i_H_iG12_Cov float,
i_Chi2 float,
i_Ndata int,
z_H float,
z_G12 float,
z_HErr float,
z_G12Err float,
z_H_zG12_Cov float,
z_Chi2 float,
z_Ndata int,
y_H float,
y_G12 float,
y_HErr float,
y_G12Err float,
y_H_yG12_Cov float,
y_Chi2 float,
y_Ndata int,
maxExtendedness float,
minExtendedness float,
medianExtendedness float,
flags bigint,
PRIMARY KEY (ssObjectId)
)
