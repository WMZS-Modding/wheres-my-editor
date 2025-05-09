import argparse
import numpy as np
from PIL import Image
from skimage.morphology import skeletonize
from skimage.measure import find_contours
import warnings
import networkx as nx

def load_image(image_path):
    img = Image.open(image_path).convert('L')  # Grayscale
    return np.array(img)

def detect_black_pixels(img, threshold=50):
    return (img < threshold).astype(np.uint8)

def pad_image(img, pad=2):
    return np.pad(img, pad_width=pad, mode='constant', constant_values=0)

def skeleton_to_graph(skeleton):
    G = nx.Graph()
    h, w = skeleton.shape

    for y in range(h):
        for x in range(w):
            if skeleton[y, x]:
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        ny, nx_ = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx_ < w and skeleton[ny, nx_]:
                            G.add_edge((x, y), (nx_, ny))
    return G

def extract_path_from_skeleton(black_pixels):
    skeleton = skeletonize(black_pixels)
    G = skeleton_to_graph(skeleton)

    if G.number_of_nodes() == 0:
        return []

    ends = [node for node in G.nodes if G.degree[node] == 1]
    if len(ends) < 2:
        return []

    max_path = []
    for i in range(len(ends)):
        for j in range(i + 1, len(ends)):
            try:
                path = nx.shortest_path(G, ends[i], ends[j])
                if len(path) > len(max_path):
                    max_path = path
            except nx.NetworkXNoPath:
                continue

    return [(float(x), float(y)) for (x, y) in max_path]

def angle_between(p1, p2, p3):
    a = np.array(p1)
    b = np.array(p2)
    c = np.array(p3)

    v1 = a - b
    v2 = c - b

    unit_v1 = v1 / (np.linalg.norm(v1) + 1e-6)
    unit_v2 = v2 / (np.linalg.norm(v2) + 1e-6)

    dot = np.clip(np.dot(unit_v1, unit_v2), -1.0, 1.0)
    angle_rad = np.arccos(dot)
    angle_deg = np.degrees(angle_rad)
    return angle_deg

def simplify_path(points, angle_threshold=35, min_distance=2.0):
    if len(points) < 3:
        return points

    simplified = [points[0]]

    for i in range(1, len(points) - 1):
        prev = simplified[-1]
        curr = points[i]
        next = points[i + 1]

        if np.linalg.norm(np.array(curr) - np.array(prev)) < min_distance:
            continue

        angle = angle_between(prev, curr, next)
        if angle <= 90 or abs(angle - 180) > angle_threshold:
            simplified.append(curr)

    if np.linalg.norm(np.array(points[-1]) - np.array(simplified[-1])) >= min_distance:
        simplified.append(points[-1])

    return simplified

def save_path_points(path_points, output_path):
    if not path_points:
        print("[!] No path points extracted.")
        return
    text = ','.join(f"{x} {y}" for (x, y) in path_points)
    with open(output_path, 'w') as f:
        f.write(text)
    print(f"[*] Saved PathPoints to {output_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_image")
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    img = load_image(args.input_image)
    black_pixels = detect_black_pixels(img)
    padded = pad_image(black_pixels, pad=2)

    full_path = extract_path_from_skeleton(padded)
    if not full_path:
        print("[!] Failed to extract path from image.")
        return

    pad = 2
    unpadded_path = [(x - pad, y - pad) for (x, y) in full_path]
    simplified_path = simplify_path(unpadded_path, angle_threshold=35, min_distance=2.0)

    save_path_points(simplified_path, args.output)

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()
