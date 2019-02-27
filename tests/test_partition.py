import time
import numpy as np

from geode.dispatcher import Dispatcher

ORIGS = np.array([[25.5580, -90.7844]])

# 394 unique pairs
DESTS = np.array([[37.755600, -96.773100], [35.393400, -95.272200],
                  [35.219700, -84.235400], [31.252500, -81.308500],
                  [31.646600, -91.954300], [30.384600, -97.415300],
                  [31.492100, -98.697900], [38.339300, -84.797900],
                  [31.719300, -96.396000], [39.113700, -96.249100],
                  [30.203000, -98.977700], [39.179000, -90.797400],
                  [39.707000, -81.610200], [38.978100, -87.091100],
                  [35.412000, -93.640600], [34.440900, -82.486700],
                  [32.529100, -95.140700], [36.434000, -86.271000],
                  [36.367600, -95.154600], [33.436000, -84.739100],
                  [36.499200, -91.634700], [39.323800, -88.615600],
                  [31.106400, -89.572400], [33.930700, -92.971900],
                  [36.977800, -84.871600], [35.019000, -85.219900],
                  [38.368600, -94.349600], [37.914100, -94.475800],
                  [31.318100, -91.481100], [33.983800, -98.433300],
                  [30.322100, -94.631500], [30.643200, -82.238600],
                  [36.893800, -98.801000], [33.035600, -99.468700],
                  [33.331600, -91.767900], [32.907600, -87.142700],
                  [38.991300, -89.080500], [32.979800, -80.872400],
                  [32.279700, -90.005900], [33.768300, -94.377100],
                  [37.939700, -84.026200], [31.415700, -92.832800],
                  [38.965400, -94.170900], [35.645800, -99.717300],
                  [36.126400, -91.340600], [39.527000, -94.774400],
                  [35.984900, -89.005300], [34.940600, -91.526400],
                  [33.229600, -81.214600], [35.232300, -94.453100],
                  [34.008100, -90.965900], [39.025300, -87.376300],
                  [35.029200, -85.601300], [37.936700, -98.955200],
                  [39.848800, -93.810200], [39.098300, -84.149300],
                  [37.282400, -83.771300], [34.712700, -82.767400],
                  [35.714100, -95.735100], [32.327100, -86.384100],
                  [36.661600, -87.788200], [36.413800, -96.725700],
                  [34.822400, -89.460500], [38.267700, -89.047700],
                  [32.871100, -86.645500], [32.220900, -95.869800],
                  [36.493100, -94.174100], [30.712900, -80.921200],
                  [38.348200, -90.396800], [35.149300, -92.507500],
                  [35.554800, -92.590900], [30.418600, -81.185100],
                  [30.497900, -82.874100], [34.712700, -85.438500],
                  [32.696100, -85.743000], [32.960300, -83.978000],
                  [32.821500, -91.662200], [37.034500, -92.334500],
                  [39.119200, -93.585500], [38.581000, -96.523000],
                  [35.740500, -81.705400], [35.538200, -84.700900],
                  [31.273000, -86.666500], [38.166800, -88.252200],
                  [34.944000, -92.373600], [32.192400, -90.854700],
                  [30.267000, -82.687200], [38.060900, -90.396800],
                  [39.828800, -80.025600], [39.877500, -90.286600],
                  [34.146400, -90.225500], [35.122700, -87.724100],
                  [31.595700, -81.146300], [37.333100, -94.872900],
                  [37.592700, -97.457400], [30.325600, -83.455700],
                  [35.825200, -94.360500], [31.836900, -80.225800],
                  [35.209700, -95.547500], [39.079400, -86.450000],
                  [36.281000, -97.702400], [38.788500, -99.678000],
                  [37.179500, -92.682400], [39.109500, -91.353800],
                  [37.505300, -83.678400], [32.185200, -88.446000],
                  [34.433100, -92.564800], [37.245600, -83.512600],
                  [37.733500, -88.370100], [30.444800, -98.976400],
                  [35.311100, -98.764100], [39.470900, -90.665600],
                  [39.088000, -94.545700], [37.920100, -97.885400],
                  [38.944100, -88.011100], [30.792900, -87.735600],
                  [36.369400, -97.816800], [38.110000, -96.706300],
                  [30.988900, -85.611600], [39.880100, -87.371900],
                  [31.967200, -83.738000], [30.696800, -88.817200],
                  [38.165800, -86.023400], [35.740800, -96.165100],
                  [36.683500, -84.560000], [30.388400, -86.458600],
                  [34.502400, -94.047900], [35.780700, -97.713600],
                  [37.924600, -83.040300], [37.584600, -85.496100],
                  [36.028800, -84.189500], [37.353100, -99.671300],
                  [34.551300, -89.446100], [34.908100, -89.509800],
                  [30.735600, -92.820700], [34.217100, -86.068100],
                  [35.197100, -91.332100], [31.478300, -90.056800],
                  [37.277500, -80.590900], [31.664700, -83.685700],
                  [31.297700, -94.692000], [37.389600, -94.366100],
                  [37.139700, -89.207700], [32.778600, -98.961400],
                  [35.581600, -85.648600], [36.134400, -89.399600],
                  [32.515200, -85.064900], [31.660600, -95.407700],
                  [30.139900, -97.053800], [33.064000, -93.475500],
                  [33.701300, -94.004300], [30.317300, -87.104300],
                  [32.826700, -82.771600], [33.884400, -80.434500],
                  [30.230000, -89.075400], [39.668100, -92.188200],
                  [38.073000, -80.078700], [32.935200, -98.523400],
                  [36.089400, -96.228000], [36.793500, -97.097100],
                  [37.719300, -97.724800], [30.689000, -94.928700],
                  [34.294400, -89.405400], [31.109300, -96.759000],
                  [36.730000, -85.248800], [37.009400, -87.480300],
                  [30.932400, -91.371800], [39.557200, -97.320300],
                  [38.446500, -88.857600], [35.755000, -98.057700],
                  [31.196000, -83.185900], [31.088900, -86.792300],
                  [31.976500, -90.100100], [35.834600, -99.096500],
                  [38.337000, -88.498300], [39.500500, -94.815300],
                  [39.677900, -80.128500], [34.202800, -83.938900],
                  [32.641200, -99.692200], [36.572200, -99.510600],
                  [33.202300, -99.289800], [36.672500, -83.624900],
                  [37.477900, -86.934400], [38.799600, -82.773900],
                  [35.887900, -97.986700], [34.221300, -82.485400],
                  [33.846100, -90.700200], [30.417700, -85.714000],
                  [34.969300, -92.290100], [33.510400, -87.238600],
                  [34.925900, -87.930800], [33.730300, -93.786600],
                  [39.078300, -89.632900], [37.496600, -88.104900],
                  [39.425800, -86.974600], [30.368600, -88.508500],
                  [30.169300, -81.035600], [30.754400, -92.577200],
                  [37.796700, -82.084700], [35.037500, -83.900100],
                  [37.609400, -91.667600], [38.369200, -84.511900],
                  [34.686900, -97.049700], [38.832300, -99.683600],
                  [34.655900, -82.905500], [38.971400, -97.892600],
                  [38.321800, -89.265200], [30.893100, -86.300800],
                  [37.992400, -94.178400], [38.798900, -99.215300],
                  [34.488900, -90.762400], [37.727600, -97.582300],
                  [31.281000, -92.402700], [33.759300, -81.112400],
                  [38.034000, -83.583500], [36.958000, -85.182600],
                  [30.039600, -80.248700], [36.999300, -82.025100],
                  [39.944600, -93.905800], [34.764100, -99.443900],
                  [32.193100, -83.017300], [34.341600, -82.222100],
                  [36.139200, -87.946700], [39.939000, -94.626400],
                  [34.070600, -89.796400], [39.607900, -80.993300],
                  [37.927400, -95.003500], [33.768800, -93.862100],
                  [38.090900, -84.675400], [36.737900, -92.784100],
                  [30.419300, -84.661100], [32.086900, -86.361500],
                  [35.699000, -96.473400], [33.902300, -91.790200],
                  [36.424100, -84.645900], [37.186200, -87.528900],
                  [31.031400, -86.880000], [37.156900, -84.979900],
                  [34.087100, -84.685800], [34.045400, -85.956200],
                  [30.985800, -89.268400], [36.157800, -80.547200],
                  [30.808900, -80.302200], [31.146800, -92.279800],
                  [35.984700, -85.864900], [35.649600, -92.764300],
                  [37.793600, -95.296000], [33.172000, -84.805100],
                  [32.473000, -90.879300], [35.610900, -89.245800],
                  [37.597400, -84.101300], [30.875100, -94.708400],
                  [34.763400, -86.929300], [36.919900, -87.706300],
                  [36.161000, -84.576000], [33.668700, -81.746100],
                  [38.603700, -80.695100], [34.882900, -92.092600],
                  [31.116000, -83.141700], [33.106000, -93.678100],
                  [39.902100, -94.600100], [39.938600, -94.794800],
                  [30.813800, -82.368000], [30.453000, -83.183500],
                  [34.814900, -83.479900], [39.078900, -88.237400],
                  [34.562900, -84.813600], [31.530000, -85.827500],
                  [36.057900, -96.625500], [30.059800, -95.143400],
                  [30.362200, -95.867800], [33.496800, -84.712100],
                  [32.185900, -83.627600], [37.008300, -88.940300],
                  [30.594000, -91.369800], [38.253400, -92.561100],
                  [37.095100, -84.916900], [38.183200, -97.784800],
                  [36.510700, -81.055300], [36.297300, -90.266400],
                  [35.368000, -90.323000], [34.551300, -96.188400],
                  [37.895100, -83.523500], [30.200000, -84.392400],
                  [35.443100, -91.217200], [34.822500, -84.350100],
                  [37.089800, -96.100500], [36.925300, -95.740100],
                  [32.865700, -92.439600], [31.720800, -87.098200],
                  [33.817200, -89.018400], [38.809000, -99.132600],
                  [30.529600, -86.958400], [37.677500, -81.325800],
                  [39.317100, -95.307600], [31.602700, -92.943800],
                  [36.562000, -82.429200], [38.020000, -88.106600],
                  [31.213800, -86.636600], [31.109000, -86.471400],
                  [36.175300, -96.404200], [36.400200, -88.499900],
                  [33.570300, -93.134900], [32.638400, -88.825300],
                  [30.497700, -83.045200], [37.410700, -91.238800],
                  [31.486200, -90.269800], [32.771600, -83.601400],
                  [30.928700, -85.349500], [37.411500, -84.945600],
                  [32.304100, -85.068500], [33.652800, -91.980500],
                  [36.182600, -94.203500], [37.172500, -86.999000],
                  [31.773500, -89.558400], [35.230800, -90.610700],
                  [37.592300, -89.383300], [35.069600, -85.524600],
                  [33.996900, -88.696800], [38.112000, -84.941500],
                  [35.444700, -82.447200], [31.726100, -86.948400],
                  [39.449500, -92.225100], [39.112900, -88.950600],
                  [37.123700, -82.500800], [32.417500, -88.441000],
                  [30.581200, -82.211700], [33.783500, -97.755600],
                  [31.874400, -97.122100], [39.694600, -86.523700],
                  [36.829000, -86.904200], [38.853300, -81.564800],
                  [35.998700, -89.176400], [39.261700, -97.657500],
                  [35.363200, -82.916000], [31.229200, -81.089400],
                  [31.912700, -86.790500], [36.944400, -87.257100],
                  [35.490200, -90.481400], [37.028700, -93.561500],
                  [37.326100, -94.204000], [30.573600, -81.350300],
                  [31.186900, -88.984200], [32.864800, -95.058800],
                  [37.652700, -88.976600], [38.520700, -80.042600],
                  [34.786700, -91.703400], [39.909300, -83.507600],
                  [35.284500, -81.880700], [31.053900, -95.315400],
                  [34.946400, -80.692800], [34.172100, -93.130500],
                  [31.178000, -98.364100], [30.054200, -91.453300],
                  [38.005500, -81.247800], [38.347400, -85.330800],
                  [33.676600, -86.080700], [39.597400, -95.595300],
                  [33.676700, -86.080800], [39.597500, -95.595400],
                  [33.676600, -86.080700], [39.597400, -95.595300],
                  [33.676700, -86.080800], [39.597500, -95.595400],
                  [33.676600, -86.080700], [39.597400, -95.595300],
                  [39.978600, -81.677900], [32.616400, -99.787400],
                  [34.906600, -85.528100], [32.718600, -87.544800],
                  [33.761300, -98.010200], [30.724400, -81.479600],
                  [39.171000, -85.773000], [38.107300, -86.502100],
                  [31.358900, -94.289700], [30.836200, -95.025400],
                  [31.174700, -87.801400], [37.974900, -81.277400],
                  [38.316200, -95.247100], [31.626500, -81.302800],
                  [32.256300, -89.117100], [30.365500, -92.763700],
                  [31.755200, -86.365500], [33.394200, -98.743200],
                  [36.448100, -88.296200], [39.232500, -88.779000],
                  [37.567300, -82.409500], [33.986700, -96.304800],
                  [33.258200, -90.880800], [37.264900, -99.051400],
                  [31.988700, -81.803000], [36.438800, -80.538400],
                  [35.099100, -85.145100], [38.562500, -95.645700],
                  [35.789900, -89.048900], [32.229100, -80.713200],
                  [32.218900, -87.102500], [34.821800, -92.052100],
                  [31.419600, -83.230200], [33.213000, -87.331800]]
)


def test_main():
    client = Dispatcher({
        'providers': {
            'google': {
                'type_': 'google',
                'key': 'test123',
                'base_url': 'http://localhost:8080/'
            }
        }
    })

    res = client.distance_matrix(
        origins=ORIGS,
        destinations=DESTS,
        provider='google',
        max_meters=np.Infinity
    )

    print(res)