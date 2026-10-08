#!/usr/bin/env bash
# Run LibreOffice headless for a one-shot conversion (pptx -> pdf, ppt -> pptx), in its own
# throwaway profile so it never collides with another soffice and never hangs on a stale lock.
#
#   soffice.sh --convert-to pdf deck.pptx [--outdir DIR]
#
# Fails loudly when LibreOffice is absent. The wrapper this replaces was called with its
# output sent to /dev/null, so on a box with no soffice the PDF step of four figure builds
# had been failing in silence: the PDFs on disk were stale and nothing said so.
set -euo pipefail
bin=${SOFFICE_BIN:-$(command -v soffice || command -v libreoffice || true)}
if [ -z "$bin" ]; then
  echo "soffice.sh: LibreOffice is not installed (no soffice or libreoffice on PATH; set SOFFICE_BIN to override)" >&2
  exit 127
fi
profile=$(mktemp -d "${TMPDIR:-/tmp}/soffice-profile.XXXXXX")
trap 'rm -rf "$profile"' EXIT
export SAL_USE_VCLPLUGIN=svp            # headless rendering backend, no display needed
"$bin" -env:UserInstallation="file://$profile" --headless --norestore --nolockcheck "$@"
