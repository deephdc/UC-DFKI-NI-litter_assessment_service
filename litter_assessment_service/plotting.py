import os
import yaml

import matplotlib.pyplot as plt
import numpy as np

from matplotlib import colors

class ResultPlot:
    def __init__(self, result, plot_type):
        self.c_matrix = result.c_matrix
        self.detected_classes = result.detected_classes
        self.grid_shape = result.grid_shape
        self.type = plot_type
        self.fig = []

    def load_plot_configs(self):
        """
        returns colors and labels for plot as specified in config.yaml file
        """
        wd = os.getcwd()
        path = os.path.join(wd, 'litter_assessment_service/litter_assessment_service/configs.yaml')

        with open(path, 'rb') as f:
            params = yaml.safe_load(f)
            color = params['plot params'][f'colors {self.type}']
            label = params['label'][f'label {self.type}'] + ['No pollution']
        return color, label

    def get_plot(self):
        """
        generates pyplot figure for classification results.
        """
        color, label = self.load_plot_configs()

        #classification matrix for heatmap
        c_matrix_im = self.c_matrix.copy()
        for i in range(len(self.c_matrix)):
            for j in range(len(self.c_matrix[0])):
                c_matrix_im[i,j] = np.where(self.c_matrix[i,j]==self.detected_classes)[0][0]
        c_matrix_im = c_matrix_im[:self.grid_shape[0]*2, :self.grid_shape[1]*2]

        #colorlist and heatmap
        color_list = [color[i] for i in self.detected_classes]
        cMap = colors.ListedColormap(color_list)
        fig = plt.figure(figsize=(9,4.5))
        ax = fig.add_subplot()
        ax.set_position([-0.1, 0.05+0.075, 1, 0.8])
        heatmap = ax.pcolor(c_matrix_im, cmap=cMap)

        #colorbar
        add_ax_pos = [0.71, 0.05+0.075, 0.02, 0.8]
        cbar_ax = fig.add_axes(add_ax_pos)
        cbar = plt.colorbar(heatmap, cax=cbar_ax)
        cbar.ax.get_yaxis().set_ticks([])
        for j, lab in enumerate([label[i] for i in self.detected_classes]):
            cbar.ax.text(len(self.detected_classes)+1,# j,
                    ( (len(self.detected_classes)-1) * j+len(self.detected_classes)/2) / (len(self.detected_classes)),
                    lab, rotation=0, fontsize = 9)
        cbar.ax.get_yaxis().labelpad = 15
        ax.invert_yaxis()

        #set aspects so plot is not oversized
        ax_im = ax
        asp = np.diff(ax.get_xlim())[0] / np.diff(ax.get_ylim())[0]
        asp /= np.abs(np.diff(ax_im.get_xlim())[0] / np.diff(ax_im.get_ylim())[0])
        ax.set_aspect(abs(asp))
        ax.set_title(f'{self.type} CNN', fontweight='bold')

        self.fig = fig

        return fig
