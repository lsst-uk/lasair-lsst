## Scientific goals of Lasair
We aim to facilitate all four science themes of LSST within the Lasair 
platform: Dark Matter and Dark Energy, the Solar System, the Changing Sky, and 
the Milky Way. We will do this by providing combined access to the alerts, to 
the annual data releases, and to external data sources, and by providing a 
flexible platform which users can adapt to their own ends.
Below we explore the issues arising from key science topics.

### Extragalactic Transients
Luminous transients outside our own galaxy include supernovae, kilonovae, tidal 
disruption events and AGN flare activity, nuclear transients of unknown origin, 
gamma-ray bursts, stellar mergers, white dwarf - NS/BH mergers, super-luminous 
supernovae and fast blue optical transients. 
These have timescales from hours (GRB afterglows), days (kilonovae and WD-NS/BH 
mergers), to weeks (supernovae, fast blue optical transients), months (TDEs, 
SLSNe, AGN activity) to years (SLSNe at high redshift, AGN and nuclear 
transients, SNe from CSM interaction). 
All of this science requires lightcurves, links to galaxy and redshift 
catalogues, precise astrometric cross-matching, correlation with high energy 
information, multiwavelength cross-matching and our concept of ``tagging'' 
which we introduce here. Objects need to be found on timescales of minutes to 
years due to the intrinsic timescale, which is mostly driven by the mass 
ejected by the transients (through photon diffusion time).  Some scientific 
highlights that Lasair will enable are : 

### Kilonovae and gravitational wave sources
Users will be able to select their own candidates by combining colour, 
lightcurve evolution, host galaxy information and any multi-wavelength 
coincidences using SQL, kafka filtering, or the Lasair API. 
This can be used to enable searches for all ``fast-transients'' of timescales 
of minutes to days (e.g. GRB afterglows, orphan afterglows, WD-NS/BH mergers).  

### Massive samples of supernovae 
Lasair will link all transients to a list of likely host galaxies together with 
their photometric redshifts and their spectroscopic redshifts, should they 
exist. We are working closely with the two major ESO projects that will provide 
tens of thousands of spectra for LSST supernovae. 
We will coordinate SN discoveries in Lasair with spectra from the 4MOST 
multi-fibre spectrometer on the ESO VISTA telescope. 
We will provide DESC with the ability to select 35,000 live transients for 
spectra and obtain spectra of 70,000 host galaxies in the TiDES (Time Domain 
Extragalactic Survey). 
This will provide the largest cosmological sample of type Ia SNe, together 
with a massive statistical sample to understand supernova explosion physics 
across a range of redshifts and host galaxy masses and metallicities. Lasair 
will provide both (reproducible) selection and extract the scientific content 
(type, phase, redshift etc) to re-ingest into the broker for user exploitation. 
We are also working closely with the UK team responsible for the science 
software infrastructure behind SOXS on ESO's New Technology Telescope.  This is 
a 0.35-2$\mu$m spectrometer and ESO are fully dedicating the NTT to time domain 
science, with the schedule being run by the SOXS consortium. 
We will enable the SOXS marshall and rapid data analysis pipeline to interface 
with Lasair, to select LSST transients ($\sim$ few$\times10^{3}$) for 
classification and re-ingest the information and public data for all users to 
access. 

### AGN, TDEs and long lived transients
Similar to the above, we will allow users to select known AGN, upload their own 
AGN catalogues, and select flaring events in both active and passive galaxies. 
This will support the science of tidal disruption events, changing look 
quasars, AGN flares, microlensing of background QSOs by foreground galaxies, 
and unusual long lived nuclear transients. Lasair will match radio and X-ray 
archival data with optical spectra, and the LSST lightcurves. Users will be 
able to select on these criteria or upload their own watch list to Lasair to 
combine with lightcurve parameters. 

### Milky Way and Local Group stellar transients
Within the TVS Science Collaboration most science for variables (typically 
recurrent and periodic signals) will be achieved with the annual data releases. 
However there is great opportunity in combining alerts with the data releases. 
Users can discover outbursts or large amplitude variability through the alerts 
and link to the data releases and full multi-year lightcurves. Lasair-ZTF 
currently can provide streams of objects matched to known stars (via watch 
lists of $10^6$ objects) and trigger on a particular magnitude variability 
index. We are working with scientists within TVS in particular to define 
features that can be measured on the incoming stream and used to provide 
alerts.  For example, outbursts of AM CVn stars 
which are then linked to the binary system's long term lightcurve 
Lasair-LSST will expand on its current functionality to provide 
seamless cross-links to the data releases within the UK IDAC infrastructure. 

### Solar System objects
LSST will provide an unprecedented opportunity for time-domain Solar System 
science.

### New types of transient
In the future, we can expect surprises. The Lasair community has  active groups 
dedicated to finding and following rare events such as superluminous 
supernovae, tidal disruption events, compact stellar mergers and black-hole 
forming supernovae.  
In the future we expect further exotica to emerge, and it is the flexibility of 
Lasair's design which will allow relevant information to be streamed in, joint 
queries to be built and executed in real time, and follow-up facilities alerted 
and activated.
