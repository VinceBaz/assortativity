import numpy as np
import matplotlib.pyplot as plt
import os
from netneurotools.plotting import plot_fsaverage as p_fsa
from netneurotools.datasets import fetch_cammoun2012, fetch_schaefer2018
from . import colors


def plot_brain_surface(values, network, hemi="L", cmap="viridis",
                       colorbar=True, center=None, vmin=None, vmax=None):
    '''
    Function to plot data on the brain, on a surface parcellation.

    PARAMETERS
    ----------
    values : ndarray (n,)
        Values to be plotted on the brain, where n is the number of nodes in
        the parcellation.
    network : dictionary
        Dictionary storing the network on associated with the values (to be
        used to identify the adequate surface parcellation)
    '''

    n = len(network["hemi"])

    if (hemi == "L"):
        scores = np.zeros((n))+np.mean(values)
        scores[network["hemi"] == 1] = values
        values = scores
    elif (hemi == "R"):
        scores = np.zeros((n))+np.mean(values)
        scores[network["hemi"] == 0] = values
        values = scores

    order = network["order"]
    noplot = network["noplot"]
    lh = network["lhannot"]
    rh = network["rhannot"]

    if os.path.isfile(lh) or os.path.isfile(rh) is False:
        fetch_cammoun2012(version='fsaverage')
        fetch_schaefer2018()

    if vmin is None:
        vmin = np.amin(values)
    if vmax is None:
        vmax = np.amax(values)

    im = p_fsa(values,
               lhannot=lh,
               rhannot=rh,
               noplot=noplot,
               order=order,
               views=['lateral', 'm'],
               vmin=vmin,
               vmax=vmax,
               colormap=cmap,
               colorbar=colorbar,
               center=center)

    return im


def plot_brain_dot(scores, coords, label=None, min_color=None,
                   max_color=None, colormap="viridis", colorbar=True, size=500,
                   show=True, dpi=100, norm=None):
    '''
    Function to plot data on the brain, where each brain region corresponds
    to a point in a 3-dimensional eucledian space
    '''
    if min_color is None:
        min_color = np.amin(scores)
    if max_color is None:
        max_color = np.amax(scores)

    fig = plt.figure(figsize=(35, 10), dpi=dpi)

    orienX = [0, 0, 90]
    orienY = [270, 180, 180]
    ax = [None, None, None]
    mapp = [None, None, None]

    for k in range(3):

        ax[k] = fig.add_subplot(1, 3, k+1, projection='3d')
        ax[k].grid(True)
        ax[k].axis('off')

        mapp[k] = ax[k].scatter(xs=coords[:, 0],
                                ys=coords[:, 1],
                                zs=coords[:, 2],
                                c=scores,
                                vmin=min_color,
                                vmax=max_color,
                                s=size,
                                cmap=colormap,
                                edgecolors='k',
                                norm=norm)

        ax[k].view_init(orienX[k], orienY[k])
        ax[k].set(xlim=0.6 * np.array(ax[k].get_xlim()),
                  ylim=0.6 * np.array(ax[k].get_ylim()),
                  zlim=0.6 * np.array(ax[k].get_zlim()))

    plt.subplots_adjust(wspace=0, left=0, right=1, bottom=0.1, hspace=0)

    if colorbar is True:

        cbar_ax = fig.add_axes([0.3, 0, 0.4, 0.10])
        cbar = fig.colorbar(mapp[0],
                            cax=cbar_ax,
                            orientation='horizontal',
                            pad=0.05)

        if label is not None:
            cbar.set_label(label, size=20)
            cbar.ax.tick_params(labelsize=20)

    if show is False:
        plt.close()


def plot_network(G, coords, edge_scores, node_scores, edge_cmap="Greys",
                 edge_alpha=0.25, edge_vmin=None, edge_vmax=None,
                 node_cmap="viridis", node_vmin=None, node_vmax=None,
                 linewidth=0.25, s=100, projection=None, view="sagittal"):

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection=projection)

    # Identify all of the edges in the network and get their colors
    Edges = np.where(G["adj"] > 0)

    if edge_scores is None:
        edge_colors = np.zeros((len(Edges[0])), dtype=str) + "black"
    else:
        edge_colors = colors.get_color_distribution(edge_scores[Edges],
                                                    cmap=edge_cmap,
                                                    vmin=edge_vmin,
                                                    vmax=edge_vmax)

    if node_scores is None:
        node_scores = "black"

    if projection is None:

        # Plot the edges
        for edge_i, edge_j, c in zip(Edges[0], Edges[1], edge_colors):

            x1 = coords[edge_i, 0]
            x2 = coords[edge_j, 0]
            y1 = coords[edge_i, 1]
            y2 = coords[edge_j, 1]

            ax.plot([x1, x2],
                    [y1, y2],
                    c=c,
                    linewidth=linewidth,
                    alpha=edge_alpha,
                    zorder=0)

        # plot the nodes
        ax.scatter(coords[:, 0],
                   coords[:, 1],
                   c=node_scores,
                   cmap=node_cmap,
                   vmin=node_vmin,
                   vmax=node_vmax,
                   s=s,
                   zorder=1)
        ax.set_aspect('equal')

    elif projection == "3d":

        # axial view of the brain
        if view == "axial":
            ax.view_init(90, 0)

        # sagittal view of the brain
        elif view == "sagittal":
            ax.view_init(0, 0)

        ax.scatter(coords[:, 0],
                   coords[:, 1],
                   coords[:, 2],
                   c=node_scores,
                   s=s,
                   zorder=1,
                   depthshade=False,
                   cmap=node_cmap,
                   vmin=node_vmin,
                   vmax=node_vmax)

        for edge_i, edge_j, c in zip(Edges[0], Edges[1], edge_colors[Edges]):
            ax.plot([coords[edge_i, 0], coords[edge_j, 0]],
                    [coords[edge_i, 1], coords[edge_j, 1]],
                    [coords[edge_i, 2], coords[edge_j, 2]],
                    c=c,
                    linewidth=linewidth,
                    zorder=0)

        scaling = np.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        ax.auto_scale_xyz(*[[np.min(scaling), np.max(scaling)]]*3)

    ax.axis('off')
