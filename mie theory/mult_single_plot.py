#import PyMieScatt as ps
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from aux_funcs import *
import csv
import sys
from scipy.special import spherical_jn

# number of terms to calculate, should be >= x
nmax = 15
npts = 1000
nplots = 5

# radius of the sphere
# a = 50
# R = 2*a
    
# wavelengths (free space) to calculate for, in nm
wlr = np.linspace(100,400,npts)

# Radius
avals = [50*x for x in range(1,nplots+1)]

def Refl(m,wl,d):
    x = np.pi*d/wl
    k = 2*np.pi/wl
    
    #points in theta, phi over which to integrate the Poynting vector
    phir = [] #first index: theta index. second index: values of phi for given theta
    ntheta = 10 #results in about 1000pts, given uniform spacing in phi and theta
    thetar = [t for t in np.linspace(np.pi*0.5,np.pi,ntheta)] # Integrating over hemisphere
    
    for theta in thetar:
        phir_i=[]
        for phi in np.linspace(0,2*np.pi,int(4*ntheta*np.sin(theta))+1)[:-1]:
            phir_i.append(phi)
        phir.append(phir_i)
    
    pivals = []
    tauvals = []
    for theta in thetar:
        pi_temp=[0,1] #first two values
        tau_temp=[0,np.cos(theta)]
        for n in range(2,nmax+1):#remaining values
            pi_temp.append(((2*n-1)/(n-1))*np.cos(theta)*pi_temp[n-1]-(n/(n-1))*pi_temp[n-2])
            tau_temp.append(np.cos(theta)*n*pi_temp[n]-(n+1)*pi_temp[n-1])
        pivals.append(pi_temp)
        tauvals.append(tau_temp)
    
    Evals = [0]
    avals = [0]
    bvals = [0]
    
    for n in range(1,nmax+1):
        Evals.append(((1j)**n)*(2*n+1)/(n*(n+1)))
        avals.append(acoeff(n,m,x))
        bvals.append(bcoeff(n,m,x))
    
    flux_r = 0
    flux_i = 0
    rho = k*d
    dtheta = 2*np.pi/ntheta
    for i in range(len(thetar)):
        theta = thetar[i]
        for j in range(len(phir[i])):
            phi = phir[i][j]
            dphi=np.pi*0.5/(int(4*ntheta*np.sin(theta)))
            #Calculate poynting vector and add to fluxes
            Est_i, Esf_i, Hst_i, Hsf_i = 0, 0, 0, 0
            Est, Esf, Hst, Hsf = 0, 0, 0, 0

            for n in range(1,nmax+1):
                rp = (h1(n,rho)+rho*h1p(n,rho))/rho
                Est+=Evals[n]*(1j*avals[n]*np.cos(phi)*tauvals[i][n]*(rp) - bvals[n]*np.cos(phi)*pivals[i][n]*h1(n,rho))
                Esf+=Evals[n]*(-1j*avals[n]*np.sin(phi)*pivals[i][n]*(rp) + bvals[n]*np.sin(phi)*tauvals[i][n]*h1(n,rho))
                Hst+=Evals[n]*(1j*bvals[n]*np.sin(phi)*tauvals[i][n]*(rp) - avals[n]*np.sin(phi)*pivals[i][n]*h1(n,rho))
                Hsf+=Evals[n]*(1j*bvals[n]*np.cos(phi)*pivals[i][n]*(rp) - avals[n]*np.cos(phi)*tauvals[i][n]*h1(n,rho))
                
                zp = (spherical_jn(n,rho,1)*rho+spherical_jn(n,rho))/rho
                Esf_i+=Evals[n]*(-np.sin(phi)*tauvals[i][n]*spherical_jn(n,rho)+1j*np.sin(phi)*pivals[i][n]*zp)
                Est_i+=Evals[n]*(np.cos(phi)*pivals[i][n]*spherical_jn(n,rho)-1j*np.cos(phi)*tauvals[i][n]*zp)
                Hsf_i+=-Evals[n]*(-np.cos(phi)*tauvals[i][n]*spherical_jn(n,rho)+1j*np.cos(phi)*pivals[i][n]*zp)
                Hst_i+=-Evals[n]*(-np.sin(phi)*pivals[i][n]*spherical_jn(n,rho)+1j*np.sin(phi)*tauvals[i][n]*zp)

            Sr = ((Esf)*np.conj(Hst)-(Est)*np.conj(Hsf))*(d**2)*np.sin(theta)*dtheta*dphi
            Si = -(Esf_i*np.conj(Hst_i)-Est_i*np.conj(Hsf_i))*(d**2)*np.sin(theta)*dtheta*dphi
            flux_r += 0.5*Sr
            flux_i += 0.5*Si                 
    #print(flux_r)
    #print("ratio: %f"%(np.imag(flux_r)/np.real(flux_r)))
    #flux_r = np.real(flux_r)/(np.pi*(R)**2)
    #print(flux_r)
    #print()
    #return flux_r#flux_r/flux_i
    #print(flux_r/flux_i)
    return flux_r/flux_i

