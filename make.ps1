.# Запуск скрипта активации виртуального окружения
& .\.venv\Scripts\Activate.ps1

# Запуск команды PyInstaller для создания дистрибутива
pyinstaller --noconfirm --distpath D:\Photonics\mjolnir37_test code\mjolnir.py

# Проверка, существует ли созданная папка mjolnir
$sourcePath = "D:\Photonics\mjolnir37_test\mjolnir"
$zipPath = "D:\Photonics\mjolnir37.zip"

if (Test-Path $sourcePath) {
    # Создание zip архива
    Compress-Archive -Path $sourcePath -DestinationPath $zipPath -Force
    Write-Host "Упаковка завершена. Архив сохранен по пути: $zipPath"
} else {
    Write-Host "Ошибка: Папка mjolnir не найдена по пути: $sourcePath"
}