from scipy.special import lambertw
import scipy.constants as sconst
import scipy.optimize as scopt
import numpy as np

class Fitter:
    
    def calculateT(arrlnm, arrI, T, L, R):
        arrl = arrlnm * 1e-9
        actualI = Fitter.alt_normalised_spectral_intensity(arrl, T)
        arrT = []
        for i in range(len(arrl)):
            if L < arrlnm[i] and R > arrlnm[i]:
                try:
                    curT = arrI[i] / actualI[i]
                    arrT.append(curT)
                except ZeroDivisionError:
                    arrT.append(0)
        arrT = np.array(arrT)
        if arrT.size == 0: return np.array([])
        else:
            try: 
                arrT = arrT / np.max(arrT)
            except ZeroDivisionError:   
                arrT = np.array([])
            return arrT
    
    def spectral_intensity(l, T):
        alpha = sconst.h * sconst.c / sconst.k / T
        return 2 * sconst.h * (sconst.c ** 2) / (l ** 5) / (np.exp(alpha / l) - 1)

    def fitted_spectral_intensity(l, T, C):
        alpha = sconst.h * sconst.c / sconst.k / T
        return C / (l ** 5) / (np.exp(alpha / l) - 1)
    
    def normalised_spectral_intensity(l, T):
        """Spectral intensity with a unit integral"""
        alpha = sconst.h * sconst.c / sconst.k / T
        return 15 * (alpha ** 4) / (l ** 5) /  (np.exp(alpha / l) - 1) / (sconst.pi ** 4)

    def alt_normalised_spectral_intensity(l, T):
        """Spectral intensity with a maximum intensity of 1"""
        alpha = sconst.h * sconst.c / sconst.k / T
        lambertConst = lambertw(-5*np.exp(-5)).real
        lmax = alpha / (lambertConst + 5)
        Imax = -lambertConst/ (lmax ** 4)
        return alpha / Imax / (l ** 5) /  (np.exp(alpha / l) - 1)
    
    def calculate_temperature(calibration, data):
        arrx, arry = [], []
        for i, l in enumerate(data.l):
            if calibration.L < l and calibration.R > l:
                arrx.append(l)
                arry.append(data.I[i])
        actualI = []
        if len(arrx) > 0:
            arrtmp = []
            for l in calibration.l:
                if l > calibration.L and l < calibration.R:
                    arrtmp.append(l)
            actualI = np.array(arry) / np.interp(arrx, arrtmp, calibration.T)
            actualI /= np.max(actualI)
            param, param_cov = scopt.curve_fit(Fitter.fitted_spectral_intensity, np.array(arrx) * 1e-9, actualI, p0 = [2000, 1e-29], sigma=10)
            data.temp = param[0]
            data.dTemp = np.sqrt(param_cov[0][0])
        return arrx, actualI