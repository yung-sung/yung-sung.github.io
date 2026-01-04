find . -maxdepth 1 \( -iname '*.jpg' -o -iname '*.jpeg' \) -print0 |
while IFS= read -r -d '' f; do
  base="$(basename "$f")"
  out="thumbs/${base%.*}.jpg"

  magick "$f" -auto-orient -strip ppm:- | \
    cjpeg -quality 60 -sample 2x2 -progressive -optimize -outfile "$out"
done