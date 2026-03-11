#!/bin/bash
# Download MUTCD road sign images from Wikimedia Commons
# These are US government works (public domain)
# Uses Special:FilePath endpoint with rate limiting

OUT_DIR="/tmp/mutcd_signs"
mkdir -p "$OUT_DIR"

download_sign() {
    local filename="$1"
    local wiki_name="$2"
    local outpath="${OUT_DIR}/${filename}.png"

    if [ -f "$outpath" ] && [ "$(file -b --mime-type "$outpath")" = "image/png" ]; then
        echo "SKIP $filename (already exists)"
        return 0
    fi

    echo -n "  $filename... "
    local code
    code=$(curl -sL -o "$outpath" \
        -H "User-Agent: Mozilla/5.0 (compatible; EducationalBot/1.0)" \
        -w "%{http_code}" \
        "https://commons.wikimedia.org/wiki/Special:FilePath/${wiki_name}?width=400" 2>/dev/null)

    if [ "$code" = "200" ] && [ "$(file -b --mime-type "$outpath" 2>/dev/null)" = "image/png" ]; then
        echo "OK"
        return 0
    else
        echo "FAILED ($code)"
        rm -f "$outpath"
        return 1
    fi
}

# Regulatory signs
echo "=== Regulatory Signs ==="
declare -A reg_signs=(
    ["stop"]="MUTCD_R1-1.svg"
    ["yield"]="MUTCD_R1-2.svg"
    ["speed_limit_25"]="MUTCD_R2-1_(25).svg"
    ["speed_limit_35"]="MUTCD_R2-1_(35).svg"
    ["speed_limit_55"]="MUTCD_R2-1_(55).svg"
    ["speed_limit_65"]="MUTCD_R2-1_(65).svg"
    ["no_u_turn"]="MUTCD_R3-4.svg"
    ["no_left_turn"]="MUTCD_R3-2.svg"
    ["no_right_turn"]="MUTCD_R3-1.svg"
    ["do_not_enter"]="MUTCD_R5-1.svg"
    ["wrong_way"]="MUTCD_R5-1a.svg"
    ["one_way_left"]="MUTCD_R6-1L.svg"
    ["one_way_right"]="MUTCD_R6-1R.svg"
    ["no_passing"]="MUTCD_R4-1.svg"
    ["keep_right"]="MUTCD_R4-7.svg"
)

for name in $(echo "${!reg_signs[@]}" | tr ' ' '\n' | sort); do
    download_sign "$name" "${reg_signs[$name]}"
    sleep 3
done

# Warning signs
echo "=== Warning Signs ==="
declare -A warn_signs=(
    ["curve_right"]="MUTCD_W1-2R.svg"
    ["curve_left"]="MUTCD_W1-2L.svg"
    ["reverse_curve"]="MUTCD_W1-4R.svg"
    ["winding_road"]="MUTCD_W1-5R.svg"
    ["merge"]="MUTCD_W4-1.svg"
    ["added_lane"]="MUTCD_W4-3.svg"
    ["divided_highway"]="MUTCD_W6-1.svg"
    ["divided_highway_ends"]="MUTCD_W6-2.svg"
    ["two_way_traffic"]="MUTCD_W6-3.svg"
    ["hill"]="MUTCD_W7-1.svg"
    ["slippery_when_wet"]="MUTCD_W8-5.svg"
    ["railroad_crossing"]="MUTCD_W10-1.svg"
    ["signal_ahead"]="MUTCD_W3-3.svg"
    ["stop_ahead"]="MUTCD_W3-1.svg"
    ["pedestrian_crossing"]="MUTCD_W11-2.svg"
    ["deer_crossing"]="MUTCD_W11-3.svg"
    ["school_zone"]="MUTCD_S1-1.svg"
    ["road_narrows"]="MUTCD_W5-1.svg"
    ["cross_road"]="MUTCD_W2-1.svg"
    ["side_road"]="MUTCD_W2-2.svg"
    ["sharp_turn_right"]="MUTCD_W1-1R.svg"
)

for name in $(echo "${!warn_signs[@]}" | tr ' ' '\n' | sort); do
    download_sign "$name" "${warn_signs[$name]}"
    sleep 3
done

# Other important signs
echo "=== Other Signs ==="
declare -A other_signs=(
    ["railroad_crossbuck"]="MUTCD_R15-1.svg"
    ["no_parking"]="MUTCD_R8-3.svg"
    ["handicap_parking"]="MUTCD_R7-8.svg"
)

for name in $(echo "${!other_signs[@]}" | tr ' ' '\n' | sort); do
    download_sign "$name" "${other_signs[$name]}"
    sleep 3
done

echo ""
echo "=== Summary ==="
count=$(find "$OUT_DIR" -name "*.png" -exec file {} \; | grep "PNG image" | wc -l)
echo "Downloaded $count sign images to $OUT_DIR"
