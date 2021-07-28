# Encoding: utf-8
import numpy as np
import matplotlib.pyplot as plt
from numpy.lib.scimath import sqrt
from .math import e_x


def getPermittivityProfile(structure, lbda, unit='m'):
    """Returns permittivity tensor profile."""
    layers = sum([L.getPermittivityProfile(lbda, unit) for L in structure.layers], [])
    front = (float('inf'), structure.frontHalfSpace.material.getTensor(lbda, unit))
    back = (float('inf'), structure.backHalfSpace.material.getTensor(lbda, unit))
    return sum([[front], layers, [back]], [])


def getIndexProfile(structure, lbda, unit='m', v=e_x):
    """Returns refractive index profile.

    'v' : Unit vector, direction of evaluation of the refraction index.
          Default value is v = e_x.
    """
    profile = getPermittivityProfile(structure, lbda, unit)
    (h, epsilon) = list(zip(*profile))  # unzip
    n = [sqrt((v.T * eps * v)[0, 0, 0]) for eps in epsilon]
    return list(zip(h, n))


def drawStructure(structure, lbda=1000, unit='nm', method="graph", margin=0.15):
    """Draw the structure.

    'method' : 'graph' or 'section'
    Returns : Axes object
    """
    # Build index profile
    profile = getIndexProfile(structure, lbda, unit)
    (h, n) = list(zip(*profile))     # unzip
    n = np.array(n)
    z_layers = np.hstack((0., np.cumsum(h[1:-1])))
    z_max = z_layers[-1]
    if z_max != 0.:
        z_margin = margin * z_max
    else:
        z_margin = 1e-6
    z = np.hstack((-z_margin, z_layers, z_max + z_margin))
    # Call specialized methods
    if method == "graph":
        ax = _drawStructureGraph(structure, z, n, unit)
    elif method == "section":
        ax = _drawStructureSection(structure, z, n, unit)
    else:
        ax = None
    return ax


def _drawStructureGraph(structure, z, n, unit):
    """Draw a graph of the refractive index profile """
    n = np.hstack((n, n[-1]))
    # Draw the graph
    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(1, 1, 1)
    fig.subplots_adjust(bottom=0.17)
    ax.step(z, n.real, 'black', where='post')
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.set_xlabel("z ({})".format(unit))
    ax.set_ylabel("n'")
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0, 0))
    ax.set_xlim(z.min(), z.max())
    ax.set_ylim(bottom=1.0)
    return ax


def _drawStructureSection(structure, z, n, unit):
    """Draw a cross section of the structure"""
    # Prepare arrays for pcolormesh()
    X = z * np.ones((2, 1))
    Y = np.array([0, 1]).reshape((2, 1)) * np.ones_like(z)
    n = np.array(n).reshape((1, -1)).real
    # Draw the cross section
    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_subplot(1, 1, 1)
    fig.subplots_adjust(left=0.05, bottom=0.15)
    ax.set_yticks([])
    ax.set_xlabel("z ({})".format(unit))
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0, 0))
    ax.set_xlim(z.min(), z.max())
    stack = ax.pcolormesh(X, Y, n, cmap=plt.get_cmap('gray_r'))
    colbar = fig.colorbar(stack, orientation='vertical', anchor=(1.2, 0.5),
                          fraction=0.05)
    colbar.ax.set_xlabel("n'", position=(3, 0))
    return ax