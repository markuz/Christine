#Header for christine.nsi

;--------------------------------
;Interface Settings

!define MUI_ICON "christine.ico"
!define MUI_UNICON "christine_uninst.ico"

#
# Global SpamExperts defines
#
!define APP_VERSION           "%(version)s"
!define APP_BETA              ""
!define APP_PRODUCT_VERSION   "%(product_version)s"

!define APP_NAME              "SpamExperts"
!define APP_DIR               "SpamExperts"
!define APP_RELEASE_NAME      "%(release_name)s"
!define APP_RELEASE_FULL_NAME "${APP_RELEASE_NAME} v${APP_VERSION}${APP_BETA}"
