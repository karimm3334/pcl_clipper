#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <cmath>
#include <string>
#include <chrono>
#include <iomanip>

struct Point3D {
    double x, y, z;
};

class Plane {
    std::array<double, 3> normal{};
    double d = 0.0;

public:
    Plane(const Point3D& a, const Point3D& b, const Point3D& c) {
        double ux = b.x - a.x, uy = b.y - a.y, uz = b.z - a.z;
        double vx = c.x - a.x, vy = c.y - a.y, vz = c.z - a.z;

        normal[0] = uy * vz - uz * vy;
        normal[1] = uz * vx - ux * vz;
        normal[2] = ux * vy - uy * vx;

        double length = std::sqrt(normal[0]*normal[0] + normal[1]*normal[1] + normal[2]*normal[2]);
        for (auto& n : normal) n /= length;

        d = -(normal[0]*a.x + normal[1]*a.y + normal[2]*a.z);
    }

    bool is_valid(const Point3D& p) const {
        return (normal[0]*p.x + normal[1]*p.y + normal[2]*p.z + d) <= 0;
    }
};

std::vector<Point3D> load_points(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) throw std::runtime_error("Cannot open file: " + filename);

    std::vector<Point3D> points;
    Point3D p;
    while (file >> p.x >> p.y >> p.z) {
        points.push_back(p);
    }
    return points;
}

void save_points(const std::string& filename, const std::vector<Point3D>& points) {
    std::ofstream file(filename);
    if (!file) throw std::runtime_error("Cannot open file for writing: " + filename);

    std::ostringstream buffer;
    for (const auto& p : points) {
        buffer << p.x << " " << p.y << " " << p.z << "\n";
    }

    file << buffer.str();  // write all at once
}


double ms_duration(const std::chrono::high_resolution_clock::time_point& start,
                   const std::chrono::high_resolution_clock::time_point& end) {
    return std::chrono::duration<double, std::milli>(end - start).count();
}

int main(int argc, char* argv[]) {
    using Clock = std::chrono::high_resolution_clock;

    if (argc < 3 || argc > 4) {
        std::cerr << "Usage: " << argv[0] << " <points.txt> <planes.txt> [-t]\n";
        return 1;
    }

    bool print_timing = (argc == 4 && std::string(argv[3]) == "-t");
    auto t0 = Clock::now();

    // Load points
    auto t1 = Clock::now();
    auto points = load_points(argv[1]);
    auto t2 = Clock::now();

    // Load plane points
    auto plane_pts = load_points(argv[2]);
    auto t3 = Clock::now();

    if (plane_pts.size() != 6) {
        std::cerr << "Error: Plane file must contain exactly 6 points (2 planes).\n";
        return 1;
    }

    // Construct planes
    Plane plane1(plane_pts[0], plane_pts[1], plane_pts[2]);
    Plane plane2(plane_pts[3], plane_pts[4], plane_pts[5]);
    auto t4 = Clock::now();

    // Classify points
    std::vector<Point3D> good, bad;
    good.reserve(points.size());
    bad.reserve(points.size());

    for (const auto& p : points) {
        if (plane1.is_valid(p) || plane2.is_valid(p))
            good.push_back(p);
        else
            bad.push_back(p);
    }
    auto t5 = Clock::now();

    // Save files
    std::string input_name = argv[1];
    size_t dot_pos = input_name.find_last_of('.');
    std::string base_name = (dot_pos != std::string::npos) ? input_name.substr(0, dot_pos) : input_name;

    save_points(base_name + "_good.txt", good);
    auto t6 = Clock::now();

    save_points(base_name + "_wrong.txt", bad);
    auto t7 = Clock::now();

    std::cout << "Total points: " << points.size()
              << " | Valid: " << good.size() << " (" << (good.size() * 100 / points.size()) << "%)"
              << " | Invalid: " << bad.size() << " (" << (bad.size() * 100 / points.size()) << "%)\n";

    if (print_timing) {
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Timing breakdown:\n"
                  << "  Load points       : " << std::setw(6) << ms_duration(t1, t2) << " ms\n"
                  << "  Load plane points : " << std::setw(6) << ms_duration(t2, t3) << " ms\n"
                  << "  Construct planes  : " << std::setw(6) << ms_duration(t3, t4) << " ms\n"
                  << "  Classification    : " << std::setw(6) << ms_duration(t4, t5) << " ms\n"
                  << "  Save good points  : " << std::setw(6) << ms_duration(t5, t6) << " ms\n"
                  << "  Save bad points   : " << std::setw(6) << ms_duration(t6, t7) << " ms\n"
                  << "  Total elapsed     : " << std::setw(6) << ms_duration(t0, t7) << " ms\n";
    }

    return 0;
}
