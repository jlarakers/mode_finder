from finite_differences import *
import matplotlib.pyplot as plt
from interp import *
import math
import csv
from read_EFIT import *
from read_EFIT_file import *
from read_iterdb_file import *
from max_pedestal_finder import find_pedestal
import matplotlib.gridspec as gridspec
#Last edited by Max Curie 06/10/2020
#Supported by David R Hatch's script mtmDopplerFreqs.py


#**************Block for user******************************************
#**************Setting up*********************************************
iterdb_file_name = 'DIIID175823.iterdb' #name of the iterdb file
geomfile = 'g175823.04108_257x257'                     #name of the magnetic geometry file

f_max=250      #upper bound of the frequency experimentally observed 
f_min=0        #lower bound of the frequency experimentally observed 
plot = 1         #set to 1 if you want to plot the result
report=1         #set to 1 if you want to export a csv report
omega_percent=10.  #choose the omega within the top that percent defined in(0,100)
n0_min=1         #minmum mode number (include) that finder will cover
n0_max=100       #maximum mode number (include) that finder will cover
q_scale=1.        #set the q to q*q_scale
mref = 2.        # mass of ion in proton mass
#**************End of Setting up*********************************************
#**************End of Block for user******************************************



#*************Loading the data******************************************
rhot0, te0, ti0, ne0, ni0, nz0, vrot0 = read_iterdb_file(iterdb_file_name)
EFITdict = read_EFIT(geomfile)
xgrid = EFITdict['psipn']
q = EFITdict['qpsi']*q_scale

uni_rhot = np.linspace(min(rhot0),max(rhot0),len(rhot0)*10)

te_u = interp(rhot0,te0,uni_rhot)
ne_u = interp(rhot0,ne0,uni_rhot)
vrot_u = interp(rhot0,vrot0,uni_rhot)
q      = interp(xgrid,q,uni_rhot)
tprime_e = -fd_d1_o4(te_u,uni_rhot)/te_u
nprime_e = -fd_d1_o4(ne_u,uni_rhot)/ne_u


midped, topped=find_pedestal(file_name=geomfile, path_name='', plot=False)
x0_center = midped

print('mid pedestal is at r/a = '+str(x0_center))

Lref, Bref, R_major, q0, shat0=get_geom_pars(geomfile,x0_center)

index_begin=np.argmin(abs(uni_rhot-x0_center+2*(1-x0_center)))

te_u = te_u[index_begin:len(uni_rhot)-1]
ne_u = ne_u[index_begin:len(uni_rhot)-1]
vrot_u = vrot_u[index_begin:len(uni_rhot)-1]
q      = q[index_begin:len(uni_rhot)-1]
tprime_e = tprime_e[index_begin:len(uni_rhot)-1]
nprime_e = nprime_e[index_begin:len(uni_rhot)-1]
uni_rhot = uni_rhot[index_begin:len(uni_rhot)-1]

center_index = np.argmin(abs(uni_rhot-x0_center))


#*************End of loading the data******************************************

#****************Start setting up ******************

q0      = q[center_index]
ne = ne_u[center_index]
te = te_u[center_index] #it is in eV
#Bref=float(Bref_Gauss)/10000
m_SI = mref *1.6726*10**(-27)
c  = 1
qref = 1.6*10**(-19)
nref = ne
Tref = te * qref
cref = np.sqrt(Tref / m_SI)
Omegaref = qref * Bref / m_SI / c
rhoref = cref / Omegaref 

ky=q0*rhoref/(Lref*x0_center)
kymin = ky
te_mid = te_u[center_index]
kyGENE =kymin * (q/q0) * np.sqrt(te_u/te_mid) * (x0_center/uni_rhot) #Add the effect of the q varying
#***Calculate omeage star********************************
#from mtm_doppler
omMTM = kyGENE*(tprime_e+nprime_e)
gyroFreq = 9.79E3/np.sqrt(mref)*np.sqrt(te_u)/Lref
#print("gyroFreq="+str(gyroFreq[center_index]))
mtmFreq = omMTM*gyroFreq/2./np.pi/1000.

fontsize0=12
fig, ax=plt.subplots(nrows=2,ncols=2,sharex=True) 
            #nrows is the total rows
            #ncols is the total columns
            #sharex true means the xaxies will be shared
