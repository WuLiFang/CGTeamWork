git push server
ROBOCOPY .venv\Lib\site-packages "$(git remote get-url server)\.venv\Lib\site-packages" /MIR /R:0
