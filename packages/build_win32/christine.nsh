#Header for christine.nsi

;--------------------------------
;Interface Settings

!define MUI_ICON "christine.ico"
!define MUI_UNICON "christine_uninst.ico"

!define exe "%(exe_name)s.exe"
!define link "%(exe_name)s.lnk"
!define install_path "$PROGRAMFILES\%(program_name)s"
!define source_path "dist\"
!define install_file "$(program_name)-0.7.0.exe"
;!define config_path ${}\Christine
;!define config_file "config.ini"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

!define PRODUCT_NAME "%(full_product_name)s"
!define PRODUCT_VERSION "%(version)s"
!define PRODUCT_PUBLISHER "%(publisher)"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${exe}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

!define APP_VERSION           "%(version)s"
!define APP_BETA              ""
!define APP_PRODUCT_VERSION   "%(version)s"

!define APP_RELEASE_NAME      "%(release_name)s"
!define APP_RELEASE_FULL_NAME "${PRODUCT_NAME} - ${PRODUCT_VERSION}"


; Best Compression
SetCompress Auto
SetCompressor /SOLID lzma
SetCompressorDictSize 32
SetDatablockOptimize On

