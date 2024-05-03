#lab5 


#Мета роботи: отримати поглиблені навички з візуалізації даних; ознайомитись з matplotlib.widgets,
#scipy.signal.filters, а також з Plotly, Bokeh, Altair; отримати навички зі створення інтерактивних
#застосунків для швидкого підбору параметрів і аналізу отриманих результатів

#matplotlib

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
import numpy as np

#essentiasls

from scipy.signal import butter, filtfilt #ex2 for filtring

#initial values for sliders
initial_amplitude = 1.0
initial_frequency = 0.5
initial_phase = 0.0
initial_noise_mean = 0.0
initial_noise_covariance = 0.05
global_noise = None

#timeline
time = np.linspace(0, 10, 1000)
sampling_frequency = 1 / (time[1] - time[0])




def harmonic_calculation(time, amplitude, frequency, phase): 
    return amplitude * np.sin(2 * np.pi * frequency * time + phase) #from harmonic formule

def create_noise(time, noise_mean, noise_covariance): #noise
    return np.random.normal(noise_mean, np.sqrt(noise_covariance), len(time))


def harmonic_with_noise(time, amplitude, frequency, phase=0, noise_mean=0, noise_covariance=0.1, show_noise=None, noise=None): #harmonic with noise
    harmonic_signal = harmonic_calculation(time, amplitude, frequency, phase)
    if show_noise:
        if noise is not None:
            return harmonic_signal + noise
        else:
            global global_noise
            global_noise = create_noise(time, noise_mean, noise_covariance)
            return harmonic_signal + global_noise

# gui
fig, ax = plt.subplots()
ax.grid()
ax.set_xlim(0, 10)
plt.subplots_adjust(left=0.1, bottom=0.45, top=0.95)

