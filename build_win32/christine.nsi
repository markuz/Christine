!define exe "christine.exe"
!define link "christine.lnk"
!define install_path "$PROGRAMFILES\Christine"
!define source_path "dist\"
!define install_file "Christine-0.7.0.exe"
;!define config_path ${}\Christine
;!define config_file "config.ini"
!define PRODUCT_NAME "Christine"
!define PRODUCT_VERSION "0.7.0"
!define PRODUCT_PUBLISHER "Christine Project"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\${exe}"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; Best Compression
SetCompress Auto
SetCompressor /SOLID lzma
SetCompressorDictSize 32
SetDatablockOptimize On

;TODO: We need to make the dialogs use several languages

Function .onInit
; Check to see if already installed
  ReadRegStr $R0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString"
  IfFileExists $R0 +1 NotInstalled
  messagebox::show MB_DEFBUTTON4|MB_TOPMOST "${PRODUCT_NAME}" \
	"0,103" \
	"It seems that ${PRODUCT_NAME} is already installed." \
	"Uninstall" "Cancel"
	Pop $R1
  StrCmp $R1 2 Quit +1
  Exec $R0
Quit:
  Quit
NotInstalled:
FunctionEnd

Function .onUninstSuccess
; Refresh the System
  System::Call 'Shell32::SHChangeNotify(i ${SHCNE_ASSOCCHANGED}, i ${SHCNF_IDLIST}, i 0, i 0)'
FunctionEnd

Function .onInstSuccess
; Refresh the System
  System::Call 'Shell32::SHChangeNotify(i ${SHCNE_ASSOCCHANGED}, i ${SHCNF_IDLIST}, i 0, i 0)'
FunctionEnd


; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "win32resources/christine.ico"
!define MUI_UNICON "win32resources/christine_uninst.ico"
;!define MUI_WELCOMEFINISHPAGE_BITMAP "nsis.bmp" ; optional

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; Licence
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE COPYING
; Directory
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${install_file}"
InstallDir "${install_path}"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails hide
ShowUnInstDetails hide
;MessageBox MB_OK $DOCUMENTS

Section 
  SetShellVarContext all
  SetOverwrite ifnewer
  SetOutPath "$INSTDIR"
  File /r "${source_path}"
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\${link}" "$INSTDIR\${exe}"
  CreateShortCut "$DESKTOP\${link}" "$INSTDIR\${exe}"
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\Uninstall Christine.lnk" "$INSTDIR\uninst.exe"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\christine.lnk" "$INSTDIR\${exe}"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\${exe}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${exe}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  Exec "$INSTDIR\configuracion.exe"
SectionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "Christine will not play anymore here :-(."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  SetShellVarContext all
  Exec "$INSTDIR\${exe} -remove"
  RMDir /r "$SMPROGRAMS\${PRODUCT_NAME}"
  RMDir /r $INSTDIR
  Delete "$DESKTOP\${link}"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
