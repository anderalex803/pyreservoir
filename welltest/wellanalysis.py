"""
Program for Well-test Result Analysis

@author: Yohanes Nuwara
@email: ign.nuwara97@gmail.com
"""

def constant_rate_drawdown_test(t, p, q, Bo, mu_oil, h, poro, ct, rw, your_guess):
  """
  Analyzing Constant-Rate Well-test Result
  Note: Make your initial guess of the data index where LTR and MTR separate
  """
  import numpy as np
  import matplotlib.pyplot as plt
  from scipy.optimize import curve_fit
  import matplotlib.patches as mpl_patches  

  def permeability(q, Bo, mu_oil, h, m_cycle):
    """Calculate permeability from BHFP vs time semilog plot"""
    return (-162.6 * q * Bo * mu_oil) / (m_cycle * h)

  def skin_factor(pi, k, poro, mu_oil, ct, rw, c1, m_cycle):
    """
    Calculate skin factor from BHFP vs time semilog plot
    Note: k is the calculated permeability
    """
    return 1.1513 * (((pi - c1) / -m_cycle) - np.log10(k / (poro * mu_oil * ct * (rw**2))) + 3.2275)

  def reservoir_size(q, Bo, poro, h, ct, m2):
    """Calculate reservoir size from BHFP vs time normal plot"""
    return np.sqrt(-(.07447 * q * Bo) / (poro * h * ct * m2))

  def linear(x, a, b):
    return a * x + b

  # guess time index (input to user)
  your_guess = 17

  " Analysis of MTR region to calculate permeability "

  t_crop1, p_crop1 = np.log(t[1:your_guess+1]), p[1:your_guess+1]
  popt, pcov = curve_fit(linear, t_crop1, p_crop1)
  m1, c1 = popt[0], popt[1]

  # calculate permeability
  m_cycle = m1 * np.log(10) # slope has unit psi/cycle
  k = permeability(q, Bo, mu_oil, h, m_cycle)

  # calculate skin factor
  s = skin_factor(pi, k, poro, mu_oil, ct, rw, c1, m_cycle)

  " Analysis of LTR region to calculate reservoir size "

  t_crop2, p_crop2 = t[your_guess:], p[your_guess:]
  popt, pcov = curve_fit(linear, t_crop2, p_crop2)
  m2, c2 = popt[0], popt[1]

  # calculate reservoir size
  re = reservoir_size(q, Bo, poro, h, ct, m2)

  " Plot Analysis "

  plt.figure(figsize=(15,5))

  # normal plot BHFP vs time
  plt.subplot(1,2,1)
  plt.plot(t, p, '.', color='black')

  ## plot the regression line
  y_fit = m2 * t + c2
  plt.plot(t, y_fit, color='red', linewidth=1)

  ## plot the separate MTR and LTR region
  plt.axvspan(0, t[your_guess], color='green', alpha=0.3)
  plt.axvspan(t[your_guess], max(t), color='yellow', alpha=0.3)

  plt.title('Normal Plot of BHFP vs Time', size=20, pad=10)
  plt.xlabel('Time (hours)', size=17); plt.ylabel('Pressure (psia)', size=17)
  plt.xlim(0,max(t))

  # output all results to plot
  labels2 = []
  labels2.append("End Time of ETR = {} hours".format(np.round(t[your_guess], 3)))
  handles2 = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white", 
                                  lw=0, alpha=0)] * 1                                    

  plt.legend(handles2, labels2, loc='best', fontsize='large', 
              fancybox=True, framealpha=0.7, 
              handlelength=0, handletextpad=0)
  plt.grid(True, which='both', color='black', linewidth=0.1)

  # semilog plot BHFP vs time
  plt.subplot(1,2,2)
  plt.semilogx(t, p, '.', color='black')

  ## plot the regression line
  y_fit = m1 * np.log(t) + c1
  plt.plot(t, y_fit, color='red', linewidth=1)

  ## plot the separate MTR and LTR region
  plt.axvspan(0, t[your_guess], color='green', alpha=0.3)
  plt.axvspan(t[your_guess], max(t), color='yellow', alpha=0.3)  

  plt.title('Semilog Plot of BHFP vs Time', size=20, pad=10)
  plt.xlabel('Time (hours)', size=17); plt.ylabel('Pressure (psia)', size=17)
  plt.xlim(xmax=max(t))

  # output all results into the plot
  labels1 = []
  labels1.append("Calc. Permeability = {} md".format(np.round(k, 3)))
  labels1.append("Calc. Skin Factor = {}".format(np.round(s, 3)))
  labels1.append("Calc. Reservoir Size = {} ft".format(np.round(re, 3)))  
  handles1 = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white", 
                                  lw=0, alpha=0)] * 3 

  plt.legend(handles1, labels1, loc='best', fontsize='large', 
              fancybox=True, framealpha=0.7, 
              handlelength=0, handletextpad=0) 
  
  plt.grid(True, which='both', color='black', linewidth=0.1)

  plt.tight_layout(1) 
  plt.show()

