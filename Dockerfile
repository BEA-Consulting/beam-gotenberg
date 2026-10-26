# Gotenberg (https://gotenberg.dev, MIT licence) with two changes for BEAM's Word/Excel -> PDF
# conversions. Everything else - routes, flags, basic auth - is the stock image's.
#
# 1. Font substitutes for Microsoft's Aptos family (Office's default font since 2024), which
#    can't be redistributed and otherwise falls back to a serif font. See fonts/.
# 2. A South African locale, so LibreOffice prints spreadsheet cells in Excel's built-in
#    short-date format as 2026/01/31 rather than US-style 1/31/2026.

ARG GOTENBERG_VERSION=8.38.1
FROM gotenberg/gotenberg:${GOTENBERG_VERSION}

LABEL org.opencontainers.image.source="https://github.com/BEA-Consulting/beam-gotenberg" \
      org.opencontainers.image.description="Gotenberg with Aptos font substitutes and a South African locale, for BEAM QMS" \
      org.opencontainers.image.licenses="MIT"

USER root

# fonts-roboto-unhinted adds Roboto Condensed, the substitute for Aptos Narrow.
RUN apt-get update \
 && apt-get install -y --no-install-recommends locales fonts-roboto-unhinted \
 && sed -i 's/^# *\(en_ZA.UTF-8 UTF-8\)/\1/' /etc/locale.gen \
 && locale-gen \
 && rm -rf /var/lib/apt/lists/*

COPY fonts/60-beam-font-substitutes.conf /etc/fonts/conf.d/60-beam-font-substitutes.conf
RUN fc-cache -f

ENV LANG=en_ZA.UTF-8 \
    LC_ALL=en_ZA.UTF-8

# Back to the stock image's unprivileged user (the workflow checks this still matches).
USER gotenberg