ax[0,0].plot(uni_rhot,te_u,label=r'$T_e$')
#ax[0,0].set_xlabel('x')
ax[0,0].set_ylabel(r'$T_e(eV)$',fontsize=fontsize0)
#ax1.set_title()        #for the set the title name
ax[0,1].plot(uni_rhot,ne_u,label=r'$n_e$')
#ax[0,1].set_xlabel('x')
ax[0,1].set_ylabel(r'$n_e(m^{-3})$',fontsize=fontsize0)
ax[1,0].plot(uni_rhot[:-1],mtmFreq[:-1],label=r'$\omega_{*e}$')
ax[1,0].set_xlabel(r'$\rho_{tor}$',fontsize=fontsize0)
ax[1,0].set_ylabel(r'$\omega_{*e}(kHz)$',fontsize=fontsize0)
ax[1,1].plot(uni_rhot,q,label='Safety factor')
ax[1,1].set_xlabel(r'$\rho_{tor}$',fontsize=fontsize0)
ax[1,1].set_ylabel('Safety factor',fontsize=fontsize0)
#for i in range(2):
#   for j in range(2):
#       ax[i,j].legend()

plt.tight_layout()
plt.show()

#******************End setting up ****************

#****************Start scanning mode number*************
kymin_range=[]
ky_range=[]
n0_range=[]
m0_range=[]
f_range=[]
f_GENE_range=[]
x_range=[]
drive_range=[]

for n0 in range(n0_min,n0_max+1):
    n0_TEMP=0

#***********Calculating the ky********************************
    #From SI_Gauss_GENE_unit.py
    m0 = n0*q0
    ky=n0*q0*rhoref/(Lref*x0_center)
    kymin = ky
    n0_global = n0
    te_mid = te_u[center_index]
    kyGENE =kymin * (q/q0) * np.sqrt(te_u/te_mid) * (x0_center/uni_rhot) #Add the effect of the q varying
#***Calculate omeage star********************************
#from mtm_doppler
    omMTM = kyGENE*(tprime_e+nprime_e)
    gyroFreq = 9.79E3/np.sqrt(mref)*np.sqrt(te_u)/Lref
    #print("gyroFreq="+str(gyroFreq[center_index]))
    mtmFreq = omMTM*gyroFreq/2./np.pi/1000.
    omegaDoppler = vrot_u*n0_global/2./np.pi/1E3
    omega=mtmFreq + omegaDoppler
    if plot==1:
        plt.clf()
        plt.title('mode number finder')
        plt.xlabel('r/a')
        plt.ylabel('frequency (kHz)') 
        plt.plot(uni_rhot,mtmFreq + omegaDoppler,label='Diamagnetic plus Doppler (MTM in lab frame)')
#***End of Calculate omeage star**************************
#***Find the range where the omega is within the top omega_percent%
    omega_range=[]
    range_ind=[]
    omega_max=np.max(omega)
    if n0 == 1: 
        print('n=1, max omega is' + str(omega_max) +'kHz')
    omega_min=omega_max*(100.-omega_percent)/100.
    for i in range(len(uni_rhot)):
        if omega[i] >= omega_min:
            omega_range.append(uni_rhot[i])
            range_ind.append(i)
    range_min=min(omega_range)
    ind_min  =min(range_ind)
    range_max=max(omega_range)
    ind_max  =max(range_ind)

#***End of Find the range where the omega is within the top omega_percent%

#*******Find the range within the frequency range************************
    range_ind2=[]
    for i in range(len(uni_rhot)):
        if omega[i] >= f_min and omega[i] <= f_max:
        	range_ind2.append(i)
#*******Find the range within the frequency range************************

#find the rational surfaces

#From the plot_mode_structures.py
    qmin = np.min(q[ind_min:ind_max])
    qmax = np.max(q[ind_min:ind_max])
    mmin = math.ceil(qmin*n0)
    mmax = math.floor(qmax*n0)
    mnums = np.arange(mmin,mmax+1)
    qrats = mnums/float(n0)

    if ky <= 5:
