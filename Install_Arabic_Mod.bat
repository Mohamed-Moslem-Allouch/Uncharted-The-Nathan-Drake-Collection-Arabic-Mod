@echo off
title Uncharted Trilogy Arabic Mod Installer - Mohamed Moslem Allouch
color 0A
echo =====================================================================
echo   UNCHARTED: The Nathan Drake Collection - Arabic Mod
echo   تعريب ثلاثية أنشارتد الكاملة للكمبيوتر (PC Port)
echo   تعريب وبرمجة: محمد مسلم علوش (Mohamed Moslem Allouch)
echo =====================================================================
echo.
echo Installing Arabic files into the game directory...
if not exist "..\Game" (
    echo Error: Please place the 'Uncharted_Arabic_Mod' folder inside the main game directory!
    pause
    exit /b
)

xcopy /E /Y /I "Game" "..\Game"
echo.
echo =====================================================================
echo   SUCCESS: Arabic Mod installed successfully!
echo   تم تثبيت ملفات التعريب بنجاح!
echo.
echo   طريقة التفعيل داخل اللعبة:
echo   1. شغل اللعبة.
echo   2. من القائمة الرئيسية، ادخل إلى Options (الخيارات) -> Language (اللغة).
echo   3. اضبط Text (النص) على: العربية.
echo   4. اضبط Subtitles (الترجمة) على: تشغيل.
echo   5. اترك Speech (الحوار) على: English للاستمتاع بالأصوات الإنجليزية الأصلية.
echo =====================================================================
echo.
pause
