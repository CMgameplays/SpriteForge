import os
import sys
import base64
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Blueprint, jsonify, render_template, request
from PIL import Image

try:
    from shared.limiter import limiter
except ImportError:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(get_remote_address, storage_uri="memory://")

bp = Blueprint("spriteforge", __name__, template_folder="templates")


def next_power_of_2(n: int) -> int:
    p = 512
    while p < n:
        p *= 2
    return p


def pack_sprites(named_images: list, padding: int, sort_mode: str):
    """Shelf/row bin-packing algorithm.

    Sorts sprites, determines the smallest power-of-2 sheet width that fits
    the widest sprite, then places sprites left-to-right, starting a new shelf
    whenever the current one would overflow.
    """
    if not named_images:
        return None, []

    if sort_mode == "name":
        items = sorted(named_images, key=lambda x: x[0].lower())
    else:  # size — sort by height descending
        items = sorted(named_images, key=lambda x: x[1].size[1], reverse=True)

    max_sprite_w = max(img.width for _, img in items)
    sheet_w = next_power_of_2(max_sprite_w + padding * 2)

    frames = []
    cur_x = padding
    cur_y = padding
    shelf_h = 0

    for name, img in items:
        w, h = img.size
        # Wrap to a new shelf if this sprite would exceed the sheet width
        if shelf_h > 0 and cur_x + w + padding > sheet_w:
            cur_y += shelf_h + padding
            cur_x = padding
            shelf_h = 0

        frames.append({"name": name, "x": cur_x, "y": cur_y, "w": w, "h": h})
        cur_x += w + padding
        shelf_h = max(shelf_h, h)

    sheet_h = cur_y + shelf_h + padding

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for (_, img), frame in zip(items, frames):
        sheet.paste(img, (frame["x"], frame["y"]))

    return sheet, frames


@bp.route("/")
def index():
    return render_template("spriteforge/index.html")


@bp.route("/api/pack", methods=["POST"])
@limiter.limit("30 per minute")
def api_pack():
    files = request.files.getlist("images[]")

    try:
        padding = int(request.form.get("padding", 2))
    except (ValueError, TypeError):
        padding = 2
    padding = max(0, min(16, padding))

    sort_mode = request.form.get("sort", "size")
    if sort_mode not in ("size", "name"):
        sort_mode = "size"

    named_images = []
    for f in files:
        if not f.filename:
            continue
        try:
            img = Image.open(f.stream).convert("RGBA")
            named_images.append((f.filename, img))
        except Exception:
            pass

    if not named_images:
        return jsonify({"error": "No valid images provided"}), 400

    sheet, frames = pack_sprites(named_images, padding, sort_mode)

    buf = io.BytesIO()
    sheet.save(buf, format="PNG")
    buf.seek(0)
    sheet_b64 = base64.b64encode(buf.read()).decode("utf-8")

    return jsonify(
        {
            "sheet_png": sheet_b64,
            "frames": frames,
            "sheet_w": sheet.width,
            "sheet_h": sheet.height,
        }
    )


if __name__ == "__main__":
    import webbrowser
    from threading import Timer
    from flask import Flask
    standalone = Flask(__name__)
    standalone.register_blueprint(bp, url_prefix="/")
    limiter.init_app(standalone)
    Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    standalone.run(debug=True, port=5000)
