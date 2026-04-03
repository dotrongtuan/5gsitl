#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"

SRSRAN_PROJECT_SRC="${SRSRAN_PROJECT_SRC:-${HOME}/src/srsRAN_Project}"
SRSRAN_4G_SRC="${SRSRAN_4G_SRC:-${HOME}/src/srsRAN_4G}"
SRSRAN_PROJECT_REF="${SRSRAN_PROJECT_REF:-release_25_04}"
SRSRAN_4G_REF="${SRSRAN_4G_REF:-release_23_11}"

relax_srsran_4g_werror() {
  local repo_dir="$1"
  local file

  log "Relaxing srsRAN 4G -Werror flags for GCC 13+ compatibility."
  while IFS= read -r -d '' file; do
    sed -E -i \
      -e 's/(^|[[:space:]])-Werror([[:space:]]|$)/ /g' \
      "${file}"
  done < <(find "${repo_dir}" -type f \( -name 'CMakeLists.txt' -o -name '*.cmake' \) -print0)
}

rebuild_repo() {
  local name="$1"
  local repo_url="$2"
  local repo_dir="$3"
  local ref="$4"
  shift 4
  local cmake_args=("$@")

  log "Rebuilding ${name} from ${ref}."
  mkdir -p "$(dirname "${repo_dir}")"
  if [[ ! -d "${repo_dir}/.git" ]]; then
    git clone "${repo_url}" "${repo_dir}"
  else
    git -C "${repo_dir}" fetch --all --tags --prune
  fi
  git -C "${repo_dir}" checkout --force "${ref}"
  if [[ "${name}" == "srsRAN 4G" ]]; then
    relax_srsran_4g_werror "${repo_dir}"
  fi
  cmake -S "${repo_dir}" -B "${repo_dir}/build" "${cmake_args[@]}"
  cmake --build "${repo_dir}/build" -j"$(nproc)"
  sudo_if_needed cmake --install "${repo_dir}/build"
}

rebuild_repo "srsRAN Project" "https://github.com/srsran/srsRAN_Project.git" "${SRSRAN_PROJECT_SRC}" "${SRSRAN_PROJECT_REF}" -DENABLE_EXPORT=ON -DENABLE_ZEROMQ=ON
rebuild_repo "srsRAN 4G" "https://github.com/srsran/srsRAN_4G.git" "${SRSRAN_4G_SRC}" "${SRSRAN_4G_REF}" \
  -DENABLE_WERROR=OFF \
  -DENABLE_SRSENB=OFF \
  -DENABLE_SRSEPC=OFF \
  -DENABLE_GUI=OFF \
  -DENABLE_UHD=OFF \
  -DENABLE_BLADERF=OFF \
  -DENABLE_SOAPYSDR=OFF \
  -DENABLE_SKIQ=OFF \
  -DENABLE_HARDSIM=OFF \
  -DENABLE_ZEROMQ=ON
sudo_if_needed ldconfig
log "Pinned srsRAN rebuild complete."
