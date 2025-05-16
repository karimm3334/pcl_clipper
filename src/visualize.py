#!/usr/bin/env python3

import argparse
import numpy as np
import matplotlib.pyplot as plt

class PointCloudLoader:
    """Handles loading of point clouds from text files."""
    @staticmethod
    def load(filename:str) -> np.ndarray:
        return np.loadtxt(filename)


class VoxelFilter:
    """Applies voxel grid downsampling to a point cloud."""
    @staticmethod
    def apply(points:np.ndarray, voxel_size:float) -> np.ndarray:
        if voxel_size <= 0:
            raise ValueError("voxel_size must be > 0")

        voxel_indices = np.floor(points/voxel_size).astype(np.int32)
        voxel_dict = {}

        for idx, voxel in enumerate(voxel_indices):
            key = tuple(voxel)
            if key not in voxel_dict:
                voxel_dict[key] = points[idx]

        return np.array(list(voxel_dict.values()))


class PlaneVisualizer:
    """Handles plotting of planes in 3D space."""

    @staticmethod
    def plot_plane(ax, p1, p2, p3, color='gray', alpha=0.2, scale=1.5):
        """
        Plots a rectangular plane on the matplotlib 3D axis `ax`.
        The plane is defined by three points: p1, p2, and p3.

        Parameters:
        - ax: matplotlib 3D axis to plot on
        - p1, p2, p3: three numpy arrays representing 3D points that define the plane
        - color: color of the plane
        - alpha: transparency of the plane
        - scale: how large the plane should be relative to the edges defined by p1-p2 and p1-p3
        """

        v1 = p2 - p1  # vector from p1 to p2
        v2 = p3 - p1  # vector from p1 to p3

        len_v1 = np.linalg.norm(v1)
        len_v2 = np.linalg.norm(v2)

        e1 = v1 / len_v1  # basis vector v1

        proj = np.dot(v2, e1) * e1  # component of v2 along e1
        v2_orth = v2 - proj  # component of v2 orthogonal to e1

        len_v2_orth = np.linalg.norm(v2_orth)

        if len_v2_orth < 1e-8:  # the three points are colinear
            raise ValueError("Points are colinear or too close; cannot build orthogonal basis")

        e2 = v2_orth / len_v2_orth  # basis vector e2

        # determine size of the plane rectangle side length
        # we take the smaller length of v1 and v2 and multiply by the scale parameter
        side = min(len_v1, len_v2) * scale

        # create a grid of points in 2D parameter space [0,1]x[0,1]
        u = np.linspace(0, 1, 20)  # 20 steps from 0 to 1 along u-axis
        v = np.linspace(0, 1, 20)  # 20 steps from 0 to 1 along v-axis
        uu, vv = np.meshgrid(u, v) # Create a 2D grid of (u,v) coordinates

        # calculate 3D coordinates of points on the plane surface by combining:
        # starting point p1 +
        # scaled movement along e1 in u direction + scaled movement along e2 in v direction
        # [:, :, None] expands dimensions so broadcasting works correctly for vector addition
        plane_points = p1[None, None, :] + (uu * side)[:, :, None] * e1 + (vv * side)[:, :, None] * e2

        X = plane_points[:, :, 0]
        Y = plane_points[:, :, 1]
        Z = plane_points[:, :, 2]

        # plot the surface on the 3D axes with specified color and transparency
        ax.plot_surface(X, Y, Z, color=color, alpha=alpha, edgecolor='none')


class PointCloudPlotter:
    """Responsible for plotting point clouds and coordinate axes."""
    @staticmethod
    def plot_points(ax, points:np.ndarray, color:str, label:str, alpha:float=0.5):
        if not points.shape[0]: return

        ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                   s=1, c=color, label=label, alpha=alpha)

    @staticmethod
    def draw_origin_axes(ax, length:float=0.2, linewidth:int=2):
        origin = np.array([0, 0, 0])
        ax.quiver(*origin, 1, 0, 0, color='r', length=length, linewidth=linewidth, arrow_length_ratio=0.1)
        ax.quiver(*origin, 0, 1, 0, color='g', length=length, linewidth=linewidth, arrow_length_ratio=0.1)
        ax.quiver(*origin, 0, 0, 1, color='b', length=length, linewidth=linewidth, arrow_length_ratio=0.1)


class PointCloudViewer:
    """Main viewer that ties together loading, filtering, and visualization of point clouds."""
    def __init__(self, base_filename:str, planes_filename:str='', voxel_size:float=0.01):
        self.base_filename = base_filename.replace('.txt', '')
        self.planes_filename = planes_filename
        self.voxel_size = voxel_size

        self.good_points = None
        self.filtered_points = None
        self.plane_points = None

    def load_data(self):
        self.good_points = PointCloudLoader.load(f"{self.base_filename}_good.txt")
        self.filtered_points = PointCloudLoader.load(f"{self.base_filename}_wrong.txt")
        self.plane_points = PointCloudLoader.load(self.planes_filename) if self.planes_filename else np.array([])

        if self.plane_points.any() and self.plane_points.shape != (6, 3):
            raise ValueError("Expected 6 lines of 3D points in planes.txt")

    def apply_filter(self):
        self.good_points = VoxelFilter.apply(self.good_points, self.voxel_size)
        self.filtered_points = VoxelFilter.apply(self.filtered_points, self.voxel_size)

    def plot(self):
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_title("Filtered Point Cloud with Clipping Planes")

        # plot clouds
        PointCloudPlotter.plot_points(ax, self.good_points, 'blue', 'False Points', alpha=0.5)
        PointCloudPlotter.plot_points(ax, self.filtered_points, 'red', 'Filtered Points', alpha=0.8)

        # plot planes
        if self.plane_points.any():
            PlaneVisualizer.plot_plane(ax, self.plane_points[0], self.plane_points[1], self.plane_points[2], color='green', alpha=0.3)
            PlaneVisualizer.plot_plane(ax, self.plane_points[3], self.plane_points[4], self.plane_points[5], color='purple', alpha=0.3)

        # plot origin axes and plane markers
        PointCloudPlotter.draw_origin_axes(ax)
        # ax.scatter(self.plane_points[:, 0], self.plane_points[:, 1], self.plane_points[:, 2],
        #            color='black', s=10, label='Plane Points')

        ax.legend(loc="upper right")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        plt.tight_layout()
        plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("points_filename", type=str, help="Base filename (e.g., points.txt)")
    parser.add_argument("planes_filename", type=str, nargs='?', default='', help="Planes filename (e.g., planes.txt)")
    parser.add_argument("--voxel_size", type=float, default=0.01, help="Voxel size (default: 0.01)")
    # parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    viewer = PointCloudViewer(
        base_filename=args.points_filename,
        planes_filename=args.planes_filename,
        voxel_size=args.voxel_size,
    )
    viewer.load_data()
    viewer.apply_filter()
    viewer.plot()

if __name__ == "__main__":
    main()