def Trans(m,wl,d):
    x = np.pi*d/wl
    k = 2*np.pi/wl
    #points in theta, phi over which to integrate the Poynting vector
    phir = [] #first index: theta index. second index: values of phi for given theta
    ntheta=8 #results in about 1000pts, given uniform spacing in phi and theta
    thetar=[t for t in np.linspace(0,np.pi*0.5,ntheta)]
    for theta in thetar:
        phir_i=[]
        for phi in np.linspace(0,2*np.pi,int(4*ntheta*np.sin(theta))+1)[:-1]: #lol
            phir_i.append(phi)
        phir.append(phir_i)
    
    pivals = []
    tauvals = []
    for theta in thetar:
        pi_temp=[0,1] #first two values
        tau_temp=[0,np.cos(theta)]
        for n in range(2,nmax+1):#remaining values
            pi_temp.append(((2*n-1)/(n-1))*np.cos(theta)*pi_temp[n-1]-(n/(n-1))*pi_temp[n-2])
            tau_temp.append(np.cos(theta)*n*pi_temp[n]-(n+1)*pi_temp[n-1])
        pivals.append(pi_temp)
        tauvals.append(tau_temp)
    
    Evals = [0]
    avals=[0]
    bvals=[0]
    for n in range(1,nmax+1):
        Evals.append(((1j)**n)*(2*n+1)/(n*(n+1)))
        avals.append(acoeff(n,m,x))
        bvals.append(bcoeff(n,m,x))
    flux_r = 0
    flux_i = 0
    rho = k*d
    dtheta = 2*np.pi/ntheta
    for i in range(len(thetar)):
        theta = thetar[i]
        for j in range(len(phir[i])):
            phi = phir[i][j]
            dphi=np.pi*0.5/(int(4*ntheta*np.sin(theta)))
            #Calculate poynting vector and add to fluxes
            Est_i, Esf_i, Hst_i, Hsf_i = 0, 0, 0, 0
            Est, Esf, Hst, Hsf = 0, 0, 0, 0

            for n in range(1,nmax+1):
                rp = (h1(n,rho)+rho*h1p(n,rho))/rho
                Est+=Evals[n]*(1j*avals[n]*np.cos(phi)*tauvals[i][n]*(rp) - bvals[n]*np.cos(phi)*pivals[i][n]*h1(n,rho))
                Esf+=Evals[n]*(-1j*avals[n]*np.sin(phi)*pivals[i][n]*(rp) + bvals[n]*np.sin(phi)*tauvals[i][n]*h1(n,rho))
                Hst+=Evals[n]*(1j*bvals[n]*np.sin(phi)*tauvals[i][n]*(rp) - avals[n]*np.sin(phi)*pivals[i][n]*h1(n,rho))
                Hsf+=Evals[n]*(1j*bvals[n]*np.cos(phi)*pivals[i][n]*(rp) - avals[n]*np.cos(phi)*tauvals[i][n]*h1(n,rho))
                
                zp = (spherical_jn(n,rho,1)*rho+spherical_jn(n,rho))/rho
                Esf_i+=Evals[n]*(-np.sin(phi)*tauvals[i][n]*spherical_jn(n,rho)+1j*np.sin(phi)*pivals[i][n]*zp)
                Est_i+=Evals[n]*(np.cos(phi)*pivals[i][n]*spherical_jn(n,rho)-1j*np.cos(phi)*tauvals[i][n]*zp)
                Hsf_i+=-Evals[n]*(-np.cos(phi)*tauvals[i][n]*spherical_jn(n,rho)+1j*np.cos(phi)*pivals[i][n]*zp)
                Hst_i+=-Evals[n]*(-np.sin(phi)*pivals[i][n]*spherical_jn(n,rho)+1j*np.sin(phi)*tauvals[i][n]*zp)

            Sr = ((Esf)*np.conj(Hst)-(Est)*np.conj(Hsf))*(d**2)*np.sin(theta)*dtheta*dphi
            Si = (Esf_i*np.conj(Hst_i)-Est_i*np.conj(Hsf_i))*(d**2)*np.sin(theta)*dtheta*dphi
            flux_r += 0.5*Sr
            flux_i += 0.5*Si                 
    #print(flux_r)
    #print("ratio: %f"%(np.imag(flux_r)/np.real(flux_r)))
    #flux_r = np.real(flux_r)/(np.pi*(R)**2)
    #print(flux_r)
    #print()
    #return flux_r#flux_r/flux_i
    #print(flux_r/flux_i)
    return flux_r/flux_i

#Scattering cross sections
def Csca(m,wl,diameter):
    x = np.pi*diameter/wl
    csca = 0
    for n in range(1,nmax+1):
        csca += (2*n+1) * (np.abs(acoeff(n,m,x))**2+np.abs(bcoeff(n,m,x))**2)
    csca = csca * ((wl**2)/(2*np.pi))
    return csca

def Cext(m,wl,diameter):
    x = np.pi*diameter/wl
    cext = 0
    for n in range(1,nmax+1):
        cext += (2*n+1)* np.real(acoeff(n,m,x)+bcoeff(n,m,x))
    cext = cext * ((wl**2)/(2*np.pi))
    return cext

def Cabs(m,wl,diameter):
    return Cext(m,wl,diameter) - Csca(m,wl,diameter)

plt.figure()
# title = "Extinction"
title = "Scattering"
# title = "Absorption"
plt.title(title)
for (i,aval) in enumerate(avals):
    # cer = []
    csr = []
    # car = []
    for w in wlr:
        # get index of ref via auxiliary functions
        m = IndexIn(w)
        # cer.append(Cext(m,w,2*aval)/(np.pi*(aval**2)))
        csr.append(Csca(m,w,2*aval)/(np.pi*(aval**2)))
        # car.append(Cabs(m,w,2*aval)/(np.pi*(aval**2)))

    # plt.plot(wlr,cer,color=("C"+str(i)),label="diam="+str(2*aval)+"nm")
    plt.plot(wlr,csr,color=("C"+str(i)),label="diam="+str(2*aval)+"nm")
    # plt.plot(wlr,car,color=("C"+str(i)),label="diam="+str(2*aval)+"nm")

plt.legend()
plt.xlabel("Wavelength (nm)")
plt.ylabel("Cross Section Amplitude (VA)")
if len(sys.argv) > 1:
    plt.savefig(str(sys.argv[1])+".png")
else:
    plt.show()

    