#butterworth filter
def butter_lowpass_filter(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

#filtering
def lowpass_filter(data, cutoff_freq, fs, order=5):
    b, a = butter_lowpass_filter(cutoff_freq, fs, order=order)
    y = filtfilt(b, a, data)
    return y




harmonic_line, = ax.plot(time, harmonic_calculation(time, initial_amplitude, initial_frequency, initial_phase), 
lw=2, color='cyan', linestyle=':', label='Harmonic line') #harmonic generation

with_noise_line, = ax.plot(time, harmonic_with_noise(time, initial_amplitude, frequency=initial_frequency, 
                                                  phase=initial_phase, noise_mean=initial_noise_mean, noise_covariance=initial_noise_covariance, 
                                                  show_noise=True, noise=None), lw=2, color='royalblue',label='Noise graph') #harmonic with noise generation




filtered_line = lowpass_filter(with_noise_line.get_ydata(), 3, sampling_frequency, order=5) #lowpass filter usage


l_filtered, = ax.plot(time, filtered_line, lw=2, color='midnightblue', label='Filtered line')


ax.legend()



# all about sliders

#styles
axcolor = 'cornflowerblue'
slider_color = 'darkblue'


#slider placement
ax_amplitude = plt.axes([0.12, 0.35, 0.65, 0.03], facecolor=axcolor)
ax_frequency = plt.axes([0.12, 0.3, 0.65, 0.03], facecolor=axcolor)
ax_phase = plt.axes([0.12, 0.25, 0.65, 0.03], facecolor=axcolor)
ax_noise_mean = plt.axes([0.12, 0.2, 0.65, 0.03], facecolor=axcolor)
ax_noise_covariance = plt.axes([0.12, 0.15, 0.65, 0.03], facecolor=axcolor)
ax_cutoff_frequency = plt.axes([0.12, 0.1, 0.65, 0.03], facecolor=axcolor)


#creating sliders
s_amplitude = Slider(ax_amplitude, 'Amplitude', 0.1, 5.0, valinit=initial_amplitude, color=slider_color)
s_frequency = Slider(ax_frequency, 'Frequency', 0.1, 5.0, valinit=initial_frequency, color=slider_color)
s_phase = Slider(ax_phase, 'Phase', 0.0, 2 * np.pi, valinit=initial_phase, color=slider_color)
s_noise_mean = Slider(ax_noise_mean, 'Noise Mean', -1.0, 1.0, valinit=initial_noise_mean, color=slider_color)
s_noise_covariance = Slider(ax_noise_covariance, 'Noise Covariance', 0.0, 1.0, valinit=initial_noise_covariance, color=slider_color)
s_cutoff_frequency = Slider(ax_cutoff_frequency, 'Cutoff Frequency', 0.1, 10.0, valinit=3, color=slider_color)



rax = plt.axes([0.12, 0.03, 0.1, 0.04], facecolor=axcolor)
cb_show_noise = CheckButtons(rax, ['Show Noise'], [True]) #noise checkbox


button_regenerate_noise = Button(plt.axes([0.48, 0.03, 0.1, 0.04]), 'Regenerate Noise', color=axcolor, hovercolor='0.975') #regenerate noise button


button_reset = Button(plt.axes([0.80, 0.03, 0.1, 0.04]), 'Reset', color=axcolor, hovercolor='0.975') #reset button

#updates with changes  


# The function to be called anytime a slider's value changes
def update(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val

    harmonic_line.set_ydata(harmonic_calculation(time, amplitude, frequency, phase))
    with_noise_line.set_ydata(harmonic_with_noise(time, amplitude, frequency, phase, noise=global_noise, show_noise=cb_show_noise.get_status()[0]))

    cutoff_frequency = s_cutoff_frequency.val
    filtered_signal = lowpass_filter(with_noise_line.get_ydata(), cutoff_frequency, sampling_frequency)
    l_filtered.set_ydata(filtered_signal)    
    fig.canvas.draw_idle()

#if checkbox:
def update_checkbox(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val

    harmonic_line.set_ydata(harmonic_calculation(time, amplitude, frequency, phase))
    with_noise_line.set_ydata(harmonic_with_noise(time, amplitude, frequency, phase, noise=global_noise, show_noise=cb_show_noise.get_status()[0]))
    fig.canvas.draw_idle()

#noise mean changes
def update_noise(val):
    amplitude = s_amplitude.val
    frequency = s_frequency.val
    phase = s_phase.val
    noise_mean = s_noise_mean.val
    noise_covariance = s_noise_covariance.val
    harmonic_line.set_ydata(harmonic_calculation(time, amplitude, frequency, phase))
    with_noise_line.set_ydata(harmonic_with_noise(time, amplitude, frequency, phase, noise_mean, noise_covariance, cb_show_noise.get_status()[0]))

    cutoff_frequency = s_cutoff_frequency.val
    filtered_signal = lowpass_filter(with_noise_line.get_ydata(), cutoff_frequency, sampling_frequency)
    l_filtered.set_ydata(filtered_signal)
    fig.canvas.draw_idle()
    
#regenerate_noise
def regenerate_noise(event):
    with_noise_line.set_ydata(harmonic_with_noise(time, s_amplitude.val, s_frequency.val, s_phase.val, s_noise_mean.val, s_noise_covariance.val, show_noise=True))
    fig.canvas.draw_idle()


# reset to defaults
def reset(event):
    s_amplitude.reset()
    s_frequency.reset()
    s_phase.reset()
    s_noise_mean.reset()
    s_noise_covariance.reset()
    s_cutoff_frequency.reset()
    cb_show_noise.set_active(0)
    regenerate_noise(event)

#filtred update
def update_filter(val):
    cutoff_frequency = s_cutoff_frequency.val
    filtered_signal = lowpass_filter(with_noise_line.get_ydata(), cutoff_frequency, sampling_frequency)
    l_filtered.set_ydata(filtered_signal)
    fig.canvas.draw_idle()






#register the update function with each slider
s_amplitude.on_changed(update)
s_frequency.on_changed(update)
s_phase.on_changed(update)
s_noise_mean.on_changed(update_noise)
s_noise_covariance.on_changed(update_noise)
s_cutoff_frequency.on_changed(update_filter)


cb_show_noise.on_clicked(update_checkbox)
button_regenerate_noise.on_clicked(regenerate_noise)
button_reset.on_clicked(reset)



plt.show()
