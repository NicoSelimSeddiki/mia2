import numpy as np
import scipy as sci
import matplotlib.pyplot as plt

from scipy.fftpack import fft, ifft

# my personal mia lib
from mia2 import non_linear_mapping
from mia2 import get_onset_mat

# Librosa module for calculating the Constant-Q Transform
import librosa as libr
from librosa.display import specshow

#------------------------------------------------------------------------------
def plot_CQT_spectrum( cqt_spectrum, sr, hop ):

    plt.figure(figsize=(8,4))
    specshow( libr.amplitude_to_db( np.abs(cqt_spectrum), ref=np.max),
        sr=sr, x_axis='time', y_axis='cqt_note', hop_length=hop)
    
    plt.colorbar( format='%+2.0f dB' )
    plt.title( 'Constant-Q power spectrum' )
    plt.tight_layout()
    plt.show()  

#------------------------------------------------------------------------------
def plot_harmonic_structure( common_harmonic_structure ):
    plt.stem( common_harmonic_structure, linefmt=None, markerfmt=None, 
        basefmt=None, use_line_collection=True)
    plt.xlabel( 'Log-freq. bin number' )
    plt.ylabel( 'Relative amplitude of harmonic component' )
    plt.grid()
    plt.show()

#------------------------------------------------------------------------------
def initial_harmonics( list_harmonics, 
    common_harmonic_structure, option=0 ):
    
    if option == 0:
        common_harmonic_structure[ list_harmonics ] = 1
    
    elif (option == 1) or (option == 2):
        for index, elem in enumerate( list_harmonics, 1 ):
            
            if option == 1:
                common_harmonic_structure[ elem ] = 1 / np.sqrt( index )

            if option == 2:
                common_harmonic_structure[ elem ] = 1 / index

    else:
        print( "No other options available!" )
    
    return common_harmonic_structure  

#------------------------------------------------------------------------------
def plot_pipeline( inv_observed_spectrum, inv_harm_struct, 
    estimate_freq_distro, u, u_bar ):
  """
  plot pipeline of the algorithm
  """
  s_frame = 0
  t_frame = 150

  plt.figure()
  plt.imshow(np.abs(inv_observed_spectrum[:, s_frame:t_frame]))
  plt.title("inv observed spectrum")
  plt.ylabel("time (specmurt)")
  plt.xlabel("frames")
  #plt.show()

  plt.figure()
  plt.plot(np.abs(inv_harm_struct))
  plt.title("inv harm struct")
  plt.ylabel("time (specmurt)")
  plt.xlabel("frames")
  #plt.show()

  plt.figure()
  plt.imshow(np.abs(estimate_freq_distro[:, s_frame:t_frame]))
  plt.title("V / H")
  plt.ylabel("time (specmurt)")
  plt.xlabel("frames")
  #plt.show()

  plt.figure()
  plt.imshow(np.abs(u[:, s_frame:t_frame]))
  plt.title("u = fft(V / H)")
  plt.ylabel("frequency")
  plt.xlabel("frames")
  #plt.show()

  plt.figure()
  plt.imshow(np.abs(u_bar[:, s_frame:t_frame]))
  plt.title("u bar")
  plt.ylabel("frequency")
  plt.xlabel("frames")
  plt.show()

#------------------------------------------------------------------------------
# Main function
if __name__ == '__main__':
    
    # Loading file in memory 
    file_name = '01-AchGottundHerr_4Kanal.wav'
    file_path = 'ignore/sounds/'
    full_name = file_path + file_name

    # file name to mat file with onsets and midi notes
    mat_file_name = '01-AchGottundHerr-GTF0s.mat'
    audio_data, sampling_rate = libr.load( full_name, sr=44100 )

    # hop length
    hop = 128

    # Compute and plot CQT-----------------------------------------------------
    # - One frequency bin has a length of 1379 (for Cmaj.wav)
    # - 48 bins in total -> 48 times 1379 
    cqt_spectrum = libr.cqt( audio_data, sr=sampling_rate, hop_length=hop, 
        fmin=110, n_bins=48, bins_per_octave=12 )
   
    # Define common harmonic structure-----------------------------------------
    # - number of frequency bins is the same as for the cqt -> n_bins = 48
    list_harmonics = [0, 12, 19, 24, 28, 31]
    common_harmonic_structure = np.zeros(( 48, 1 ))
    common_harmonic_structure = initial_harmonics( list_harmonics, 
        common_harmonic_structure, option=1 )

    # Plots so far-------------------------------------------------------------
    # plot_CQT_spectrum( cqt_spectrum, sampling_rate, hop )
    # plot_harmonic_structure( common_harmonic_structure )
    
    # Initial guess for fundamental frequency distribution---------------------
    # - Done via inverse filter approach.
    n_samples = 128
    squared_cqt_spectrum  = np.power( np.abs( cqt_spectrum ), 2 )

    inv_squared_spectrum = ifft( squared_cqt_spectrum, n_samples, axis=0)
    inv_harm_struct = ifft( common_harmonic_structure, n_samples, axis=0)

    # estimate first estimate
    initial_freq_distro = np.multiply( inv_squared_spectrum, 
      np.conj(inv_harm_struct ))

    # fundamental frequency distribution
    u_init = fft( initial_freq_distro, axis=0 )
    print( u_init.shape )

    # Non-linear mapping function----------------------------------------------
    u_bar = non_linear_mapping( u_init )

    # check shapes
    # print("inv_observed_spectrum: ", inv_squared_spectrum.shape)
    # print("inv_harm_struct: ", inv_harm_struct.shape)
    # print("u: ", u.shape)
    # print("u_bar: ", u_bar.shape)

    # plot whole pipeline    
    # plot_pipeline( squared_cqt_spectrum, inv_harm_struct, 
    #   initial_freq_distro, u_init, u_bar )

    # get the onsets and midi notes of the audiofile
    onsets, m, t = get_onset_mat( file_path + mat_file_name )

    # print("onsets: ", onsets.shape)
    # print("midi: ", m.shape)
    # plt.figure()
    # plt.plot(t, onsets.T)
    # plt.plot(t, m.T)
    # plt.show()
