import matplotlib.pyplot as plt
import numpy as np



color_dict = {'all':'tab:gray','REP':'tab:red','DEM':'tab:blue','IND':'tab:green','LIB':'tab:purple'}

def scatter_fig(target,pred, x_y_max,xlabel,ylabel,title,party,color, fig_name):
    fig, ax = plt.subplots()
    plt.scatter(target,pred, alpha = .3, s = 10, zorder = 1, c = color_dict[party] if color == None else color)
    plt.plot([0,x_y_max],[0,x_y_max], color = 'k',zorder=2)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(0,x_y_max)
    plt.ylim(0,x_y_max)
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close('all')

def residual_fig(target,pred, x_min,x_max,xlabel,title,party,color,fig_name):
    fig, ax = plt.subplots()
    resid_list = [pair[0]-pair[1] for pair in zip(pred,target)]
    plt.hist(resid_list,  bins = 200, color = color_dict[party] if color == None else color)
    plt.xlabel(xlabel)
    plt.ylabel('Frequency')
    plt.xlim(x_min,x_max)
    plt.title(title)
    plt.axvline(x = np.mean(np.array([resid_list])), color = 'k', lw = 1,alpha = .3, zorder = 2)
    plt.tight_layout()
    plt.savefig(fig_name)
    plt.close('all')

