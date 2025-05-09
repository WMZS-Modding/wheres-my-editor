import numpy as np
from PIL import Image
from skimage.morphology import skeletonize
import networkx as nx
import warnings

# --- Core API ---

def extract_pathpoints_from_image(image_path: str, *, simplify=True, pad=2):
    """
    Returns a float (x, y) list of pathpoints from the image.
    """
    img = _load_image(image_path)
    black_pixels = _detect_black_pixels(img)
    padded = _pad_image(black_pixels, pad=pad)

    full_path = _extract_path_from_skeleton(padded)
    if not full_path:
        return []

    unpadded_path = [(x - pad, y - pad) for (x, y) in full_path]

    if simplify:
        return _simplify_path(unpadded_path)
    return unpadded_path

# --- Internal helpers ---

def _load_image(image_path):
    img = Image.open(image_path).convert('L')  # Grayscale
    return np.array(img)

def _detect_black_pixels(img, threshold=50):
    return (img < threshold).astype(np.uint8)

def _pad_image(img, pad=2):
    return np.pad(img, pad_width=pad, mode='constant', constant_values=0)

def _skeleton_to_graph(skeleton):
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

def _extract_path_from_skeleton(black_pixels):
    skeleton = skeletonize(black_pixels)
    G = _skeleton_to_graph(skeleton)

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

def _angle_between(p1, p2, p3):
    a, b, c = np.array(p1), np.array(p2), np.array(p3)
    v1, v2 = a - b, c - b
    unit_v1 = v1 / (np.linalg.norm(v1) + 1e-6)
    unit_v2 = v2 / (np.linalg.norm(v2) + 1e-6)
    dot = np.clip(np.dot(unit_v1, unit_v2), -1.0, 1.0)
    return np.degrees(np.arccos(dot))

def _simplify_path(points, angle_threshold=35, min_distance=2.0):
    if len(points) < 3:
        return points

    simplified = [points[0]]
    for i in range(1, len(points) - 1):
        prev, curr, next = simplified[-1], points[i], points[i + 1]
        if np.linalg.norm(np.array(curr) - np.array(prev)) < min_distance:
            continue
        angle = _angle_between(prev, curr, next)
        if angle <= 90 or abs(angle - 180) > angle_threshold:
            simplified.append(curr)
    if np.linalg.norm(np.array(points[-1]) - np.array(simplified[-1])) >= min_distance:
        simplified.append(points[-1])
    return simplified

# --- CLI entrypoint (optional) ---

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_image")
    parser.add_argument("-o", "--output", required=True)
    args = parser.parse_args()

    points = extract_pathpoints_from_image(args.input_image)
    if not points:
        print("[!] No path points extracted.")
        return
    text = ','.join(f"{x:.2f} {y:.2f}" for (x, y) in points)
    with open(args.output, 'w') as f:
        f.write(text)
    print(f"[*] Saved {len(points)} PathPoints to {args.output}")

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    main()
