import matplotlib
import matplotlib.pyplot as plt
import mpld3
matplotlib.use('Agg')

import numpy as np


def get_results(givendata, needs_to_increase):

    data = [int(i) for i in givendata]
    
    mean_value = np.mean(data)
    std_deviation = np.std(data)
    
    
    cv = (std_deviation / mean_value) * 100
    
    
    x = np.arange(1, len(data) + 1)
    slope, _ = np.polyfit(x, data, 1)
    
    
    if cv < 10:
        consistency_feedback = "Excellent consistency! Keep up the steady progress."
    elif 10 <= cv <= 30:
        consistency_feedback = "Good consistency, but there is room for improvement."
    else:
        consistency_feedback = "High variability in your efforts. Try to maintain a more consistent pace."
    


    if needs_to_increase:
        if slope > 0:
            progress_feedback = "Your progress is on track with an increasing trend."
        else:
            progress_feedback = "Your progress is not on track; it is decreasing when it should be increasing."
    else:
        if slope < 0:
            progress_feedback = "Your progress is on track with a decreasing trend."
        else:
            progress_feedback = "Your progress is not on track; it is increasing when it should be decreasing."
    
    
    return {
        "mean_value": mean_value,
        "std_deviation": std_deviation,
        "cv": round(cv, 2),
        "slope": round(slope, 2),
        "consistency_feedback": consistency_feedback,
        "progress_feedback": progress_feedback
    }


def get_visuals(data, title, unit):
    y = [int(i) for i in data]
    x = np.arange(1, len(y) + 1)
    
    fig, ax = plt.subplots()
    ax.plot(x, y, marker='o', linestyle='-', label='Actual Data')
    
    slope, intercept = np.polyfit(x, y, 1)    
    ax.plot(x, slope * x + intercept, color='red', linestyle='--', label=f'Regression Line (Slope: {slope:.2f})')

    ax.set_title(title)
    ax.set_xlabel('Day')
    ax.set_ylabel(f'Progress ({unit})')    
    ax.legend()
    
    svg_code = mpld3.fig_to_html(fig)

    return svg_code
