#!/usr/bin/env bash
set -euo pipefail
set +x

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_EXAMPLE="$SCRIPT_DIR/.env.example"
ENV_FILE="$SCRIPT_DIR/.env"
TMP_FILE=""

cleanup() {
  if [[ -n "${TMP_FILE:-}" && -f "$TMP_FILE" ]]; then
    rm -f -- "$TMP_FILE"
  fi
}
trap cleanup EXIT INT TERM

fail() {
  printf '\nSETUP FAILED: %s\n' "$1" >&2
  exit 1
}

[[ -f "$ENV_EXAMPLE" ]] || fail ".env.example was not found beside setup.sh."

printf '%s\n' 'VIDEO DESTIM TERMINAL SETUP'
printf '%s\n' '---------------------------'
printf '\n'

if [[ -f "$ENV_FILE" ]]; then
  printf '%s\n' 'EXISTING .env CONFIGURATION FOUND.'
  while true; do
    IFS= read -r -p 'UPDATE YOUTUBE API KEY AND OVERRIDE PIN? [Y/N] ' update_answer || fail 'Input ended before a choice was made.'
    case "${update_answer,,}" in
      y|yes)
        break
        ;;
      n|no)
        printf '%s\n' 'NO CHANGES MADE.'
        exit 0
        ;;
      *)
        printf '%s\n' 'PLEASE ENTER Y OR N.'
        ;;
    esac
  done
else
  umask 077
  cp -- "$ENV_EXAMPLE" "$ENV_FILE"
fi

while true; do
  IFS= read -r -s -p 'ENTER YOUTUBE API KEY: ' api_key || fail 'Input ended before an API key was entered.'
  printf '\n'
  api_key="${api_key//$'\r'/}"

  if [[ -z "$api_key" ]]; then
    printf '%s\n' 'API KEY CANNOT BE BLANK.'
    continue
  fi

  if [[ "$api_key" =~ [[:space:]] ]]; then
    printf '%s\n' 'API KEY CANNOT CONTAIN WHITESPACE. TRY AGAIN.'
    continue
  fi

  break
done

while true; do
  IFS= read -r -s -p 'CHOOSE OVERRIDE PIN: ' override_pin || fail 'Input ended before an override PIN was entered.'
  printf '\n'
  override_pin="${override_pin//$'\r'/}"

  if [[ "$override_pin" =~ ^[0-9]{4}$ ]]; then
    break
  fi

  printf '%s\n' 'OVERRIDE PIN MUST BE EXACTLY FOUR DIGITS.'
done

umask 077
TMP_FILE="$(mktemp "${ENV_FILE}.tmp.XXXXXX")"
key_written=0
pin_written=0

while IFS= read -r line || [[ -n "$line" ]]; do
  case "$line" in
    YOUTUBE_API_KEY=*)
      if [[ "$key_written" -eq 0 ]]; then
        printf 'YOUTUBE_API_KEY=%s\n' "$api_key" >> "$TMP_FILE"
        key_written=1
      fi
      ;;
    OVERRIDE_PIN=*)
      if [[ "$pin_written" -eq 0 ]]; then
        printf 'OVERRIDE_PIN=%s\n' "$override_pin" >> "$TMP_FILE"
        pin_written=1
      fi
      ;;
    *)
      printf '%s\n' "$line" >> "$TMP_FILE"
      ;;
  esac
done < "$ENV_FILE"

if [[ "$key_written" -eq 0 ]]; then
  printf '\nYOUTUBE_API_KEY=%s\n' "$api_key" >> "$TMP_FILE"
fi

if [[ "$pin_written" -eq 0 ]]; then
  printf 'OVERRIDE_PIN=%s\n' "$override_pin" >> "$TMP_FILE"
fi

chmod 600 "$TMP_FILE"
mv -- "$TMP_FILE" "$ENV_FILE"
TMP_FILE=""
chmod 600 "$ENV_FILE"
unset api_key override_pin

printf '\n%s\n' 'CONFIGURATION SAVED TO .env.'
printf '%s\n' 'THE API KEY AND PIN WERE NOT PRINTED BACK TO THE TERMINAL.'
printf '\n%s\n' 'NEXT STEP:'
printf '%s\n' 'docker compose up -d --build'
