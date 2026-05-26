#!/bin/bash

set -euo pipefail

CHUNK_SIZE=100
PDF=""
OUTPUT_DIR=""
DRY_RUN=false

usage() {
  echo "Usage:"
  echo "  $0 --pdf-in-file <pdf_file> --output-dir <output_dir> [--chunk-size <size>] [--dry-run]"
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pdf-in-file)
      PDF="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --chunk-size)
      CHUNK_SIZE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      usage
      ;;
  esac
done

# Validate required args
if [[ -z "$PDF" || -z "$OUTPUT_DIR" ]]; then
  usage
fi

if [[ ! -f "$PDF" ]]; then
  echo "PDF file not found: $PDF"
  exit 1
fi

# Get PDF basename without extension
PDF_BASENAME=$(basename "$PDF")
PDF_NAME="${PDF_BASENAME%.*}"

# Calculate total pages
TOTAL_PAGES=$(python3 -c "import fitz; doc=fitz.open('$PDF'); print(doc.page_count)")

# Calculate total chunks
TOTAL_CHUNKS=$(( (TOTAL_PAGES + CHUNK_SIZE - 1) / CHUNK_SIZE ))

echo "PDF           : $PDF"
echo "Output dir    : $OUTPUT_DIR"
echo "Chunk size    : $CHUNK_SIZE"
echo "Total pages   : $TOTAL_PAGES"
echo "Total chunks  : $TOTAL_CHUNKS"
echo "Dry run       : $DRY_RUN"

mkdir -p "$OUTPUT_DIR"

# If total pages <= chunk size, process directly
if [[ "$TOTAL_PAGES" -le "$CHUNK_SIZE" ]]; then
  echo "Processing entire PDF directly..."

  CMD="marker_single \"$PDF\" --output_dir \"${OUTPUT_DIR%/}\""

  echo "$CMD"

  if [[ "$DRY_RUN" != true ]]; then
    eval "$CMD"
  fi

  exit 0
fi

# Determine zero-padding width
PAD_WIDTH=${#TOTAL_CHUNKS}

start=0
chunk=1

while [[ $start -lt $TOTAL_PAGES ]]; do
  end=$((start + CHUNK_SIZE - 1))

  if [[ $end -ge $TOTAL_PAGES ]]; then
    end=$((TOTAL_PAGES - 1))
  fi

  chunk_text=$(printf "chunk_%0${PAD_WIDTH}d" "$chunk")

  echo "Processing chunk $chunk_text: pages $start-$end"

  CMD="marker_single \"$PDF\" \
--output_dir \"${OUTPUT_DIR%/}/${PDF_NAME}/${chunk_text}\" \
--page_range \"${start}-${end}\""

  echo "$CMD"

  if [[ "$DRY_RUN" != true ]]; then
    eval "$CMD"
  fi

  start=$((end + 1))
  chunk=$((chunk + 1))
done

echo "Done."
