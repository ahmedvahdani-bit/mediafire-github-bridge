@echo off
echo.
echo ZK
echo Block Host Cellebrite UFED 4PC
echo @ZK_GSM
echo Blocking Cellebrite Host ....
echo.
pause
SET NEWLINE=^& echo.

attrib -r %WINDIR%\system32\drivers\etc\hosts

FIND /C /I "www11.iconductcloud.com" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	www11.iconductcloud.com>>%WINDIR%\system32\drivers\etc\hosts

FIND /C /I "iconductcloud.com" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	iconductcloud.com>>%WINDIR%\system32\drivers\etc\hosts

FIND /C /I "cdn5.cellebrite.org" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	cdn5.cellebrite.org>>%WINDIR%\system32\drivers\etc\hosts

FIND /C /I "cdn6.cellebrite.org" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	cdn6.cellebrite.org>>%WINDIR%\system32\drivers\etc\hosts

FIND /C /I "www.cellebrite.org" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	www.cellebrite.org>>%WINDIR%\system32\drivers\etc\hosts

FIND /C /I "cellebrite.org" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	cellebrite.org>>%WINDIR%\system32\drivers\etc\hosts

FIND /C /I "herokuapp.com" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	herokuapp.com>>%WINDIR%\system32\drivers\etc\hosts

FIND /C /I "aur6mxbbq8jsu2o.herokuapp.com" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	aur6mxbbq8jsu2o.herokuapp.com>>%WINDIR%\system32\drivers\etc\hosts

FIND /C /I "test3.iconductcloud.com" %WINDIR%\system32\drivers\etc\hosts
IF %ERRORLEVEL% NEQ 0 ECHO %NEWLINE%^	127.0.0.1	test3.iconductcloud.com>>%WINDIR%\system32\drivers\etc\hosts


attrib +r %WINDIR%\system32\drivers\etc\hosts
echo Task Complete
pause