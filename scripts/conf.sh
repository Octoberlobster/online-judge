#!/bin/bash
REAL_UID="${SUDO_UID:-$(id -u)}"
REAL_HOME="$(getent passwd "${REAL_UID}" | cut -d: -f6)"
DMOJ_STATIC_PATH="${HOME}/dmoj-site/static"
SITE_DIR="${REAL_HOME}/dmoj-site" 
PROBLEMS_DIR="${SITE_DIR}/problems"                # 問題庫目錄（會掛到容器 /problems）
WAVES_DIR="${SITE_DIR}/waves"                      # 波形目錄（會掛到容器 /waves）
log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }
trap 'log "❌ 發生錯誤，腳本中止。"' ERR
sudo apt update
sudo apt install -y acl
sudo setfacl -m u:www-data:x /home
sudo setfacl -m u:www-data:x "${HOME}"
sudo setfacl -R -m u:www-data:rx "$DMOJ_STATIC_PATH"
sudo setfacl -R -m d:u:www-data:rx "$DMOJ_STATIC_PATH"

# ===== STEP 4：建立 problems / waves 目錄並設定權限 =====
log "STEP 12: 建立 problems 目錄：${PROBLEMS_DIR}"
sudo mkdir -p "${PROBLEMS_DIR}"
sudo chmod 777 "${PROBLEMS_DIR}"
sudo chown "$(id -u)":"$(id -g)" "${PROBLEMS_DIR}"

log "STEP 13: 建立 waves 目錄：${WAVES_DIR}"
sudo mkdir -p "${WAVES_DIR}"
sudo chmod 777 "${WAVES_DIR}"
sudo chown "$(id -u)":"$(id -g)" "${WAVES_DIR}"