#***********End of Calculating the ky************************
        for i in range(len(qrats)):
            n = int(n0)
            m = int(mmin + i)
            ix = np.argmin(abs(q-qrats[i])) 
            if uni_rhot[ix] >= range_min and uni_rhot[ix] <= range_max:
                if ix in range_ind2:
                    print('ky='+str(ky))
                    print('(m,n)='+str((m,n)))
                    temp_str=str((n,m))
                    if plot==1:
                        plt.axvline(uni_rhot[ix],color='red', label= temp_str)
                    n0_TEMP=n0_TEMP+1
                    kymin_range.append(ky)
                    ky_range.append(kyGENE[ix])
                    n0_range.append(n)
                    m0_range.append(m)
                    f_range.append(omega[ix])
                    f_GENE_range.append(omega[ix]*2*np.pi*1000/gyroFreq[ix])
                    x_range.append(uni_rhot[ix])
                    drive_range.append(omega[ix]/omega_max)

                else:
                    if plot==1:
                        plt.axvline(uni_rhot[ix],color='green')
            else:
                if plot==1:
                    plt.axvline(uni_rhot[ix],color='green')
    else:
        for i in range(len(qrats)):
            n = int(n0)
            m = int(mmin + i)
            ix = np.argmin(abs(q-qrats[i]))
            if plot==1:
                plt.axvline(uni_rhot[ix],color='green')

    if n0_TEMP > 0 and plot==1:
        plt.xlim(0.9,1)
        plt.ylim(0,max(mtmFreq + omegaDoppler))
        plt.legend()
        plt.savefig('mode_number_finder_n0='+str(n0)+'.png')
print('**********************************************')
print('**************Start of report*****************')
if len(ky_range)==0:
    print('There is no unstabel MTM')
else:
    print('ky range from '+str(min(ky_range))+' to '+str(max(ky_range)))
    print('n0 range from '+str(min(n0_range))+' to '+str(max(n0_range)))
print('**********************************************')
print('***************End of report******************')

if report==1:
    with open('mode_number_finder_report.csv','w') as csvfile:
        data = csv.writer(csvfile, delimiter=',')
        data.writerow(['n ','m ','ky(' + str(x0_center)+')','ky(r)   ','frequency(kHz)           ','location(r/a)            ','omega(cs/a)    ','Drive(omega*/omega*_max)'])
        for i in range(len(n0_range)):
            data.writerow([n0_range[i],m0_range[i],kymin_range[i],ky_range[i],f_range[i],x_range[i],f_GENE_range[i],drive_range[i]])
    csvfile.close()

ky_range2=ky_range
n0_range2=n0_range
m0_range2=m0_range
f_range2=f_range
x_range2=x_range

#for i in range(len(n0_range)):
#    for j in range(len(n0_range)):
#        if min(x_range2[i]*Lref) >= rhoref:
#        	countinue
#        else:
            

plt.clf()
plt.title('Frequency Spectrum')
plt.ylabel('frequency (kHz)') 
for i in range(len(n0_range)):
   plt.axhline(f_range[i],color='red',alpha=0.5)#alpha control the transparency, alpha=0 transparency, alpha=1 solid
plt.xlim(0,1)
plt.ylim(f_min,f_max)
plt.show()


x_zoom=[]
q_zoom=[]
f_zoom=[]
#x_min=np.min(x_range)*0.7
#x_max=np.max(x_range)*1.3
x_min=0
x_max=1

for i in range(len(uni_rhot)):
    if uni_rhot[i]<=x_max and uni_rhot[i]>=x_min:
        x_zoom.append(uni_rhot[i])
        q_zoom.append(q[i])
        f_zoom.append(mtmFreq[i] + omegaDoppler[i])


plt.clf()
plt.title('Summary plot')
plt.xlabel('r/a')
plt.ylabel('a.u.') 
plt.plot(x_zoom,f_zoom/np.max(f_zoom),label='Diamagnetic plus Doppler frequency(MTM in lab frame)')
plt.plot(x_zoom,q_zoom/np.max(q_zoom),label='Safety factor')
for i in range(len(n0_range)):
   plt.axvline(x_range[i],color='red',alpha=0.2)#alpha control the transparency, alpha=0 transparency, alpha=1 solid
plt.legend()
plt.show()
plt.savefig('Summary.png')

#midped, topped = find_pedestal(geomfile, path_name='', plot=0)