def multi_rate_drawdown_test(t, p, t_change, q_change, Bo, mu_oil, h, poro, ct, rw):
  """
  Analyzing Multi-Rate Well-test Result
  """
  import numpy as np
  import matplotlib.pyplot as plt
  from scipy.optimize import curve_fit
  import matplotlib.patches as mpl_patches  

  def permeability(Bo, mu_oil, h, m):
    """Calculate permeability from drawdown plot"""
    return (162.6 * Bo * mu_oil) / (m * h)

  def skin_factor(k, poro, mu_oil, ct, rw, c, m):
    """
    Calculate skin factor from drawdown plot
    Note: k is the calculated permeability
    """
    return 1.1513 * ((c / m) - np.log10(k / (poro * mu_oil * ct * (rw**2))) + 3.2275)

  def linear(x, a, b):
    return a * x + b
  
  # calculate delta rate (Δq)
  t_change = np.append(0, t_change)
  delta_q = [j-i for i, j in zip(q_change[:-1], q_change[1:])]
  delta_q = np.concatenate((np.array([0, q_change[0]]), delta_q))

  # create rate step profile
  time_arr = []
  rate_arr = []
  x = []
  y = []

  " Calculate the x-axis and y-axis "

  for i in range(len(t)):  
      for j in range(0, len(t_change)-1):
          if t[i] > t_change[j] and t[i] <= t_change[j+1]:
              # produce t and q profile
              time_arr.append(t[i])
              rate_arr.append(q_change[j])

              # calculate Fp as x-axis
              tn = np.log10(t[i] - t_change[:j+1])
              delta_qn = delta_q[1:j+2] / q_change[j]
              tn_mult_delta_qn = tn * delta_qn
              Fp = np.sum(tn_mult_delta_qn)
              x.append(Fp)

              # calculate ((pi - pwf) / qn) as y-axis
              y_ = (pi - p[i]) / q_change[j]
              y.append(y_)

  # regression to the drawdown plot
  popt, pcov = curve_fit(linear, x, y)
  m, c = popt[0], popt[1]

  # calculate permeability
  k = permeability(Bo, mu_oil, h, m)

  # calculate skin factor
  s = skin_factor(k, poro, mu_oil, ct, rw, c, m)

  # output calculated results to plot
  labels1 = []
  labels1.append("Calc. Permeability = {} md".format(np.round(k, 3)))
  labels1.append("Calc. Skin Factor = {}".format(np.round(s, 3)))
  handles1 = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white", 
                                  lw=0, alpha=0)] * 2

  " Plot Analysis "

  plt.figure(figsize=(15,5))

  plt.subplot(1,2,1)
  plt.plot(time_arr, p, '.-', color='black')
  plt.xlim(0, max(t))
  plt.title('Pressure Profile from Well-Test Result', size=20, pad=10)
  plt.xlabel(r'Time (hours)', size=17); plt.ylabel(r'Pressure (psi)', size=17)
  plt.grid(True, which='both', color='black', linewidth=0.1)

  plt.subplot(1,2,2)
  plt.plot(x, y, '.', color='black')
  plt.xlim(0, max(x))
  plt.title('Drawdown Plot for Multi-Rate Flow', size=20, pad=10)
  plt.xlabel(r'$F_p$', size=17); plt.ylabel(r'$\frac{p_i-p_{wf}}{q_n}$ (psi-D/STB)', size=17)

  # plot regression line
  y_fit = m * np.array(x) + c
  plt.plot(x, y_fit, color='red', linewidth=0.5)

  plt.legend(handles1, labels1, loc='best', fontsize='large', 
              fancybox=True, framealpha=0.7, 
              handlelength=0, handletextpad=0) 
  plt.grid(True, which='both', color='black', linewidth=0.1)
  plt.tight_layout(1)
  plt.show()  
  
def constant_pressure_test(t, q, pwf, pi, Bo, mu_oil, h, poro, ct, rw):
  """
  Analyzing Constant Pressure Well-test Result
  """
  import numpy as np
  import matplotlib.pyplot as plt
  from scipy.optimize import curve_fit
  import matplotlib.patches as mpl_patches  

  def permeability(Bo, mu_oil, h, m):
    """Calculate permeability from semilog plot"""
    return (162.6 * Bo * mu_oil) / (m * h * (pi - pwf))

  def skin_factor(k, poro, mu_oil, ct, rw, c, m):
    """
    Calculate skin factor from semilog plot
    Note: k is the calculated permeability
    """
    return 1.1513 * ((c / m) - np.log10(k / (poro * mu_oil * ct * (rw**2))) + 3.2275)

  def linear(x, a, b):
    return a * x + b
  
  # linear regression
  x, y = np.log10(t), 1/q
  popt, pcov = curve_fit(linear, x, y)
  m, c = popt[0], popt[1]

  plt.figure(figsize=(10,7))

  # calculate permeability
  k = permeability(Bo, mu_oil, h, m)

  # calculate skin factor
  s = skin_factor(k, poro, mu_oil, ct, rw, c, m)

  # output calculated results to plot
  labels1 = []
  labels1.append("Calc. Permeability = {} md".format(np.round(k, 3)))
  labels1.append("Calc. Skin Factor = {}".format(np.round(s, 3)))
  handles1 = [mpl_patches.Rectangle((0, 0), 1, 1, fc="white", ec="white", 
                                  lw=0, alpha=0)] * 2

  # plot semilog plot of 1/q vs t
  plt.semilogx(t, 1/q, '.', color='black')
  plt.title('Semilog Plot of Reciprocal Rate vs Time', size=20, pad=10)
  plt.xlabel('Time (hour)', size=17); plt.ylabel(r'$\frac{1}{q}$ (D/STB)', size=17)
  plt.xlim(xmin=1)

  # plot regression line
  y_fit = m * np.log10(t) + c
  plt.plot(t, y_fit, color='red', linewidth=0.7)

  plt.legend(handles1, labels1, loc='best', fontsize='large', 
              fancybox=True, framealpha=0.7, 
              handlelength=0, handletextpad=0) 

  plt.grid(True, which='both', color='black', linewidth=0.1)
  plt.show() 
  