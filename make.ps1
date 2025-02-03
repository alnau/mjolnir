
& .\.venv\Scripts\Activate.ps1


pyinstaller --noconfirm --distpath D:\Photonics\mjolnir37_test code\mjolnir.py


$sourcePath = "D:\Photonics\mjolnir37_test\mjolnir"
$zipPath = "D:\Photonics\mjolnir37.zip"

if (Test-Path $sourcePath) {

    Compress-Archive -Path $sourcePath -DestinationPath $zipPath -Force
    Write-Host "Archivation successfull. ZIP file saved in: $zipPath"
} else {
    Write-Host "Error: Directory mjolnir hadnt been found in path"
}