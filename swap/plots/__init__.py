################################################################

try:
    from swap.plots import traces, distributions, performance

    from swap.plots.distributions import plot_pdf
    from swap.plots.distributions import plot_class_histogram

    from swap.plots.performance import plot_user_cm
    from swap.plots.performance import plot_confusion_matrix
    # from swap.plots.performance import plot_histogram
    from swap.plots.performance import plot_roc

    _active = True
except ImportError:
    _active = False
    import warnings
    warnings.warn('Plotting is offline. Can\'t import necessary modules')
