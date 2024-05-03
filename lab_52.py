#lab5 


#Мета роботи: отримати поглиблені навички з візуалізації даних; ознайомитись з matplotlib.widgets,
#scipy.signal.filters, а також з Plotly, Bokeh, Altair; отримати навички зі створення інтерактивних
#застосунків для швидкого підбору параметрів і аналізу отриманих результатів

#bokeh was chosen



from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, CheckboxGroup, Button
import numpy as np
from scipy.signal import butter, filtfilt
import sys
import subprocess #for running bokeh server

#essentials




#initial values for sliders
initial_amplitude = 1.0
initial_frequency = 0.5
initial_phase = 0.0
initial_noise_mean = 0.0
initial_noise_covariance = 0.1
global_noise = None

#creating timeline
time = np.linspace(0, 10, 1000)
sampling_frequency = 1 / (time[1] - time[0])


#from harmonic formule
def harmonic_calculation(time, amplitude, frequency, phase):
    return amplitude * np.sin(2 * np.pi * frequency * time + phase)

#noise
def create_noise(time, noise_mean, noise_covariance):
    return np.random.normal(noise_mean, np.sqrt(noise_covariance), len(time))

#harmonic with noise
def harmonic_with_noise(time, amplitude, frequency, phase=0, noise_mean=0, noise_covariance=0.1, noise=None):
    harmonic_signal = harmonic_calculation(time, amplitude, frequency, phase)
    if noise is not None:
        return harmonic_signal + noise
    else:
        global global_noise
        global_noise = create_noise(time, noise_mean, noise_covariance)
        return harmonic_signal + global_noise



#median filter
def median_filter(data, window_size):
  filtered_data = []
  window_size = int(window_size) 
  for i in range(len(data)):
    if i < window_size // 2:  # data at the beginning
      window = data[:i+window_size]
    elif i >= len(data) - window_size // 2:  # data at the end
      window = data[i-window_size+1:]
    else:
      window = data[i-window_size//2:i+window_size//2+1]  # extract window
    filtered_data.append(sorted(window)[window_size // 2]) #sorting & getting median
  return filtered_data


#gui
plot = figure(title="Harmonic & Noise", x_axis_label='Time', y_axis_label='Amplitude', width=1000, height=500, align='center', sizing_mode="fixed", toolbar_location="below")


#harmonic line generation
harmonic_line = plot.line(time, harmonic_calculation(time, initial_amplitude, initial_frequency, initial_phase), line_width=2, color='cyan', line_dash='dotted', legend_label='Harmonic line')

#harmonic & noise generation
with_noise_line = plot.line(time, harmonic_with_noise(time, initial_amplitude, frequency=initial_frequency,
                                                   phase=initial_phase, noise_mean=initial_noise_mean,
                                                   noise_covariance=initial_noise_covariance,noise=None), 
                                                   line_width=2, color='royalblue', legend_label='Signal with noise')

#filtering
filtered_signal = median_filter(with_noise_line.data_source.data['y'],sampling_frequency)
#build filtred line
l_filtered = plot.line(time, filtered_signal, line_width=2, color='midnightblue', legend_label='Filtered Signal')

#all about sliders

#color
slider_color = 'darkblue'


#making
s_amplitude = Slider(title="Amplitude", value=initial_amplitude, start=0.1, end=10.0, step=0.1,  bar_color=slider_color)
s_frequency = Slider(title="Frequency", value=initial_frequency, start=0.1, end=10.0, step=0.1,  bar_color=slider_color)
s_phase = Slider(title="Phase", value=initial_phase, start=0.0, end=2 * np.pi, step=0.1, bar_color=slider_color)
s_noise_mean = Slider(title="Noise Mean", value=initial_noise_mean, start=-1.0, end=1.0, step=0.1, bar_color=slider_color)
s_noise_covariance = Slider(title="Noise Covariance", value=initial_noise_covariance, start=0.0, end=1.0, step=0.1, bar_color=slider_color)
s_cutoff_frequency = Slider(title="window_size", value=3, start=1, end=35.0, step=1, bar_color=slider_color)

cb_show_noise = CheckboxGroup(labels=['Show Noise'], active=[0]) #show noise checkbox

button_regenerate_noise = Button(label='Regenerate Noise') #regenerate noise button

button_reset = Button(label='Reset') #reset button

#update with all changes made with params
def update(attrname, old, new):
    amplitude = s_amplitude.value
    frequency = s_frequency.value
    phase = s_phase.value

    noise_mean = s_noise_mean.value
    noise_covariance = s_noise_covariance.value

    global initial_noise_mean, initial_noise_covariance, global_noise
    
    if initial_noise_covariance != noise_covariance or initial_noise_mean != noise_mean:
        initial_noise_mean = noise_mean
        initial_noise_covariance = noise_covariance
        global_noise = create_noise(time, noise_mean, noise_covariance)


    show_noise = bool(new)
    harmonic_line.data_source.data['y'] = harmonic_calculation(time, amplitude, frequency, phase)
    
    with_noise_line.data_source.data['y'] = harmonic_with_noise(time, amplitude, frequency, phase,
                                                                noise_mean, noise_covariance, global_noise)
    with_noise_line.visible = show_noise

    cutoff_frequency = s_cutoff_frequency.value
    filtered_signal = median_filter(with_noise_line.data_source.data['y'], cutoff_frequency)
    l_filtered.data_source.data['y'] = filtered_signal







#regenerate noise button
def regenerate_noise():
    with_noise_line.data_source.data['y'] = harmonic_with_noise(time, s_amplitude.value, s_frequency.value, s_phase.value,
                                                                s_noise_mean.value, s_noise_covariance.value)
#reset button 
def reset_params():
    s_amplitude.value = initial_amplitude
    s_frequency.value = initial_frequency
    s_phase.value = initial_phase
    s_noise_mean.value = 0.0
    s_noise_covariance.value = 0.1
    s_cutoff_frequency.value = 3
    cb_show_noise.active = [0]
    regenerate_noise()

s_amplitude.on_change('value', update)
s_frequency.on_change('value', update)
s_phase.on_change('value', update)
s_noise_mean.on_change('value', update)
s_noise_covariance.on_change('value', update)
s_cutoff_frequency.on_change('value', update)

cb_show_noise.on_change('active', update)
button_regenerate_noise.on_click(regenerate_noise)
button_reset.on_click(reset_params)

layout = column(plot, 
                row(s_amplitude, s_frequency, align='center'),
                row(s_phase, s_noise_mean, align='center'),
                row(s_noise_covariance, s_cutoff_frequency, align='center'),
                row(cb_show_noise, button_regenerate_noise, button_reset, align='center'),
                sizing_mode='stretch_width',  align='center')

#bg color
layout.background = "cornflowerblue"
curdoc().add_root(layout)

#starting a bokeh server
if __name__ == "__main__":
    with open("lab5_bokeh.py", "w", encoding="utf-8") as f:
        f.write(__import__("inspect").getsource(sys.modules[__name__]))
    subprocess.run(["bokeh", "serve", "--show", "lab5_bokeh.py"])
