; WARNING: This script has been created by py2exe. Changes to this script
; will be overwritten the next time py2exe is run!
[Setup]
AppName=pytray
AppVerName=pytray 1.0
DefaultDirName={pf}\pytray
DefaultGroupName=pytray

[Files]
Source: "pyTray.exe"; DestDir: "{app}\"; Flags: ignoreversion
Source: "lib\_elementtree.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_hashlib.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_socket.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_ssl.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\bz2.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\pyexpat.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\unicodedata.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_imaging.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_imaging.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\twain.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_controls_.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_core_.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_gdi_.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_grid.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_misc_.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_stc.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_windows_.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\_rl_accel.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\pyHnj.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\sgmlop.pyd"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "MSVCR71.dll"; DestDir: "{app}\"; Flags: ignoreversion
Source: "lib\wxmsw28uh_core_vc.dll"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "w9xpopen.exe"; DestDir: "{app}\"; Flags: ignoreversion
Source: "python25.dll"; DestDir: "{app}\"; Flags: ignoreversion
Source: "lib\wxmsw28uh_adv_vc.dll"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\python24.dll"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "MSVCR71.dll"; DestDir: "{app}\"; Flags: ignoreversion
Source: "lib\wxbase28uh_vc.dll"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\wxmsw28uh_html_vc.dll"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\wxmsw28uh_stc_vc.dll"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\wxbase28uh_net_vc.dll"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "lib\shardlib"; DestDir: "{app}\lib"; Flags: ignoreversion
Source: "files\user.pytray"; DestDir: "{app}\files"; Flags: ignoreversion
Source: "files\test\CrystalScreenConverted.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\CrystalScreenSimplexConverted.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\CrystalScreenStocksConverted.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\hampton_crystal_screen.csv"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\hampton_crystal_screen2_25-48.csv"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\jtest.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\newScreen.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\newScreenTempl.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\simplex_screen.csv"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\simplex_stocks.csv"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\StockSolutions.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\test.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\test.jpg"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\test.pdf"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\test_analysis.cvs"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\test_obs.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\test_out.exp"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\test_simplex_drop0.txt"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\test\testresults.txt"; DestDir: "{app}\files\test"; Flags: ignoreversion
Source: "files\Dtd\definition.xml"; DestDir: "{app}\files\Dtd"; Flags: ignoreversion
Source: "files\fonts\helvB08.pil"; DestDir: "{app}\files\fonts"; Flags: ignoreversion
Source: "files\fonts\helvB08.png"; DestDir: "{app}\files\fonts"; Flags: ignoreversion
Source: "files\fonts\helvetica-10.pil"; DestDir: "{app}\files\fonts"; Flags: ignoreversion
Source: "files\fonts\helvetica-10.png"; DestDir: "{app}\files\fonts"; Flags: ignoreversion
Source: "files\images\icon.ico"; DestDir: "{app}\files\images"; Flags: ignoreversion
Source: "files\images\title.jpg"; DestDir: "{app}\files\images"; Flags: ignoreversion
Source: "files\images\title1.jpg"; DestDir: "{app}\files\images"; Flags: ignoreversion
Source: "files\images\title1.psd"; DestDir: "{app}\files\images"; Flags: ignoreversion
Source: "files\images\title2.jpg"; DestDir: "{app}\files\images"; Flags: ignoreversion
Source: "files\images\title2.psd"; DestDir: "{app}\files\images"; Flags: ignoreversion

[Icons]
Name: "{group}\pytray"; Filename: "{app}\pyTray.exe"
Name: "{group}\Uninstall pytray"; Filename: "{uninstallexe}"
